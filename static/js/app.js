if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker
      .register("static/js/serviceWorker.js")
      .then((res) => console.log("service worker registered"))
      .catch((err) => console.log("service worker not registered", err));
  });
}

// This script toggles the active class and aria-current attribute on the nav links
document.addEventListener("DOMContentLoaded", function () {
  const navLinks = document.querySelectorAll(".nav-link");
  const currentUrl = window.location.pathname;

  navLinks.forEach((link) => {
    const linkUrl = link.getAttribute("href");
    if (linkUrl === currentUrl) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    } else {
      link.classList.remove("active");
      link.removeAttribute("aria-current");
    }
  });
});

// Used Co-Pilot to generate functionality for Show Password checkbox
document.addEventListener("DOMContentLoaded", function () {
  const showPasswordCheckbox = document.getElementById("show_password");
  const passwordField = document.getElementById("password");
  const confirmPasswordField = document.getElementById("confirm_password");

  if (showPasswordCheckbox && passwordField && confirmPasswordField) {
    showPasswordCheckbox.addEventListener("change", function () {
      const type = this.checked ? "text" : "password";
      passwordField.type = type;
      confirmPasswordField.type = type;
    });
  }
});
