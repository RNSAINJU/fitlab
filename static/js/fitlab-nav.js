(function () {
  function closeSidebar(shell) {
    if (!shell) return;
    shell.classList.remove("is-mobile-sidebar-open");
    document.body.classList.remove("is-mobile-sidebar-open");
  }

  function openSidebar(shell) {
    if (!shell) return;
    shell.classList.add("is-mobile-sidebar-open");
    document.body.classList.add("is-mobile-sidebar-open");
  }

  function toggleSidebar(shell) {
    if (!shell) return;
    if (shell.classList.contains("is-mobile-sidebar-open")) {
      closeSidebar(shell);
    } else {
      openSidebar(shell);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-sidebar-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        toggleSidebar(btn.closest("[data-mobile-sidebar]"));
      });
    });

    document.querySelectorAll("[data-sidebar-close]").forEach(function (el) {
      el.addEventListener("click", function () {
        closeSidebar(el.closest("[data-mobile-sidebar]"));
      });
    });

    document.querySelectorAll("[data-mobile-sidebar] .admin-sidebar a, [data-mobile-sidebar] .app-sidebar a").forEach(function (link) {
      link.addEventListener("click", function () {
        closeSidebar(link.closest("[data-mobile-sidebar]"));
      });
    });

    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      document.querySelectorAll("[data-mobile-sidebar].is-mobile-sidebar-open").forEach(closeSidebar);
    });
  });
})();
