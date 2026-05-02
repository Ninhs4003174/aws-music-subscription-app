function getCurrentUser() {
  const email = localStorage.getItem("musicUserEmail");
  const userName = localStorage.getItem("musicUserName");

  if (!email) {
    return null;
  }

  return {
    email: email,
    user_name: userName || email
  };
}

function saveCurrentUser(user) {
  const email = user.email;
  const userName = user.user_name || user.username || user.name || email;

  localStorage.setItem("musicUserEmail", email);
  localStorage.setItem("musicUserName", userName);
}

function logout() {
  localStorage.removeItem("musicUserEmail");
  localStorage.removeItem("musicUserName");
  window.location.href = "login.html";
}