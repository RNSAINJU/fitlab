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

  function scrollGroupIntoSidebar(group) {
    var sidebar = group && group.closest(".admin-sidebar, .app-sidebar");
    if (!sidebar || !group) return;
    window.requestAnimationFrame(function () {
      var groupBottom = group.offsetTop + group.offsetHeight;
      var visibleBottom = sidebar.scrollTop + sidebar.clientHeight;
      if (groupBottom > visibleBottom) {
        sidebar.scrollTop = groupBottom - sidebar.clientHeight + 8;
      } else if (group.offsetTop < sidebar.scrollTop) {
        sidebar.scrollTop = Math.max(0, group.offsetTop - 8);
      }
    });
  }

  function setSettingsGroupOpen(group, open) {
    if (!group) return;
    var toggle = group.querySelector("[data-sidebar-group-toggle]");
    var subnav = group.querySelector(".admin-sidebar__subnav");
    group.classList.toggle("is-open", open);
    if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (subnav) subnav.removeAttribute("hidden");
    if (open) scrollGroupIntoSidebar(group);
  }

  function initSidebarNav() {
    document.querySelectorAll("[data-sidebar-group-toggle]").forEach(function (toggle) {
      if (toggle.dataset.sidebarBound === "true") return;
      toggle.dataset.sidebarBound = "true";
      toggle.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        var group = toggle.closest("[data-sidebar-group]");
        if (!group) return;
        var open = !group.classList.contains("is-open");
        document.querySelectorAll("[data-sidebar-group].is-open").forEach(function (other) {
          if (other !== group) setSettingsGroupOpen(other, false);
        });
        setSettingsGroupOpen(group, open);
      });
    });

    document.querySelectorAll("[data-sidebar-toggle]").forEach(function (btn) {
      if (btn.dataset.sidebarBound === "true") return;
      btn.dataset.sidebarBound = "true";
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        toggleSidebar(btn.closest("[data-mobile-sidebar]"));
      });
    });

    document.querySelectorAll("[data-sidebar-close]").forEach(function (el) {
      if (el.dataset.sidebarBound === "true") return;
      el.dataset.sidebarBound = "true";
      el.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        closeSidebar(el.closest("[data-mobile-sidebar]"));
      });
    });

    document
      .querySelectorAll(
        "[data-mobile-sidebar] .admin-sidebar a, [data-mobile-sidebar] .app-sidebar a"
      )
      .forEach(function (link) {
        if (link.dataset.sidebarBound === "true") return;
        link.dataset.sidebarBound = "true";
        link.addEventListener("click", function () {
          closeSidebar(link.closest("[data-mobile-sidebar]"));
        });
      });

    document.querySelectorAll("[data-sidebar-group].is-open").forEach(scrollGroupIntoSidebar);
  }

  function init() {
    initSidebarNav();

    if (window.__fitlabSidebarEscapeBound) return;
    window.__fitlabSidebarEscapeBound = true;
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      document.querySelectorAll("[data-mobile-sidebar].is-mobile-sidebar-open").forEach(closeSidebar);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
