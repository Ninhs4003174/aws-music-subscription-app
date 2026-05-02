// Backend API URL.
// Local FastAPI backend usually runs on port 8000.
// Frontend may run on port 3000 through npx serve.

const API_BASE_URL = "http://localhost:8000";

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