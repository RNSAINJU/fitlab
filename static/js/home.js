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
    function activateAccordionItem(item) {
      accordion.querySelectorAll(".home-accordion__item").forEach(function (el) {
        el.classList.remove("is-active");
      });
      item.classList.add("is-active");
    }

    accordion.querySelectorAll(".home-accordion__item").forEach(function (item) {
      item.addEventListener("mouseenter", function () {
        activateAccordionItem(item);
      });
      item.addEventListener("click", function () {
        activateAccordionItem(item);
      });
      item.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          activateAccordionItem(item);
        }
      });
    });
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

  function initTrainerCarousel3D(containerId) {
    var container = document.getElementById(containerId);
    if (!container) return;

    var viewport = container.querySelector("[data-trainer-viewport]");
    var slides = Array.prototype.slice.call(
      container.querySelectorAll(".home-slider__card")
    );
    if (!slides.length) return;

    var dots = Array.prototype.slice.call(
      container.querySelectorAll(".home-slider__dot")
    );
    var prev = container.querySelector(".home-slider__arrow--prev");
    var next = container.querySelector(".home-slider__arrow--next");
    var index = slides.findIndex(function (slide) {
      return slide.classList.contains("is-active");
    });
    if (index < 0) index = 0;

    var touchStartX = 0;
    var touchStartY = 0;
    var touchDeltaX = 0;
    var touchActive = false;
    var swipeLocked = false;

    function mod(n, m) {
      return ((n % m) + m) % m;
    }

    function setActive(nextIndex) {
      index = mod(nextIndex, slides.length);
      slides.forEach(function (slide, i) {
        var offset = i - index;
        if (offset > slides.length / 2) offset -= slides.length;
        if (offset < -slides.length / 2) offset += slides.length;

        slide.classList.remove("is-active", "is-prev", "is-next", "is-far", "is-dragging");
        if (offset === 0) slide.classList.add("is-active");
        else if (offset === -1) slide.classList.add("is-prev");
        else if (offset === 1) slide.classList.add("is-next");
        else slide.classList.add("is-far");
      });

      dots.forEach(function (dot, i) {
        var isActive = i === index;
        dot.classList.toggle("is-active", isActive);
        dot.setAttribute("aria-selected", isActive ? "true" : "false");
      });
    }

    function goTo(nextIndex) {
      setActive(nextIndex);
    }

    slides.forEach(function (slide, i) {
      slide.addEventListener("click", function () {
        if (i !== index) goTo(i);
      });
    });

    dots.forEach(function (dot, i) {
      dot.addEventListener("click", function () {
        goTo(i);
      });
    });

    if (prev) {
      prev.addEventListener("click", function () {
        goTo(index - 1);
      });
    }

    if (next) {
      next.addEventListener("click", function () {
        goTo(index + 1);
      });
    }

    if (viewport) {
      viewport.addEventListener("touchstart", function (event) {
        if (!event.changedTouches || !event.changedTouches.length) return;
        var touch = event.changedTouches[0];
        touchStartX = touch.clientX;
        touchStartY = touch.clientY;
        touchDeltaX = 0;
        touchActive = true;
        swipeLocked = false;
        slides.forEach(function (slide) {
          slide.classList.add("is-dragging");
        });
      }, { passive: true });

      viewport.addEventListener("touchmove", function (event) {
        if (!touchActive || !event.changedTouches || !event.changedTouches.length) return;
        var touch = event.changedTouches[0];
        var deltaX = touch.clientX - touchStartX;
        var deltaY = touch.clientY - touchStartY;

        if (!swipeLocked) {
          if (Math.abs(deltaY) > Math.abs(deltaX) && Math.abs(deltaY) > 12) {
            touchActive = false;
            slides.forEach(function (slide) {
              slide.classList.remove("is-dragging");
            });
            return;
          }
          if (Math.abs(deltaX) > 12) {
            swipeLocked = true;
          }
        }

        if (!swipeLocked) return;
        touchDeltaX = deltaX;
        event.preventDefault();

        var activeSlide = slides[index];
        if (activeSlide) {
          activeSlide.style.transform =
            "translate3d(" + (touchDeltaX * 0.35) + "px, 0, 90px) rotateY(" +
            (touchDeltaX * -0.04) + "deg) scale(1)";
        }
      }, { passive: false });

      function endTouch() {
        if (!touchActive) return;
        touchActive = false;
        swipeLocked = false;

        slides.forEach(function (slide) {
          slide.classList.remove("is-dragging");
          slide.style.transform = "";
        });

        if (Math.abs(touchDeltaX) > 48) {
          if (touchDeltaX < 0) goTo(index + 1);
          else goTo(index - 1);
        }
        touchDeltaX = 0;
      }

      viewport.addEventListener("touchend", endTouch, { passive: true });
      viewport.addEventListener("touchcancel", endTouch, { passive: true });
    }

    setActive(index);
  }

  initTrainerCarousel3D("trainer-slider");
})();
