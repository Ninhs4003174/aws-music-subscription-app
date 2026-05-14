#!/bin/bash
# EC2 Deployment Script
# This script deploys the backend to an EC2 instance

set -e

AWS_REGION="us-east-1"
INSTANCE_NAME="music-subscription-backend"
INSTANCE_TYPE="t3.micro"
KEY_PAIR_NAME="music-app-key"
SECURITY_GROUP_NAME="music-app-backend"

echo "=== AWS Music Subscription App - EC2 Deployment ==="
echo "AWS Region: $AWS_REGION"
echo "Instance Type: $INSTANCE_TYPE"
echo ""

echo "Step 0: Preparing self-contained backend bootstrap..."

# Step 1: Create security group
echo "Step 1: Creating security group..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
  --group-name $SECURITY_GROUP_NAME \
  --description "Security group for Music Subscription App backend" \
  --region $AWS_REGION \
  --query 'GroupId' \
  --output text \
  2>/dev/null || echo "sg-0a37205a20571c737")

if [ "$SECURITY_GROUP_ID" = "sg-0a37205a20571c737" ]; then
  echo "Using existing security group: $SECURITY_GROUP_ID"
else
  # Allow HTTP, HTTPS, SSH
  aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp --port 80 --cidr 0.0.0.0/0 \
    --region $AWS_REGION
  
  aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp --port 443 --cidr 0.0.0.0/0 \
    --region $AWS_REGION
  
  aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp --port 22 --cidr 0.0.0.0/0 \
    --region $AWS_REGION
  
  aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp --port 8000 --cidr 0.0.0.0/0 \
    --region $AWS_REGION
  
  echo "Security group created: $SECURITY_GROUP_ID"
fi

# Step 2: Create or use existing key pair
echo "Step 2: Setting up key pair..."
echo "Using key pair: $KEY_PAIR_NAME"

# Step 3: Create user data script for EC2 initialization
echo "Step 3: Writing backend app into user data..."
cat > /tmp/ec2_userdata.sh << 'USERDATA'
#!/bin/bash
set -eux

apt-get update
apt-get install -y python3 python3-pip

