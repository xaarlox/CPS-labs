document.addEventListener("DOMContentLoaded", function () {
  document.addEventListener("click", function (e) {
    if (e.target.classList.contains("alert__close")) {
      const alert = e.target.closest(".alert");
      if (alert) {
        alert.remove();
      }
    }
  });

  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({ behavior: "smooth" });
      }
    });
  });

  const wrapper = document.querySelector(".user-menu-wrapper");
  if (wrapper) {
    const dropdown = wrapper.querySelector(".user-dropdown");
    let closeTimer = null;
    const CLOSE_DELAY = 200;

    function openMenu() {
      clearTimeout(closeTimer);
      wrapper.classList.add("open");
    }

    function scheduleClose() {
      clearTimeout(closeTimer);
      closeTimer = setTimeout(() => {
        wrapper.classList.remove("open");
      }, CLOSE_DELAY);
    }

    wrapper.addEventListener("mouseenter", openMenu);
    wrapper.addEventListener("mouseleave", scheduleClose);

    if (dropdown) {
      dropdown.addEventListener("mouseenter", openMenu);
      dropdown.addEventListener("mouseleave", scheduleClose);
    }
  }

  const navLinks = document.querySelectorAll(".nav-list a");
  const profileContent = document.getElementById("profile-content");
  const accountContent = document.getElementById("account-content");
  const teacherContent = document.getElementById("teacher-content");

  function showSection(targetSection) {
    if (profileContent)
      profileContent.style.display =
        targetSection === "profile" ? "block" : "none";
    if (accountContent)
      accountContent.style.display =
        targetSection === "account" ? "block" : "none";
    if (teacherContent)
      teacherContent.style.display =
        targetSection === "account" ? "block" : "none";
  }

  navLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      navLinks.forEach((nav) => nav.classList.remove("active"));
      this.classList.add("active");
      const target = this.getAttribute("data-section");
      showSection(target);
    });
  });

  showSection("profile");

  const avatarInput = document.getElementById("avatar-upload-input");
  const avatarForm = document.getElementById("avatar-form");

  if (avatarInput && avatarForm) {
    avatarInput.addEventListener("change", function () {
      if (this.files && this.files[0]) {
        // Показати превью (опціонально)
        const reader = new FileReader();
        reader.onload = function (e) {
          const avatarImg = document.querySelector(
            ".user-avatar-display .avatar-img"
          );
          if (avatarImg) {
            avatarImg.src = e.target.result;
          }
        };
        reader.readAsDataURL(this.files[0]);

        // Автоматично відправити форму
        avatarForm.submit();
      }
    });
  }
});
