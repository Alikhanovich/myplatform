# 03 — UI/UX + Motion Dizayn Spetsifikatsiyasi

> Shaxsiy portfolio sayt · Mavzu: "tizimlar va boshqaruv panellari quruvchisi"
> Estetika: texnik / o'lchov-asbobi (instrument) · grid · monospace urg'u
> Motion: maksimal, lekin tartibli — bitta signature moment, qolgani jim
> Jonli mockup: `Portfolio.dc.html` (shu hujjat bilan birga keladi, 3 yo'nalish switcher bilan)

---

## BOSQICH 1 — Dizayn rejasi va o'z-tanqid

### Konsepsiya
Egasi **tizimlar quradi** — hujjat avtomatlashtirish, davomat tracking, test
platformalari. Demak portfolio o'zi ham **boshqaruv paneli / o'lchov asbobi**
kabi ko'rinishi kerak: kalibrlangan grid, koordinata o'qlari, monospace
readout'lar, "signal" urg'usi. Bu — vizual metafora, bezak emas.

### Rang palitra (asosiy yo'nalish: "Graphite & Signal")
| Token | Hex | Ishlatilishi |
|---|---|---|
| `--bg` | `#16181D` | Asosiy fon — sovuq grafit (qora EMAS, biroz ko'k-kulrang) |
| `--panel` | `#1E2127` | Panel/karta foni |
| `--line` | `#2C313A` | Grid chiziqlari, chegaralar |
| `--fg` | `#E7E9EC` | Asosiy matn — sovuq oq |
| `--muted` | `#8A92A0` | Ikkilamchi matn, monospace label |
| `--signal` | `oklch(0.78 0.13 75)` ≈ `#E6A martin` (amber-ochre) | Yagona urg'u — "signal"/o'lchov nuqtasi |

> Eslatma: aniq signal hex = `#E0A458` (iliq ochre-amber). Neon EMAS, kalibr-asbob nuri.

### Tipografika
| Rol | Shrift | Nega |
|---|---|---|
| Display (sarlavhalar) | **Space Grotesk** | Geometrik, biroz "muhandislik" hissi, lekin sovuq emas — shaxsiylik bor |
| Body (matn) | **Inter Tight** yoki tizim sans | O'qish uchun toza, zич (tight) varianti display bilan jaranglaydi |
| Mono / utility (label, readout, koordinata) | **JetBrains Mono** | "Instrument readout" estetikasi — raqamlar, koordinatalar, kategoriyalar |

> Inter "default" deb tanqid qilinishi mumkin — shuning uchun **Inter Tight**
> (zичroq, kamroq ishlatilgan variant) + display'da Space Grotesk farqlanishni beradi.

### Layout konsepsiyasi
Butun sahifa **kalibrlangan koordinata maydoni** ustida: chap chetda doimiy vertikal
"o'q" (monospace section indekslari `01 / 02 / 03`), yuqorida nozik grid chiziqlari.
Har bo'lim — "panel" kabi, burchaklarda kichik kalibr belgilari (corner ticks).

```
┌────────────────────────────────────────────┐
│ [logo]              nav · nav · nav   [01]  │  ← sticky nav, mono indeks
├──┬─────────────────────────────────────────┤
│0 │   HERO                                   │
│1 │   katta ism + lavozim          ┌──────┐  │  ← signature 3D
│  │   "tizimlar quruvchi"          │ wire │  │     wireframe shakl
│  │   [hero statlar: 12 · 3+ ...]  │ frame│  │     (auto-rotate +
│  │                                └──────┘  │      mouse parallax)
├──┼─────────────────────────────────────────┤
│0 │   ABOUT / TAJRIBA (timeline panellar)    │
│2 │                                          │
├──┼─────────────────────────────────────────┤
│0 │   SKILLS (kalibr-bar 0–100, mono label)  │
│3 │                                          │
├──┼─────────────────────────────────────────┤
│0 │   LOYIHALAR (grid kartalar, hover ochiladi)│
│4 │                                          │
├──┼─────────────────────────────────────────┤
│0 │   BLOG PREVIEW (3 ta so'nggi)            │
│5 │                                          │
├──┼─────────────────────────────────────────┤
│0 │   CONTACT (mono "terminal" uslubi)       │
│6 │                                          │
└──┴─────────────────────────────────────────┘
```

### Signature element
**Hero'dagi wireframe polyhedron** (masalan kesilgan ikosaedr / "tugun" shakli),
Three.js bilan: doimiy sekin auto-rotate + sichqonchaga **parallax** javob beradi,
yuklanishda chiziqlari ketma-ket "chiziladi". Bu — egasining "tizim/struktura"
mavzusining **bitta kuchli vizual tasviri**. Qolgan animatsiyalar undan jimroq.

### O'z-tanqid: "bu AI-default emasmi?"
- ❌ *"Qora fon + neon yashil terminal"* — eng ko'p ishlatilgan AI-portfolio klişesi.
  → **Tuzatildi:** grafit (qora emas) + **amber-ochre** signal (yashil/neon emas).
- ❌ *"Aylanuvchi 3D shar/torus bezak sifatida"* — ma'nosiz dekor.
  → **Tuzatildi:** wireframe shakl **mavzuga bog'liq** (struktura/tizim metaforasi),
  dekor emas; bitta joyda, qolgani jim.
- ❌ *"Inter hamma joyda"* — default sans.
  → **Tuzatildi:** Space Grotesk display + JetBrains Mono utility farqlanish beradi.
- ❌ *"Har element fade-in + ko'p parallax"* — AI-slop motion.
  → **Tuzatildi:** scroll-reveal **nozik** (kichik translate + opacity), parallax
  faqat 1-2 element, `prefers-reduced-motion` to'liq qo'llab-quvvatlanadi.

---

## BOSQICH 2 — To'liq UI/UX spetsifikatsiya

### 1. Sitemap + har sahifaning bitta vazifasi (single job)

| Sahifa | Single job |
|---|---|
| Bosh sahifa `/` | "Bu odam kim va nima quradi" — 10 soniyada ishonch hosil qildirish |
| Loyihalar `/projects/` | Barcha ishlarni skanerlash imkoni |
| Loyiha detali `/projects/<slug>/` | Bitta loyihaning **chuqurligini** ko'rsatish (muammo→yechim→stack) |
| Blog ro'yxati `/blog/` | "Bu odam o'ylaydi va yozadi" — fikr chuqurligi |
| Blog detali `/blog/<slug>/` | Bitta maqolani bemalol o'qitish |

### 2. ASCII wireframe — sahifalar

**Loyiha detali:**
```
┌──────────────────────────────────────────┐
│ ← orqaga          [04 / loyiha]           │
│ LOYIHA NOMI                               │
│ qisqa summary · [Django][Flutter][...]    │
│ ┌──────────────────────────────────────┐ │
│ │   cover image (full-bleed)           │ │
│ └──────────────────────────────────────┘ │
│ ## Muammo      ## Yechim     ## Natija    │
│ to'liq matn (o'qish uchun keng kolonka)   │
│ [ Demo ↗ ]  [ Repo ↗ ]                    │
│ ── keyingi loyiha →                       │
└──────────────────────────────────────────┘
```

**Blog ro'yxati:**
```
┌──────────────────────────────────────────┐
│ BLOG                     [05]             │
│ [hammasi][Django][Flutter][SaaS]  ← filtr │
│ ┌────────┐ sana · kategoriya              │
│ │ thumb  │ sarlavha                        │
│ └────────┘ excerpt ...            o'qish → │
│ (ro'yxat, pagination pastda)              │
└──────────────────────────────────────────┘
```

### 3. Design token jadvali

**Rang** (asosiy "Graphite & Signal" yo'nalishi)
| Token | Hex | Joy |
|---|---|---|
| bg | `#16181D` | sahifa foni |
| panel | `#1E2127` | kartalar |
| line | `#2C313A` | grid, chegara |
| fg | `#E7E9EC` | asosiy matn |
| muted | `#8A92A0` | label, mono |
| signal | `#E0A458` | urg'u, hover, active |

> Mockupda yana 2 yo'nalish bor (switcher orqali): **"Blueprint"** (iliq qog'oz
> `#EEEAE0` + ink `#1A1D21` + blueprint-blue `#3B6CA8`) va **"Slate Terminal"**
> (chuqur slate `#12161D` + steel + desaturlangan teal `#5BA6A0`). Uchalasi ham
> bir xil grid/mono DNA, faqat palitra/shaxsiyat farq qiladi.

**Tipografika**
| Daraja | Shrift | O'lcham (desktop) | Weight |
|---|---|---|---|
| Display XL (hero ism) | Space Grotesk | 72–96px | 600 |
| Display L (bo'lim sarlavha) | Space Grotesk | 40–48px | 600 |
| Body | Inter Tight | 16–18px | 400 |
| Body lead | Inter Tight | 20–22px | 400 |
| Mono label / readout | JetBrains Mono | 12–13px | 500, letter-spacing 0.08em, UPPERCASE |

**Spacing scale** (4px asos): `4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96 · 128`.
Bo'limlar orasi 96–128px, panel ichi 24–32px.

### 4. Motion spetsifikatsiyasi

**Hero (signature):**
- 3D obyekt: **wireframe polyhedron** (icosahedron geometry, `WireframeGeometry`,
  nozik chiziqlar, signal rang).
- Doimiy harakat: sekin **auto-rotate** (~0.15 rad/s Y o'qida).
- **Mouse-parallax:** sichqoncha pozitsiyasiga qarab obyekt ±8° egiladi (lerp bilan
  silliq).
- Yuklanish ketma-ketligi: (1) grid chiziqlari fade-in (0.3s) → (2) wireframe
  chiziqlari `drawSVG`-uslubida ketma-ket paydo bo'ladi / yoki opacity 0→1 +
  scale 0.9→1 (0.8s) → (3) hero matn pastdan yuqoriga (stagger 0.06s).

**Scroll-trigger (GSAP ScrollTrigger):**
- Har bo'lim ko'rinishga kirganda: **translateY(24px)→0 + opacity 0→1**, davomiyligi
  0.6s, ease `power2.out`. Nozik — sakrash yo'q.
- Skills barlar: ko'ringanda 0→`level%` kenglikka animatsiya (0.8s, stagger).
- Parallax: faqat (a) hero 3D obyekt va (b) bo'lim fonidagi grid — scroll'da
  sekinroq harakatlanadi (yvelocity ~0.3x). Boshqa hech narsa parallax qilmaydi.

**Micro-interactions:**
- Loyiha karta hover: chegara `line`→`signal`, yuqoriga 4px ko'tariladi, burchak
  kalibr-tick'lari yorishadi, mono "view ↗" paydo bo'ladi.
- Tugma/link hover: signal rang underline "chiziladi" (chapdan o'ngga).
- Nav link active: pastida mono indeks + signal nuqta.

**`prefers-reduced-motion: reduce` (MAJBURIY):**
- 3D auto-rotate va parallax **o'chadi** — wireframe statik ko'rinadi (yoki butunlay
  statik SVG fallback).
- Scroll-reveal'lar **darhol** ko'rinadi (opacity 1, transform yo'q).
- Faqat ranglar/hover state'lar (transition-siz ham) saqlanadi.

### 5. Responsive qoidalari
| Breakpoint | O'zgarish |
|---|---|
| ≥1024px (desktop) | To'liq 3D + parallax + barcha scroll-reveal |
| 640–1024px (tablet) | 3D saqlanadi lekin past poly; parallax intensivligi yarmiga; grid 2-kolonka |
| <640px (mobile) | 3D'ni **statik render** yoki butunlay statik SVG fallback bilan almashtirish (batareya/perf); parallax o'chadi; bir kolonka; mono o'q yashiriladi yoki yuqoriga ko'chiriladi |

### 6. Bo'sh holatlar (empty states)
| Holat | Ko'rsatiladigan | Ohang |
|---|---|---|
| Loyiha yo'q | Mono ramka ichida: `// loyihalar tez orada qo'shiladi` + nozik grid | Texnik, jim, "kutilmoqda" hissi — uzr emas |
| Blog bo'sh | `// hali yozilmagan. birinchi yozuv yo'lda.` | Shaxsiy, kamtarona |
| Rasm yuklanmagan | Striped placeholder + mono `[ cover ]` | Neytral |

### 7. Matn ohangi — real misol jumlalar (O'zbek, texnik-shaxsiy)

- **Hero tagline:** "Tizimlar quraman — hujjat avtomatlashtirishdan SaaS mahsulotlargacha."
- **Hero subline:** "Django bilan backend, Flutter bilan mobil. Universitet hujjatlarini
  va talaba ma'lumotlarini tartibga soladigan tizimlar."
- **About ochilishi:** "Men murakkab jarayonlarni ishonchli, boshqariladigan
  tizimlarga aylantiraman."
- **Bo'lim sarlavhalari:** `01 · KIM` · `02 · TAJRIBA` · `03 · KO'NIKMALAR` ·
  `04 · LOYIHALAR` · `05 · YOZUVLAR` · `06 · ALOQA`
- **CTA tugmalari:** "Loyihani ko'rish ↗" · "Repozitoriy ↗" · "Yozib qoldiring"
- **Contact:** "Yangi tizim qurish kerakmi? Yozing — javob beraman."

---

## Mockup haqida
`Portfolio.dc.html` — shu spetsifikatsiyaning **jonli, ishlaydigan** versiyasi:
haqiqiy Three.js wireframe hero (auto-rotate + mouse-parallax), GSAP ScrollTrigger
reveal'lar, `prefers-reduced-motion` qo'llab-quvvatlash. Tweaks panelidan **3 yo'nalishni**
(Graphite / Blueprint / Slate) jonli almashtirish mumkin — har biri to'liq ishlaydigan
sayt, dead screenshot emas.
