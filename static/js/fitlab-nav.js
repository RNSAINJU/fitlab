(function () {
  function setExpanded(shell, open) {
    if (!shell) return;
    shell.querySelectorAll("[data-sidebar-toggle]").forEach(function (btn) {
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
  }

  function closeSidebar(shell) {
    if (!shell) return;
    shell.classList.remove("is-mobile-sidebar-open");
    document.body.classList.remove("is-mobile-sidebar-open");
    setExpanded(shell, false);
  }

  function openSidebar(shell) {
    if (!shell) return;
    shell.classList.add("is-mobile-sidebar-open");
    document.body.classList.add("is-mobile-sidebar-open");
    setExpanded(shell, true);
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
    document.querySelectorAll("[data-sidebar-group-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        var group = btn.closest("[data-sidebar-group]");
        if (!group) return;
        var open = !group.classList.contains("is-open");
        document.querySelectorAll("[data-sidebar-group].is-open").forEach(function (other) {
          if (other !== group) {
            other.classList.remove("is-open");
            var otherToggle = other.querySelector("[data-sidebar-group-toggle]");
            if (otherToggle) otherToggle.setAttribute("aria-expanded", "false");
          }
        });
        group.classList.toggle("is-open", open);
        btn.setAttribute("aria-expanded", open ? "true" : "false");
      });
    });

    document.querySelectorAll("[data-sidebar-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        toggleSidebar(btn.closest("[data-mobile-sidebar]"));
      });
    });

    document.querySelectorAll("[data-sidebar-close]").forEach(function (el) {
      el.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
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
