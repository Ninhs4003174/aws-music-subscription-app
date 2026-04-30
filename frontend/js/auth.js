function getCurrentUser() {
  const email = localStorage.getItem("musicUserEmail");
  const username = localStorage.getItem("musicUsername");

  if (!email) return null;

  return {
    email,
    username: username || email
  };
}

function logout() {
  localStorage.removeItem("musicUserEmail");
  localStorage.removeItem("musicUsername");
  window.location.href = "login.html";
}
