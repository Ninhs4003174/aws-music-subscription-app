const registerForm = document.querySelector("#register-form");
const registerMessage = document.querySelector("#register-message");

function showRegisterMessage(message, type = "info") {
  if (!registerMessage) return;

  registerMessage.textContent = message;
  registerMessage.className = `message ${type}`;
  registerMessage.hidden = !message;
}

if (registerForm) {
  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(registerForm);
    const email = String(formData.get("email") || "").trim();
    const username = String(formData.get("username") || "").trim();
    const password = String(formData.get("password") || "").trim();

    if (!email || !username || !password) {
      showRegisterMessage("Enter email, username, and password.", "error");
      return;
    }

    showRegisterMessage("Creating account...", "info");

    try {
      await apiRequest("/register", {
        method: "POST",
        body: JSON.stringify({ email, username, password })
      });

      window.location.href = "login.html";
    } catch (error) {
      const message = error.message === "The email already exists"
        ? "The email already exists"
        : `Unable to register: ${error.message}`;
      showRegisterMessage(message, "error");
    }
  });
}
