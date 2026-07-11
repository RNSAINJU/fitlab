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

  function initHero3dCarousel(containerId) {
    var carousel = document.getElementById(containerId);
    var viewport = document.getElementById("trainerCarouselViewport");
    var stage = document.getElementById("trainer3dStage");
    var dotsWrap = document.getElementById("trainerCarouselDots");
    var prevBtn = document.getElementById("trainerCarouselPrev");
    var nextBtn = document.getElementById("trainerCarouselNext");
    if (!carousel || !viewport || !stage) return;

    var slides = Array.prototype.slice.call(stage.querySelectorAll("[data-hero-slide]"));
    if (!slides.length) return;

    var activeIndex = 0;
    var touchStartX = 0;
    var touchStartY = 0;
    var autoTimer = null;
    var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function slideSpacing() {
      if (window.innerWidth >= 768) return 155;
      if (window.innerWidth <= 480) return 108;
      return 128;
    }

    function buildDots() {
      if (!dotsWrap || slides.length <= 1) return;
      dotsWrap.innerHTML = "";
      slides.forEach(function (_, index) {
        var dot = document.createElement("button");
        dot.type = "button";
        dot.className = "hero-3d-dot" + (index === activeIndex ? " is-active" : "");
        dot.setAttribute("role", "tab");
        dot.setAttribute("aria-label", "Show trainer " + (index + 1));
        dot.setAttribute("aria-selected", index === activeIndex ? "true" : "false");
        dot.addEventListener("click", function () {
          goTo(index);
          restartAuto();
        });
        dotsWrap.appendChild(dot);
      });
    }

    function updateDots() {
      if (!dotsWrap) return;
      dotsWrap.querySelectorAll(".hero-3d-dot").forEach(function (dot, index) {
        var isActive = index === activeIndex;
        dot.classList.toggle("is-active", isActive);
        dot.setAttribute("aria-selected", isActive ? "true" : "false");
      });
    }

    function layoutSlides() {
      var spacing = slideSpacing();
      var time = Date.now() * 0.001;

      slides.forEach(function (slide, index) {
        var offset = index - activeIndex;
        var total = slides.length;
        if (offset > total / 2) offset -= total;
        if (offset < -total / 2) offset += total;

        var abs = Math.abs(offset);
        var hidden = abs > 2;
        var floatY = reducedMotion ? 0 : Math.sin(time * 1.2 + index) * (offset === 0 ? 8 : 4);
        var translateX = offset * spacing;
        var translateZ = offset === 0 ? 72 : Math.max(0, 48 - abs * 22);
        var rotateY = offset * -38;
        var rotateX = offset === 0 ? (reducedMotion ? 0 : Math.sin(time * 0.5) * 4) : 8;
        var scale = offset === 0 ? 1 : Math.max(0.72, 0.9 - abs * 0.12);
        var opacity = hidden ? 0 : Math.max(0.25, 1 - abs * 0.32);

        slide.style.opacity = String(opacity);
        slide.style.pointerEvents = abs <= 1 ? "auto" : "none";
        slide.style.zIndex = String(100 - abs);
        slide.style.transform =
          "translate3d(calc(-50% + " + translateX + "px), calc(-50% + " + floatY + "px), " + translateZ + "px) " +
          "rotateX(" + rotateX + "deg) rotateY(" + rotateY + "deg) scale(" + scale + ")";

        slide.setAttribute("aria-hidden", offset === 0 ? "false" : "true");
        if (offset === 0) {
          slide.setAttribute("aria-current", "true");
        } else {
          slide.removeAttribute("aria-current");
        }
      });

      updateDots();
      requestAnimationFrame(layoutSlides);
    }

    function goTo(index) {
      var total = slides.length;
      activeIndex = ((index % total) + total) % total;
    }

    function next() { goTo(activeIndex + 1); }
    function prev() { goTo(activeIndex - 1); }

    function restartAuto() {
      if (autoTimer) clearInterval(autoTimer);
      if (slides.length <= 1 || reducedMotion) return;
      autoTimer = setInterval(next, 4500);
    }

    slides.forEach(function (slide, index) {
      slide.addEventListener("click", function () {
        if (index !== activeIndex) {
          goTo(index);
          restartAuto();
        }
      });
    });

    if (prevBtn) {
      prevBtn.addEventListener("click", function () {
        prev();
        restartAuto();
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener("click", function () {
        next();
        restartAuto();
      });
    }

    if (slides.length <= 1) {
      if (prevBtn) prevBtn.style.display = "none";
      if (nextBtn) nextBtn.style.display = "none";
      var hint = carousel.querySelector(".hero-3d-swipe-hint");
      if (hint) hint.style.display = "none";
    }

    viewport.addEventListener("touchstart", function (event) {
      if (!event.touches || !event.touches.length) return;
      touchStartX = event.touches[0].clientX;
      touchStartY = event.touches[0].clientY;
    }, { passive: true });

    viewport.addEventListener("touchend", function (event) {
      var touch = event.changedTouches[0];
      if (!touch) return;
      var deltaX = touch.clientX - touchStartX;
      var deltaY = touch.clientY - touchStartY;
      if (Math.abs(deltaX) < 40 || Math.abs(deltaX) < Math.abs(deltaY)) return;
      if (deltaX < 0) next();
      else prev();
      restartAuto();
    }, { passive: true });

    buildDots();
    layoutSlides();
    restartAuto();
  }

  initHero3dCarousel("trainer-slider");
})();
