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
  console.log("Password toggle v2 initializing...");

  const checkboxes = document.querySelectorAll(".show-password-toggle");

  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      const showPassword = this.checked;
      console.log(`Show password: ${showPassword}`);

      // ALWAYS search by ID and name, never by current type
      const passwordFieldIds = [
        "password",
        "confirm_password",
        "exampleInputPassword1",
      ];
      const passwordFieldNames = ["password", "confirm_password"];

      let fieldsToToggle = [];

      // Get by ID
      passwordFieldIds.forEach((id) => {
        const field = document.getElementById(id);
        if (field) fieldsToToggle.push(field);
      });

      // Get by name
      passwordFieldNames.forEach((name) => {
        document.querySelectorAll(`[name="${name}"]`).forEach((field) => {
          if (!fieldsToToggle.includes(field)) fieldsToToggle.push(field);
        });
      });

      console.log(`Found ${fieldsToToggle.length} field(s) to toggle`);

      // Toggle all found fields
      fieldsToToggle.forEach((field) => {
        const newType = showPassword ? "text" : "password";
        console.log(
          `Changing ${field.id || field.name} from ${field.type} to ${newType}`
        );
        field.type = newType;
      });
    });
  });
});
