(function () {
  var header = document.getElementById("home-header");
  var toggle = document.getElementById("home-menu-toggle");
  var mobileNav = document.getElementById("home-mobile-nav");
  var backdrop = document.getElementById("home-mobile-backdrop");

  function setMenuOpen(open) {
    if (!mobileNav || !toggle) return;
    mobileNav.classList.toggle("is-open", open);
    toggle.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    document.body.classList.toggle("home-nav-open", open);
    if (backdrop) {
      backdrop.classList.toggle("is-open", open);
    }
  }

  function closeMenu() {
    setMenuOpen(false);
  }

  function scrollToSection(hash) {
    if (!hash || hash === "#") return;
    var target = document.querySelector(hash);
    if (!target) return;
    var headerH = header ? header.offsetHeight : 70;
    var top = target.getBoundingClientRect().top + window.pageYOffset - headerH - 12;
    window.scrollTo({ top: Math.max(0, top), behavior: "smooth" });
  }

  function handleNavClick(event) {
    var link = event.currentTarget;
    var href = link.getAttribute("href") || "";
    if (href.charAt(0) === "#" && href.length > 1) {
      event.preventDefault();
      closeMenu();
      scrollToSection(href);
      if (history.replaceState) {
        history.replaceState(null, "", href);
      } else {
        window.location.hash = href;
      }
    } else {
      closeMenu();
    }
  }

  if (toggle && mobileNav) {
    toggle.addEventListener("click", function () {
      setMenuOpen(!mobileNav.classList.contains("is-open"));
    });
    if (backdrop) {
      backdrop.addEventListener("click", closeMenu);
    }
    document.querySelectorAll(".home-mobile-nav a[href^='#'], .home-header__nav a[href^='#']").forEach(function (link) {
      link.addEventListener("click", handleNavClick);
    });
    mobileNav.querySelectorAll("a:not([href^='#'])").forEach(function (link) {
      link.addEventListener("click", closeMenu);
    });
    window.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeMenu();
    });
  }

  if (window.location.hash) {
    window.setTimeout(function () {
      scrollToSection(window.location.hash);
    }, 100);
  }

  window.addEventListener("scroll", function () {
    if (header) header.classList.toggle("is-scrolled", window.scrollY > 24);
  }, { passive: true });

  var accordion = document.getElementById("powerlifter-accordion");
  if (accordion) {
    accordion.querySelectorAll(".home-accordion__item").forEach(function (item) {
      item.addEventListener("mouseenter", function () {
        if (window.matchMedia("(min-width: 769px)").matches) {
          accordion.querySelectorAll(".home-accordion__item").forEach(function (el) {
            el.classList.remove("is-active");
          });
          item.classList.add("is-active");
        }
      });
      item.addEventListener("click", function () {
        accordion.querySelectorAll(".home-accordion__item").forEach(function (el) {
          el.classList.remove("is-active");
        });
        item.classList.add("is-active");
        if (window.matchMedia("(max-width: 768px)").matches) {
          item.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
        }
      });
    });

    if (window.matchMedia("(max-width: 768px)").matches) {
      accordion.addEventListener("scroll", function () {
        var items = accordion.querySelectorAll(".home-accordion__item");
        var center = accordion.scrollLeft + accordion.clientWidth / 2;
        var closest = null;
        var closestDist = Infinity;
        items.forEach(function (item) {
          var itemCenter = item.offsetLeft + item.offsetWidth / 2;
          var dist = Math.abs(center - itemCenter);
          if (dist < closestDist) {
            closestDist = dist;
            closest = item;
          }
        });
        if (closest) {
          items.forEach(function (el) { el.classList.remove("is-active"); });
          closest.classList.add("is-active");
        }
      }, { passive: true });
    }
  }

  function initSlider(containerId) {
    var container = document.getElementById(containerId);
    if (!container) return;
    var slides = container.querySelectorAll(".home-slider__slide, .home-client-card");
    if (!slides.length) return;
    var index = 0;
    var prev = container.querySelector(".home-slider__arrow--prev");
    var next = container.querySelector(".home-slider__arrow--next");
    function show(i) {
      index = (i + slides.length) % slides.length;
      slides.forEach(function (slide, n) {
        slide.classList.toggle("is-active", n === index);
      });
    }
    if (prev) prev.addEventListener("click", function () { show(index - 1); });
    if (next) next.addEventListener("click", function () { show(index + 1); });
  }

  ["trainer-slider", "gallery-slider", "clients-row-1", "clients-row-2"].forEach(initSlider);
})();
