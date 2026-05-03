const loginForm = document.querySelector("#login-form");
const loginMessage = document.querySelector("#login-message");

function showLoginMessage(message, type = "info") {
  if (!loginMessage) return;

  loginMessage.textContent = message;
  loginMessage.className = `message ${type}`;
  loginMessage.hidden = !message;
}

function usernameFromEmail(email) {
  return email.includes("@") ? email.split("@")[0] : email;
}

function completeLogin(email, username) {
  const storedUsername = username || usernameFromEmail(email);

  localStorage.setItem("musicUserEmail", email);
  localStorage.setItem("musicUsername", storedUsername);
  window.location.href = "main.html";
}

async function backendLogin(email, password) {
  return apiRequest("/login", {
    method: "POST",
    body: JSON.stringify({ email, password })
  });
}

if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(loginForm);
    const email = String(formData.get("email") || "").trim();
    const password = String(formData.get("password") || "").trim();

    if (!email || !password) {
      showLoginMessage("Enter both email and password.", "error");
      return;
    }

    showLoginMessage("Signing in...", "info");

    try {
      const data = await backendLogin(email, password);
      completeLogin(email, data.username);
    } catch (error) {
      showLoginMessage(`Login failed: ${error.message}`, "error");
    }
  });
}