mkdir -p /home/ubuntu/app
cat > /home/ubuntu/app/main.py <<'PY'
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATA_DIR = Path("/home/ubuntu/app/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGIN_FILE = DATA_DIR / "login.json"
SONGS_FILE = DATA_DIR / "songs.json"
SUBS_FILE = DATA_DIR / "subscriptions.json"

class RegisterRequest(BaseModel):
  email: str
  username: str
  password: str

class LoginRequest(BaseModel):
  email: str
  password: str

SAMPLES = [
  {"artist": "Taylor Swift", "title": "Anti-Hero", "year": "2022", "album": "Midnights", "song_id": "Taylor Swift#Anti-Hero", "image_url": ""},
  {"artist": "Adele", "title": "Hello", "year": "2015", "album": "25", "song_id": "Adele#Hello", "image_url": ""},
  {"artist": "Ed Sheeran", "title": "Shape of You", "year": "2017", "album": "Divide", "song_id": "Ed Sheeran#Shape of You", "image_url": ""},
  {"artist": "Coldplay", "title": "Yellow", "year": "2000", "album": "Parachutes", "song_id": "Coldplay#Yellow", "image_url": ""},
  {"artist": "BTS", "title": "Dynamite", "year": "2020", "album": "Be", "song_id": "BTS#Dynamite", "image_url": ""},
]

def read_json(path: Path, default):
  if path.exists():
    return json.loads(path.read_text())
  return default

def write_json(path: Path, value):
  path.write_text(json.dumps(value, indent=2))

def bootstrap():
  if not LOGIN_FILE.exists():
    write_json(LOGIN_FILE, {"s1234560@student.rmit.edu.au": {"email": "s1234560@student.rmit.edu.au", "username": "student", "password": "012345"}})
  if not SONGS_FILE.exists():
    write_json(SONGS_FILE, SAMPLES)
  if not SUBS_FILE.exists():
    write_json(SUBS_FILE, {})

def load_logins():
  return read_json(LOGIN_FILE, {})

def save_logins(data):
  write_json(LOGIN_FILE, data)

def load_songs():
  return read_json(SONGS_FILE, SAMPLES)

def load_subs():
  return read_json(SUBS_FILE, {})

def save_subs(data):
  write_json(SUBS_FILE, data)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def init():
  bootstrap()

@app.get("/health")
def health():
  return {"status": "ok"}

@app.post("/register")
def register(req: RegisterRequest):
  logins = load_logins()
  if req.email in logins:
    raise HTTPException(400, "The email already exists")
  logins[req.email] = {"email": req.email, "username": req.username, "password": req.password}
  save_logins(logins)
  return {"message": "registered"}

@app.post("/login")
def login_user(req: LoginRequest):
  item = load_logins().get(req.email)
  if not item or item.get("password") != req.password:
    raise HTTPException(400, "email or password is invalid")
  return {"email": req.email, "username": item.get("username") or req.email}

def match(song, artist: Optional[str] = None, year: Optional[str] = None, album: Optional[str] = None, title: Optional[str] = None):
  def starts(value, term):
    return True if not term else str(value or "").lower().startswith(str(term).lower())
  return starts(song.get("artist"), artist) and starts(song.get("title"), title) and starts(song.get("album"), album) and (not year or str(song.get("year", "")) == str(year))

@app.get("/music/query")
def query_music(artist: str = None, year: str = None, album: str = None, title: str = None, limit: int = 50, last_evaluated_key: str = None):
  if not any([artist, year, album, title]):
    return []
  items = load_songs()
  return [song for song in items if match(song, artist, year, album, title)][:limit]

def upsert_subscription(email, song_id, title, artist, album, image_url):
  subs = load_subs()
  subs.setdefault(email, {})[song_id] = {"user_email": email, "song_id": song_id, "title": title, "artist": artist, "album": album, "image_url": image_url}
  save_subs(subs)

@app.post("/subscriptions")
def subscribe(payload: dict):
  email = payload.get("email") or payload.get("user_email")
  song_id = payload.get("song_id")
  if not email or not song_id:
    raise HTTPException(400, "email and song_id are required")
  upsert_subscription(email, song_id, str(payload.get("title") or ""), str(payload.get("artist") or ""), str(payload.get("album") or ""), str(payload.get("image_url") or payload.get("s3_image_url") or ""))
  return {"message": "subscribed"}

@app.get("/subscriptions")
def list_subscriptions(email: str):
  return list(load_subs().get(email, {}).values())

@app.delete("/subscriptions/{song_id}")
def unsubscribe(song_id: str, email: str):
  subs = load_subs()
  subs.get(email, {}).pop(song_id, None)
  save_subs(subs)
  return {"message": "removed", "song_id": song_id}
PY

python3 -m pip install --no-cache-dir fastapi uvicorn pydantic
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 >/var/log/app.log 2>&1 &

echo "Backend deployment complete"
USERDATA

# Step 4: Launch EC2 instance
echo "Step 4: Launching EC2 instance..."
AMI_ID="resolve:ssm:/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id"

INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type $INSTANCE_TYPE \
  --key-name $KEY_PAIR_NAME \
  --security-group-ids $SECURITY_GROUP_ID \
  --user-data file:///tmp/ec2_userdata.sh \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
  --region $AWS_REGION \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "EC2 Instance launched: $INSTANCE_ID"

# Step 5: Wait for instance and get details
echo "Step 5: Waiting for instance to start..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $AWS_REGION

# Get public IP
sleep 10  # Give the instance a few seconds to fully initialize
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --region $AWS_REGION \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo ""
echo "=== Deployment Complete ==="
echo "Instance ID: $INSTANCE_ID"
echo "Instance IP: $PUBLIC_IP"
echo "Instance Name: $INSTANCE_NAME"
echo ""
echo "To SSH into the instance:"
echo "  ssh -i ~/.ssh/$KEY_PAIR_NAME.pem ubuntu@$PUBLIC_IP"
echo ""
echo "Backend URL:"
echo "  http://$PUBLIC_IP:8000"
echo ""
echo "Note: The instance may still be initializing. Wait 2-3 minutes for Docker setup."
echo "Check instance status with:"
echo "  aws ec2 describe-instance-status --instance-ids $INSTANCE_ID --region $AWS_REGION"
