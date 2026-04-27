const loginForm = document.getElementById("loginForm");
const loginMessage = document.getElementById("loginMessage");

if (loginForm) {
  loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const submitButton = loginForm.querySelector("button");

    loginMessage.textContent = "";
    loginMessage.className = "message";

    if (!email || !password) {
      showMessage("Please enter both email and password.", "error");
      return;
    }

    try {
      submitButton.disabled = true;
      submitButton.textContent = "Logging in...";

      const response = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          email: email,
          password: password
        })
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        showMessage(data.message || "email or password is invalid", "error");
        return;
      }

      localStorage.setItem("loggedInUser", JSON.stringify(data.user));

      showMessage("Login successful. Redirecting...", "success");

      setTimeout(function () {
        window.location.href = "main.html";
      }, 700);
    } catch (error) {
      showMessage("Unable to connect to the server. Please try again.", "error");
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Log In";
    }
  });
}

function showMessage(message, type) {
  loginMessage.textContent = message;
  loginMessage.className = `message ${type}`;
}