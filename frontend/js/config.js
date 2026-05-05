// Use the EC2 backend URL (no path suffix) so frontend requests go to the API.
const API_BASE_URL = "http://ec2-3-91-56-14.compute-1.amazonaws.com:8000";

async function apiRequest(path, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      },
      ...options
    });
  } catch {
    throw new Error("Backend is offline or unreachable.");
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = data.detail || data.message || "Request failed";
    throw new Error(message);
  }

  return data;
}
