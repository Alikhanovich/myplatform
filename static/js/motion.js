/* =====================================================================
   motion.js — DOM motion (Portfolio.dc.html DCLogic'dan React'siz qayta
   yozilgan). Three.js bilan ishlamaydi (u hero3d.js'da).

   Boshqaradi:
     - boot sequence      [data-boot] / [data-bootline] / [data-bootbar] / [data-bootpct]
     - hero reveal        [data-hero]  (stagger)
     - scroll reveal      [data-reveal] (GSAP ScrollTrigger bo'lsa, aks holda IO)
     - skill bar fill     [data-bar]   (ko'ringanda width -> level%)
     - counter            [data-count]
     - HUD scroll foizi   [data-hud-scroll] / [data-progress] / [data-hud-sec] / [data-hud-xy]
     - marquee — CSS animatsiya (faqat reduced-motion'da to'xtaydi)

   prefers-reduced-motion: reduce -> hamma narsa darhol ko'rinadi, transformsiz.
   ===================================================================== */
(function () {
  "use strict";

  var reduce = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // JS mavjud — CSS'ga belgi beramiz (pre-hide faqat shunda qo'llanadi).
  document.documentElement.classList.add("js");

  function $all(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  // ------------------------------------------------------------------
  // HUD — scroll foizi, progress bar, bo'lim indikatori, X/Y
  // ------------------------------------------------------------------
  function initHud() {
    var hudScroll = document.querySelector("[data-hud-scroll]");
    var progress = document.querySelector("[data-progress]");
    var hudSec = document.querySelector("[data-hud-sec]");
    var hudXY = document.querySelector("[data-hud-xy]");
    var sections = $all("section[id]");

    function onScroll() {
      var doc = document.documentElement;
      var max = (doc.scrollHeight - window.innerHeight) || 1;
      var sy = window.scrollY || window.pageYOffset || 0;
      var p = Math.min(Math.max(sy / max, 0), 1);
      if (progress) progress.style.width = (p * 100).toFixed(1) + "%";
      if (hudScroll) hudScroll.textContent = String(Math.round(p * 100)).padStart(3, "0") + "%";
      if (hudSec && sections.length) {
        var mid = sy + window.innerHeight * 0.42;
        var cur = null;
        for (var i = 0; i < sections.length; i++) {
          if (sections[i].offsetTop <= mid) cur = sections[i];
        }
        if (cur) {
          var label = cur.getAttribute("data-hud-label");
          hudSec.textContent = label || cur.id.toUpperCase();
        } else {
          hudSec.textContent = "01 · INTRO";
        }
      }
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    if (hudXY && !reduce) {
      window.addEventListener("mousemove", function (e) {
        var ax = e.clientX / window.innerWidth;
        var ay = e.clientY / window.innerHeight;
        hudXY.textContent = "X:" + ax.toFixed(2) + " · Y:" + ay.toFixed(2);
      });
    }
    onScroll();
  }

  // ------------------------------------------------------------------
  // Counter — [data-count]. Raqam bo'lmasa (UZ) o'zgartirmaydi.
  // ------------------------------------------------------------------
  function animateCounters() {
    $all("[data-count]").forEach(function (el) {
      var target = parseInt(el.getAttribute("data-count"), 10);
      if (isNaN(target)) return;
      if (reduce || target <= 0) { el.textContent = String(target); return; }
      var steps = 28, n = 0;
      var iv = setInterval(function () {
        n++;
        el.textContent = String(Math.min(Math.round((target / steps) * n), target));
        if (n >= steps) { el.textContent = String(target); clearInterval(iv); }
      }, 34);
    });
  }

  // ------------------------------------------------------------------
  // Scroll reveal + skill bar fill
  // ------------------------------------------------------------------
  function initReveals() {
    var revealEls = $all("[data-reveal]");
    var barEls = $all("[data-bar]");

    // Bar'larning maqsad kengligini saqlaymiz (inline width="level%").
    barEls.forEach(function (b) {
      b.setAttribute("data-target-width", b.style.width || "100%");
    });

    if (reduce) {
      // Darhol ko'rinadi — transformsiz (bar'lar to'la holatda qoladi).
      return;
    }

    // Dastlab yashiramiz.
    revealEls.forEach(function (el) { el.classList.add("pre-hide"); });
    barEls.forEach(function (b) { b.style.width = "0%"; });

    function show(el) { el.classList.remove("pre-hide"); }
    function fill(b) { b.style.width = b.getAttribute("data-target-width") || "100%"; }

    if (window.gsap && window.ScrollTrigger) {
      // ---- GSAP ScrollTrigger yo'li (03-UIUX 4-bo'lim) ----
      window.gsap.registerPlugin(window.ScrollTrigger);
      revealEls.forEach(function (el) {
        window.ScrollTrigger.create({
          trigger: el, start: "top 92%", once: true,
          onEnter: function () { show(el); },
        });
      });
      barEls.forEach(function (b) {
        window.ScrollTrigger.create({
          trigger: b, start: "top 90%", once: true,
          onEnter: function () { fill(b); },
        });
      });
    } else if ("IntersectionObserver" in window) {
      // ---- Fallback: IntersectionObserver (CDN yuklanmasa) ----
      var ro = new IntersectionObserver(function (entries, obs) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { show(e.target); obs.unobserve(e.target); }
        });
      }, { rootMargin: "0px 0px -8% 0px" });
      revealEls.forEach(function (el) { ro.observe(el); });

      var bo = new IntersectionObserver(function (entries, obs) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { fill(e.target); obs.unobserve(e.target); }
        });
      }, { rootMargin: "0px 0px -10% 0px" });
      barEls.forEach(function (b) { bo.observe(b); });
    } else {
      // JS bor, lekin observer yo'q — hammasini ko'rsatamiz.
      revealEls.forEach(show);
      barEls.forEach(fill);
    }
  }

  // ------------------------------------------------------------------
  // Hero reveal — boot tugagach matn stagger bilan chiqadi.
  // ------------------------------------------------------------------
  var heroDone = false;
  function startHeroIntro() {
    if (heroDone) return;
    heroDone = true;
    var heroEls = $all("[data-hero]");
    if (!reduce) {
      heroEls.forEach(function (el) { el.classList.add("pre-hide"); });
      heroEls.forEach(function (el, i) {
        setTimeout(function () { el.classList.remove("pre-hide"); }, i * 90);
      });
    }
    animateCounters();
  }

  // ------------------------------------------------------------------
  // Boot sequence — [data-boot] overlay.
  // ------------------------------------------------------------------
  function initBoot() {
    var overlay = document.querySelector("[data-boot]");
    if (!overlay) { startHeroIntro(); return; }
    if (reduce) {
      overlay.style.display = "none";
      startHeroIntro();
      return;
    }
    var bar = overlay.querySelector("[data-bootbar]");
    var pctEl = overlay.querySelector("[data-bootpct]");
    var lines = $all("[data-bootline]", overlay);
    lines.forEach(function (l) { l.style.opacity = "0"; l.style.transition = "opacity .25s ease"; });

    var pct = 0;
    var timer = setInterval(function () {
      pct = Math.min(pct + 3, 100);
      if (bar) bar.style.width = pct + "%";
      if (pctEl) pctEl.textContent = String(pct).padStart(3, "0") + "%";
      var shown = Math.round((pct / 100) * lines.length);
      for (var i = 0; i < lines.length; i++) if (i < shown) lines[i].style.opacity = "1";
      if (pct >= 100) {
        clearInterval(timer);
        for (var j = 0; j < lines.length; j++) lines[j].style.opacity = "1";
        overlay.style.transition = "opacity .6s ease";
        overlay.style.opacity = "0";
        overlay.style.pointerEvents = "none";
        setTimeout(function () { overlay.style.display = "none"; }, 650);
        startHeroIntro();
      }
    }, 55);
  }

  // ------------------------------------------------------------------
  // Mobil nav toggle
  // ------------------------------------------------------------------
  function initNav() {
    var toggle = document.querySelector("[data-nav-toggle]");
    var links = document.querySelector("[data-nav-links]");
    if (!toggle || !links) return;
    toggle.addEventListener("click", function () {
      links.classList.toggle("open");
    });
    $all("a", links).forEach(function (a) {
      a.addEventListener("click", function () { links.classList.remove("open"); });
    });
  }

  function start() {
    initNav();
    initHud();
    initReveals();
    initBoot();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
