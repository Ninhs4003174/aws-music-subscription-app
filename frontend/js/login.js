const loginForm = document.querySelector("#login-form");
const loginMessage = document.querySelector("#login-message");

function showLoginMessage(message, type = "info") {
  if (!loginMessage) return;

  loginMessage.textContent = message;
  loginMessage.className = `message ${type}`;
  loginMessage.hidden = !message;
}

function normaliseLoginResponse(data, email) {
  if (data.user) {
    return {
      email: data.user.email || email,
      user_name: data.user.user_name || data.user.username || data.user.name || email
    };
  }

  return {
    email: data.email || email,
    user_name: data.user_name || data.username || data.name || email
  };
}

if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(loginForm);
    const email = String(formData.get("email") || "").trim();
    const password = String(formData.get("password") || "").trim();
    const submitButton = loginForm.querySelector("button[type='submit']");

    if (!email || !password) {
      showLoginMessage("Enter both email and password.", "error");
      return;
    }

    showLoginMessage("Signing in...", "info");
    submitButton.disabled = true;

    try {
      const data = await apiRequest("/login", {
        method: "POST",
        body: JSON.stringify({
          email: email,
          password: password
        })
      });

      if (data.success === false) {
        showLoginMessage(data.message || "email or password is invalid", "error");
        return;
      }

      const user = normaliseLoginResponse(data, email);
      saveCurrentUser(user);

      showLoginMessage("Login successful. Redirecting...", "success");

      setTimeout(() => {
        window.location.href = "main.html";
      }, 500);
    } catch (error) {
      showLoginMessage(error.message || "email or password is invalid", "error");
    } finally {
      submitButton.disabled = false;
    }
  });
}