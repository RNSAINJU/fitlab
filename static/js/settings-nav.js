document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-settings-nav]").forEach((select) => {
    select.addEventListener("change", () => {
      const url = select.value;
      if (url) {
        window.location.assign(url);
      }
    });
  });
});
