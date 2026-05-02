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
    const username =
      String(formData.get("username") || "").trim() ||
      String(formData.get("user_name") || "").trim();
    const password = String(formData.get("password") || "").trim();
    const submitButton = registerForm.querySelector("button[type='submit']");

    if (!email || !username || !password) {
      showRegisterMessage("Enter email, username, and password.", "error");
      return;
    }

    showRegisterMessage("Creating account...", "info");
    submitButton.disabled = true;

    try {
      const data = await apiRequest("/register", {
        method: "POST",
        body: JSON.stringify({
          email: email,
          username: username,
          password: password
        })
      });

      if (data.success === false) {
        showRegisterMessage(data.message || "The email already exists", "error");
        return;
      }

      showRegisterMessage("Registration successful. Redirecting to login...", "success");

      setTimeout(() => {
        window.location.href = "login.html";
      }, 700);
    } catch (error) {
      showRegisterMessage(error.message || "Unable to register.", "error");
    } finally {
      submitButton.disabled = false;
    }
  });
}
