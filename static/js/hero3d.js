/* =====================================================================
   hero3d.js — Three.js sahnalar (Portfolio.dc.html DCLogic'dan React'siz
   qayta yozilgan).

   Ikki sahna:
     1) #hero-canvas  — signature wireframe icosahedron (auto-rotate +
        mouse-parallax + yuklanish "paydo bo'lishi").
     2) #bg-canvas    — fon: nuqtalar to'ri + sekin aylanuvchi wireframe
        shakllar (ambient chuqurlik).

   Talablar: window.THREE (CDN). Yo'q bo'lsa — jim chiqib ketadi (sayt
   baribir o'qiladi: 01-Arxitektura risk #3 graceful fallback).
   prefers-reduced-motion: auto-rotate va parallax o'chadi (statik render).
   ===================================================================== */
(function () {
  "use strict";

  function cssVar(name, fallback) {
    var v = getComputedStyle(document.documentElement).getPropertyValue(name);
    return (v && v.trim()) || fallback;
  }

  function clamp(v, lo, hi) { return Math.min(Math.max(v, lo), hi); }

  function HeroScene() {
    var THREE = window.THREE;
    if (!THREE) return; // CDN yuklanmadi — sokin chiqib ketamiz.

    this.THREE = THREE;
    this.reduce = window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    // Mobil/kichik ekran: og'ir 3D'ni yengillashtirish (03-UIUX 5-bo'lim).
    this.small = window.matchMedia && window.matchMedia("(max-width: 640px)").matches;

    this.signal = cssVar("--signal", "#E0A458");
    this.muted = cssVar("--muted", "#8A92A0");

    this.heroCanvas = document.getElementById("hero-canvas");
    this.bgCanvas = document.getElementById("bg-canvas");

    // Parallax maqsad/joriy qiymatlari (lerp bilan silliq).
    this.curTX = 0; this.curTY = 0; this.tgTX = 0; this.tgTY = 0;
    this.autoY = 0; this.bgTime = 0; this.bgPX = 0; this.bgPY = 0;
    this.introT = 0;

    this.initHero();
    this.initBg();

    if (this.renderer || this.bgRenderer) {
      this._onResize = this.onResize.bind(this);
      this._onMove = this.onMove.bind(this);
      window.addEventListener("resize", this._onResize);
      if (!this.reduce && !this.small) {
        window.addEventListener("mousemove", this._onMove);
      }
      this.loop();
    }
  }

  HeroScene.prototype.initHero = function () {
    var THREE = this.THREE;
    var c = this.heroCanvas;
    if (!c) return;
    var wrap = c.parentElement;
    var w = wrap.clientWidth || 420, h = wrap.clientHeight || 420;

    this.renderer = new THREE.WebGLRenderer({ canvas: c, alpha: true, antialias: true });
    this.renderer.setSize(w, h, false);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100);
    this.camera.position.z = 4.4;

    // Tashqi wireframe icosahedron (signal rang) — past poly mobil uchun.
    var detail = this.small ? 0 : 1;
    var geo = new THREE.IcosahedronGeometry(1.55, detail);
    this.mat = new THREE.LineBasicMaterial({
      color: new THREE.Color(this.signal), transparent: true, opacity: 0.9,
    });
    this.mesh = new THREE.LineSegments(new THREE.WireframeGeometry(geo), this.mat);
    this.scene.add(this.mesh);

    // Ichki shakl (muted) — chuqurlik beradi.
    var innerGeo = new THREE.IcosahedronGeometry(0.85, 0);
    this.innerMat = new THREE.LineBasicMaterial({
      color: new THREE.Color(this.muted), transparent: true, opacity: 0.4,
    });
    this.inner = new THREE.LineSegments(new THREE.WireframeGeometry(innerGeo), this.innerMat);
    this.scene.add(this.inner);

    // Yuklanish "paydo bo'lishi" uchun kichik boshlang'ich masshtab.
    this.mesh.scale.setScalar(this.reduce ? 1 : 0.82);
  };

  HeroScene.prototype.initBg = function () {
    var THREE = this.THREE;
    var c = this.bgCanvas;
    if (!c || this.small) return; // mobile fon sahnasini o'tkazib yuboramiz.
    var w = window.innerWidth, h = window.innerHeight;

    this.bgRenderer = new THREE.WebGLRenderer({ canvas: c, alpha: true, antialias: true });
    this.bgRenderer.setSize(w, h, false);
    this.bgRenderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    this.bgScene = new THREE.Scene();
    this.bgCamera = new THREE.PerspectiveCamera(55, w / h, 0.1, 100);
    this.bgCamera.position.z = 20;
    this.bgGroup = new THREE.Group();

    var N = 96, RX = 17, RY = 11, RZ = 8, TH = 5.0;
    var pts = [];
    for (var i = 0; i < N; i++) {
      pts.push(new THREE.Vector3(
        (Math.random() * 2 - 1) * RX,
        (Math.random() * 2 - 1) * RY,
        (Math.random() * 2 - 1) * RZ
      ));
    }
    var posArr = [];
    pts.forEach(function (p) { posArr.push(p.x, p.y, p.z); });
    var pg = new THREE.BufferGeometry();
    pg.setAttribute("position", new THREE.Float32BufferAttribute(posArr, 3));
    this.bgPointsMat = new THREE.PointsMaterial({
      color: new THREE.Color(this.signal), size: 0.18,
      transparent: true, opacity: 0.85, sizeAttenuation: true,
    });
    this.bgGroup.add(new THREE.Points(pg, this.bgPointsMat));

    // Katta sekin aylanuvchi wireframe shakllar.
    this.bgShapes = [];
    this.bgShapeMat = new THREE.LineBasicMaterial({
      color: new THREE.Color(this.signal), transparent: true, opacity: 0.16,
    });
    var defs = [
      { geo: new THREE.IcosahedronGeometry(3.6, 0), pos: [-11, 5, -3], spin: 0.0016 },
      { geo: new THREE.OctahedronGeometry(3.0, 0), pos: [12, -6, -2], spin: -0.0022 },
      { geo: new THREE.DodecahedronGeometry(3.2, 0), pos: [3, 7, -5], spin: 0.0019 },
      { geo: new THREE.IcosahedronGeometry(2.6, 0), pos: [-9, -7, -4], spin: -0.0014 },
    ];
    var self = this;
    defs.forEach(function (d) {
      var m = new THREE.LineSegments(new THREE.WireframeGeometry(d.geo), self.bgShapeMat);
      m.position.set(d.pos[0], d.pos[1], d.pos[2]);
      m.userData.spin = d.spin;
      m.rotation.set(Math.random() * 3, Math.random() * 3, 0);
      self.bgShapes.push(m);
      self.bgGroup.add(m);
    });

    // Yaqin nuqtalarni bog'lovchi chiziqlar.
    var linePos = [];
    for (var a = 0; a < N; a++) {
      for (var b = a + 1; b < N; b++) {
        if (pts[a].distanceTo(pts[b]) < TH) {
          linePos.push(pts[a].x, pts[a].y, pts[a].z, pts[b].x, pts[b].y, pts[b].z);
        }
      }
    }
    var lg = new THREE.BufferGeometry();
    lg.setAttribute("position", new THREE.Float32BufferAttribute(linePos, 3));
    this.bgLineMat = new THREE.LineBasicMaterial({
      color: new THREE.Color(this.muted), transparent: true, opacity: 0.3,
    });
    this.bgGroup.add(new THREE.LineSegments(lg, this.bgLineMat));

    this.bgScene.add(this.bgGroup);
  };

  HeroScene.prototype.loop = function () {
    this.raf = requestAnimationFrame(this.loop.bind(this));
    var motion = !this.reduce;
    var sy = window.scrollY || window.pageYOffset || 0;

    if (this.mesh && this.renderer) {
      if (motion) this.autoY += 0.0034;                 // sekin auto-rotate
      this.introT = Math.min(this.introT + 0.02, 1);    // paydo bo'lish
      var ease = 1 - Math.pow(1 - this.introT, 3);
      var base = 0.82 + 0.18 * ease;
      this.mesh.scale.setScalar(base * (1 + Math.min(sy / 2600, 0.32)));
      this.curTX += (this.tgTX - this.curTX) * 0.05;     // lerp parallax
      this.curTY += (this.tgTY - this.curTY) * 0.05;
      this.mesh.rotation.y = this.autoY + this.curTY;
      this.mesh.rotation.x = this.curTX * 0.6;
      this.mesh.rotation.z = sy * 0.0004;
      if (this.inner) {
        this.inner.rotation.y = -this.autoY * 0.6 + this.curTY * 0.5;
        this.inner.rotation.x = -this.curTX * 0.4;
      }
      this.renderer.render(this.scene, this.camera);
    }

    if (this.bgGroup && this.bgRenderer) {
      if (motion) this.bgTime += 0.0012;
      this.bgGroup.rotation.y = this.bgTime + sy * 0.00045;   // scroll parallax
      this.bgGroup.rotation.x = Math.sin(this.bgTime * 0.7) * 0.06 + sy * 0.00012;
      this.bgPX += ((this.tgTY * 2.4) - this.bgPX) * 0.04;
      this.bgPY += ((-this.tgTX * 1.6) - this.bgPY) * 0.04;
      this.bgGroup.position.x = this.bgPX;
      this.bgGroup.position.y = this.bgPY;
      if (this.bgShapes && motion) {
        for (var i = 0; i < this.bgShapes.length; i++) {
          var s = this.bgShapes[i];
          s.rotation.y += s.userData.spin;
          s.rotation.x += s.userData.spin * 0.6;
        }
      }
      this.bgRenderer.render(this.bgScene, this.bgCamera);
    }
  };

  HeroScene.prototype.onMove = function (e) {
    var ax = e.clientX / window.innerWidth;
    var ay = e.clientY / window.innerHeight;
    this.tgTY = (ax - 0.5) * 0.7;
    this.tgTX = (ay - 0.5) * 0.7;
  };

  HeroScene.prototype.onResize = function () {
    if (this.renderer && this.heroCanvas) {
      var wrap = this.heroCanvas.parentElement;
      var w = wrap.clientWidth, h = wrap.clientHeight;
      this.renderer.setSize(w, h, false);
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
    }
    if (this.bgRenderer && this.bgCamera) {
      var vw = window.innerWidth, vh = window.innerHeight;
      this.bgRenderer.setSize(vw, vh, false);
      this.bgCamera.aspect = vw / vh;
      this.bgCamera.updateProjectionMatrix();
    }
  };

  function start() {
    // Hech bo'lmasa bitta canvas mavjud bo'lsa ishga tushiramiz.
    if (document.getElementById("hero-canvas") || document.getElementById("bg-canvas")) {
      try { new HeroScene(); } catch (err) { /* graceful: motion'siz davom */ }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
