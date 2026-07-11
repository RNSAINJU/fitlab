(function () {
  var STORAGE_KEY = "fitlab-theme";
  var COOKIE_NAME = "fitlab_theme";
  var VALID = { dark: true, light: true };

  function getCsrfToken() {
    var match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  function readStoredTheme() {
    try {
      var stored = localStorage.getItem(STORAGE_KEY);
      if (stored && VALID[stored]) return stored;
    } catch (e) {}
    return null;
  }

  function writeCookie(theme) {
    document.cookie =
      COOKIE_NAME + "=" + theme + ";path=/;max-age=31536000;SameSite=Lax";
  }

  function persistTheme(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {}
    writeCookie(theme);
  }

  function readForcedTheme() {
    var meta = document.querySelector('meta[name="fitlab-forced-theme"]');
    var forced = meta && meta.getAttribute("content");
    return forced && VALID[forced] ? forced : null;
  }

  function applyTheme(theme) {
    if (!VALID[theme]) theme = "dark";
    document.documentElement.setAttribute("data-theme", theme);
    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      var isLight = theme === "light";
      btn.setAttribute("aria-pressed", isLight ? "true" : "false");
      btn.setAttribute("aria-label", isLight ? "Switch to dark mode" : "Switch to light mode");
      btn.classList.toggle("is-light", isLight);
    });
  }

  function saveToServer(theme) {
    var body = document.body;
    if (!body || body.getAttribute("data-authenticated") !== "true") return;
    fetch("/accounts/theme/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      credentials: "same-origin",
      body: JSON.stringify({ theme: theme }),
    }).catch(function () {});
  }

  function setTheme(theme, options) {
    options = options || {};
    applyTheme(theme);
    persistTheme(theme);
    if (options.syncServer !== false) {
      saveToServer(theme);
    }
  }

  function toggleTheme() {
    var current = document.documentElement.getAttribute("data-theme") || "light";
    setTheme(current === "light" ? "dark" : "light");
  }

  window.FitlabTheme = {
    apply: applyTheme,
    set: setTheme,
    toggle: toggleTheme,
    readStored: readStoredTheme,
  };

  document.addEventListener("DOMContentLoaded", function () {
    var forced = readForcedTheme();
    if (forced) {
      setTheme(forced, { syncServer: false });
      return;
    }

    var initial =
      document.documentElement.getAttribute("data-theme") ||
      readStoredTheme() ||
      "dark";
    applyTheme(initial);
    persistTheme(initial);

    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.addEventListener("click", toggleTheme);
    });
  });
})();
