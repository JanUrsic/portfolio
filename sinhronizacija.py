#!/usr/bin/env python3
"""
sinhronizacija.py — Objavi vsebino iz ~/Desktop/PORTFOLIO na GitHub Pages.

Prebere strukturo:
  ~/Desktop/PORTFOLIO/
  ├── KOMERCIALNO/
  │   ├── HERO/                    (ena fotka, hero za panel na domov)
  │   └── Ime projekta/            (ime = naslov na spletu)
  │       ├── cover.jpg (opcijsko) (če obstaja, override; sicer 01.jpg = cover)
  │       └── IMG-1.jpg ... N.jpg
  ├── DOGODKI/  ... enako
  ├── ŠPORT/    ... enako
  └── KONCERTI/ ... enako

Za vsako fotko: resize na max 2000 wide (2400 za hero), stiskanje quality 82.
Za vsak nov projekt: generira /category/slug/index.html (galerija + lightbox).
Za vsako kategorijo: regenerira /category/index.html s karticami vseh projektov.
Obstoječih project index.html NE prepiše — respektira ročne editacije naslovov/meta.
Na koncu: git add -A + commit + push.
"""

from __future__ import annotations  # kompatibilnost s Python 3.7+ (potrebno za "str | None" hint)

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from string import Template

# ═══════════════════════════════════════════════════════════════════
# KONFIGURACIJA
# ═══════════════════════════════════════════════════════════════════

SRC = Path.home() / "Desktop" / "PORTFOLIO"
DST = Path.home() / "Documents" / "PORTFOLIO"

# Desktop CATEGORY_DIR → (web_slug, display_name, page_subtitle)
CATEGORIES = {
    "KOMERCIALNO": (
        "komercialno",
        "Komercialno",
        "Brand, produkt, lifestyle. Vizualni jezik, ki znamki pomaga prodajati — od studio shootinga do kampanj na terenu.",
    ),
    "DOGODKI": (
        "dogodki",
        "Dogodki",
        "Konference, otvoritve, korporativni dogodki in zasebna slavja. Atmosfera, ki ostane v slikah.",
    ),
    "ŠPORT": (
        "sport",
        "Šport",
        "Tekme, treningi, maratoni. Stotinke, ki odločajo — in trenutki, ki jih ne moreš ponoviti.",
    ),
    "KONCERTI": (
        "koncerti",
        "Koncerti",
        "Stage, znoj, množica. Ujamem energijo, ki jo bend in publika ustvarita skupaj.",
    ),
}

RESIZE_MAX_WIDTH = 2000          # gallery photos
HERO_MAX_WIDTH   = 2400          # hero images (wider viewport)
JPEG_QUALITY     = 82
COMPRESS_THRESHOLD = 800_000     # only recompress files > 800 KB (already-optimized skipped)

IMG_EXTS = {".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG"}

# ═══════════════════════════════════════════════════════════════════
# SVG IKONE (za nav + mobile menu)
# ═══════════════════════════════════════════════════════════════════

SVG_IG = '<svg viewBox="0 0 24 24"><path d="M12 2.2c3.2 0 3.6 0 4.8.1 1.2.1 1.8.2 2.2.4.6.2 1 .5 1.4 1 .5.4.8.8 1 1.4.2.4.4 1 .4 2.2.1 1.2.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 1.2-.2 1.8-.4 2.2-.2.6-.5 1-1 1.4-.4.5-.8.8-1.4 1-.4.2-1 .4-2.2.4-1.2.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-1.2-.1-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-1-.5-.4-.8-.8-1-1.4-.2-.4-.4-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8c.1-1.2.2-1.8.4-2.2.2-.6.5-1 1-1.4.4-.5.8-.8 1.4-1 .4-.2 1-.4 2.2-.4C8.4 2.2 8.8 2.2 12 2.2zm0 3.1c2.7 0 4.9 2.2 4.9 4.9s-2.2 4.9-4.9 4.9-4.9-2.2-4.9-4.9 2.2-4.9 4.9-4.9zm0 8.1c1.7 0 3.2-1.4 3.2-3.2s-1.4-3.2-3.2-3.2-3.2 1.4-3.2 3.2 1.4 3.2 3.2 3.2zm6.2-8.3c0 .6-.5 1.1-1.1 1.1s-1.1-.5-1.1-1.1.5-1.1 1.1-1.1 1.1.5 1.1 1.1z"/></svg>'
SVG_FB = '<svg viewBox="0 0 24 24"><path d="M22 12c0-5.5-4.5-10-10-10S2 6.5 2 12c0 5 3.7 9.1 8.4 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.3c-1.2 0-1.6.8-1.6 1.6V12h2.8l-.4 2.9h-2.3v7C18.3 21.1 22 17 22 12z"/></svg>'
SVG_YT = '<svg viewBox="0 0 24 24"><path d="M21.6 7.2c-.2-.9-.9-1.6-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4c-.9.2-1.6.9-1.8 1.8C2 8.8 2 12 2 12s0 3.2.4 4.8c.2.9.9 1.6 1.8 1.8 1.6.4 7.8.4 7.8.4s6.2 0 7.8-.4c.9-.2 1.6-.9 1.8-1.8.4-1.6.4-4.8.4-4.8s0-3.2-.4-4.8zM10 15V9l5.2 3-5.2 3z"/></svg>'
SVG_TT = '<svg viewBox="0 0 24 24"><path d="M19.6 6.3c-1.4-.9-2.3-2.4-2.5-4.1V2h-3.2v12.7c0 1.5-1.2 2.7-2.7 2.7-1.5 0-2.7-1.2-2.7-2.7s1.2-2.7 2.7-2.7c.3 0 .5 0 .8.1V8.7c-.3 0-.5-.1-.8-.1-3.3 0-5.9 2.6-5.9 5.9s2.6 5.9 5.9 5.9 5.9-2.6 5.9-5.9V8.1c1.3.9 2.8 1.5 4.4 1.5V6.4c-.6 0-1.3 0-1.9-.1z"/></svg>'

def make_nav_socials():
    return "\n".join([
        f'    <li><a href="#" target="_blank" rel="noopener" aria-label="Instagram">{SVG_IG}</a></li>',
        f'    <li><a href="#" target="_blank" rel="noopener" aria-label="Facebook">{SVG_FB}</a></li>',
        f'    <li><a href="#" target="_blank" rel="noopener" aria-label="YouTube">{SVG_YT}</a></li>',
        f'    <li><a href="#" target="_blank" rel="noopener" aria-label="TikTok">{SVG_TT}</a></li>',
    ])

def make_mobile_socials():
    return "\n".join([
        f'    <a href="#" target="_blank" rel="noopener" aria-label="Instagram">{SVG_IG}</a>',
        f'    <a href="#" target="_blank" rel="noopener" aria-label="Facebook">{SVG_FB}</a>',
        f'    <a href="#" target="_blank" rel="noopener" aria-label="YouTube">{SVG_YT}</a>',
        f'    <a href="#" target="_blank" rel="noopener" aria-label="TikTok">{SVG_TT}</a>',
    ])

# ═══════════════════════════════════════════════════════════════════
# HTML TEMPLATE — projektna stran (galerija + lightbox)
# ═══════════════════════════════════════════════════════════════════

PROJECT_TEMPLATE = Template(r'''<!DOCTYPE html>
<html lang="sl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="$title — projekt Jana Uršiča.">
<title>$title — Jan Uršič Photography</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../style.css">
</head>
<body>

<nav class="nav" id="nav">
  <a href="../../" class="logo">
    <span class="logo-name">Jan Uršič</span>
    <span class="logo-tag">Photography</span>
  </a>

  <ul class="nav-cats" aria-label="Kategorije">
    <li><a href="../../komercialno/" class="cat-pill $active_kom">Komercialno</a></li>
    <li><a href="../../dogodki/" class="cat-pill $active_dog">Dogodki</a></li>
    <li><a href="../../sport/" class="cat-pill $active_spo">Šport</a></li>
    <li><a href="../../koncerti/" class="cat-pill $active_kon">Koncerti</a></li>
  </ul>

  <ul class="nav-socials" aria-label="Družbena omrežja">
$nav_socials
  </ul>

  <button class="hamburger" id="hamburger" aria-label="Meni" aria-expanded="false">
    <span></span><span></span><span></span>
  </button>
</nav>

<div class="mobile-menu" id="mobileMenu">
  <ul class="mobile-menu-cats">
    <li><a href="../../komercialno/" class="$active_kom">Komercialno</a></li>
    <li><a href="../../dogodki/" class="$active_dog">Dogodki</a></li>
    <li><a href="../../sport/" class="$active_spo">Šport</a></li>
    <li><a href="../../koncerti/" class="$active_kon">Koncerti</a></li>
  </ul>
  <div class="mobile-menu-socials">
$mobile_socials
  </div>
</div>

<main class="page">
  <div class="container">

    <header class="page-header">
      <p class="breadcrumb"><a href="../../">Domov</a><span class="sep">/</span><a href="../">$cat_display</a><span class="sep">/</span>$title</p>
      <h1 class="page-title">$title</h1>
    </header>

    <section class="project-hero">
      <ul class="project-hero-meta">
        <li><span class="label">Datum</span><span class="value">$date</span></li>
        <li><span class="label">Lokacija</span><span class="value">Slovenija</span></li>
        <li><span class="label">Finalnih kadrov</span><span class="value">$count</span></li>
      </ul>
      <p class="description">Fotografska zgodba projekta "$title". Meta podatke lahko urediš direktno v tem HTML-ju.</p>
    </section>

    <section class="gallery" id="gallery" aria-label="Galerija projekta">
$gallery
    </section>

    <div class="project-bottom-nav">
      <a href="../" class="btn-back">← Nazaj na vse $cat_display_lower</a>
      <p class="contact-cta">Za podobno produkcijo — <a href="mailto:hello@janursic.com">hello@janursic.com</a></p>
    </div>

  </div>

  <footer class="footer">
    <span>© 2026 Jan Uršič Photography</span>
    <span><a href="../../">Nazaj na portfolio</a></span>
  </footer>
</main>

<div class="lightbox" id="lightbox" aria-hidden="true">
  <button class="lightbox-close" id="lightboxClose" aria-label="Zapri">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M18 6L6 18M6 6l12 12"/></svg>
  </button>
  <button class="lightbox-prev" id="lightboxPrev" aria-label="Prejšnja">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M15 18l-6-6 6-6"/></svg>
  </button>
  <img class="lightbox-img" id="lightboxImg" src="" alt="">
  <button class="lightbox-next" id="lightboxNext" aria-label="Naslednja">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M9 18l6-6-6-6"/></svg>
  </button>
  <span class="lightbox-counter" id="lightboxCounter">1 / $count</span>
</div>

<script>
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  hamburger.addEventListener('click', () => {
    const open = mobileMenu.classList.toggle('open');
    hamburger.classList.toggle('open', open);
    hamburger.setAttribute('aria-expanded', open);
    document.body.style.overflow = open ? 'hidden' : '';
  });
  mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    mobileMenu.classList.remove('open');
    hamburger.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }));

  const nav = document.getElementById('nav');
  window.addEventListener('scroll', () => {
    nav.classList.toggle('solid', window.scrollY > 40);
  }, { passive: true });

  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightboxImg');
  const lightboxCounter = document.getElementById('lightboxCounter');
  const galleryItems = Array.from(document.querySelectorAll('.gallery-item'));
  let currentImg = 0;

  function updateLightbox() {
    const img = galleryItems[currentImg].querySelector('img');
    lightboxImg.src = img.dataset.full || img.src;
    lightboxImg.alt = img.alt;
    lightboxCounter.textContent = (currentImg + 1) + ' / ' + galleryItems.length;
  }
  function openLightbox(idx) {
    currentImg = idx;
    updateLightbox();
    lightbox.classList.add('open');
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }
  function closeLightbox() {
    lightbox.classList.remove('open');
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }
  function nextImg() { currentImg = (currentImg + 1) % galleryItems.length; updateLightbox(); }
  function prevImg() { currentImg = (currentImg - 1 + galleryItems.length) % galleryItems.length; updateLightbox(); }

  galleryItems.forEach((item, i) => item.addEventListener('click', () => openLightbox(i)));
  document.getElementById('lightboxClose').addEventListener('click', closeLightbox);
  document.getElementById('lightboxPrev').addEventListener('click', (e) => { e.stopPropagation(); prevImg(); });
  document.getElementById('lightboxNext').addEventListener('click', (e) => { e.stopPropagation(); nextImg(); });
  lightbox.addEventListener('click', (e) => { if (e.target === lightbox || e.target === lightboxImg) closeLightbox(); });
  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('open')) return;
    if (e.key === 'Escape') closeLightbox();
    else if (e.key === 'ArrowRight') nextImg();
    else if (e.key === 'ArrowLeft') prevImg();
  });
</script>

</body>
</html>
''')

# ═══════════════════════════════════════════════════════════════════
# HTML TEMPLATE — kategorijska stran (karte)
# ═══════════════════════════════════════════════════════════════════

CATEGORY_TEMPLATE = Template(r'''<!DOCTYPE html>
<html lang="sl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="$cat_display — projekti Jana Uršiča.">
<title>$cat_display — Jan Uršič Photography</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../style.css">
</head>
<body>

<nav class="nav" id="nav">
  <a href="../" class="logo">
    <span class="logo-name">Jan Uršič</span>
    <span class="logo-tag">Photography</span>
  </a>

  <ul class="nav-cats" aria-label="Kategorije">
    <li><a href="../komercialno/" class="cat-pill $active_kom">Komercialno</a></li>
    <li><a href="../dogodki/" class="cat-pill $active_dog">Dogodki</a></li>
    <li><a href="../sport/" class="cat-pill $active_spo">Šport</a></li>
    <li><a href="../koncerti/" class="cat-pill $active_kon">Koncerti</a></li>
  </ul>

  <ul class="nav-socials" aria-label="Družbena omrežja">
$nav_socials
  </ul>

  <button class="hamburger" id="hamburger" aria-label="Meni" aria-expanded="false">
    <span></span><span></span><span></span>
  </button>
</nav>

<div class="mobile-menu" id="mobileMenu">
  <ul class="mobile-menu-cats">
    <li><a href="../komercialno/" class="$active_kom">Komercialno</a></li>
    <li><a href="../dogodki/" class="$active_dog">Dogodki</a></li>
    <li><a href="../sport/" class="$active_spo">Šport</a></li>
    <li><a href="../koncerti/" class="$active_kon">Koncerti</a></li>
  </ul>
  <div class="mobile-menu-socials">
$mobile_socials
  </div>
</div>

<main class="page">
  <div class="container">

    <header class="page-header">
      <p class="breadcrumb"><a href="../">Domov</a><span class="sep">/</span>$cat_display</p>
      <h1 class="page-title">$cat_display</h1>
      <p class="page-subtitle">$cat_subtitle</p>
    </header>

    <section class="projects" aria-label="Projekti — $cat_display_lower">

$cards

    </section>

  </div>

  <footer class="footer">
    <span>© 2026 Jan Uršič Photography</span>
    <span><a href="../">Nazaj na portfolio</a></span>
  </footer>
</main>

<script>
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  hamburger.addEventListener('click', () => {
    const open = mobileMenu.classList.toggle('open');
    hamburger.classList.toggle('open', open);
    hamburger.setAttribute('aria-expanded', open);
    document.body.style.overflow = open ? 'hidden' : '';
  });
  mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    mobileMenu.classList.remove('open');
    hamburger.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }));

  const nav = document.getElementById('nav');
  window.addEventListener('scroll', () => {
    nav.classList.toggle('solid', window.scrollY > 40);
  }, { passive: true });

  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in-view'); obs.unobserve(e.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
  document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
</script>

</body>
</html>
''')

# ═══════════════════════════════════════════════════════════════════
# POMOŽNE FUNKCIJE
# ═══════════════════════════════════════════════════════════════════

def c(color_code, s):
    """Barvni print (ANSI)."""
    return f"\033[{color_code}m{s}\033[0m"
BOLD = lambda s: c("1", s)
DIM  = lambda s: c("2", s)
GREEN = lambda s: c("32", s)
YELLOW = lambda s: c("33", s)
RED = lambda s: c("31", s)
CYAN = lambda s: c("36", s)

def slugify(text: str) -> str:
    """URL-friendly slug: 'Naj Športnik' → 'naj-sportnik'."""
    trans = str.maketrans({
        "č": "c", "š": "s", "ž": "z", "ć": "c", "đ": "d",
        "Č": "c", "Š": "s", "Ž": "z", "Ć": "c", "Đ": "d",
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
    })
    text = text.translate(trans).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def natural_key(name: str):
    """Natural sort key: IMG-2 before IMG-10."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]

def list_photos(dir_path: Path):
    """Vrne seznam fotk v mapi, po naravnem vrstnem redu."""
    if not dir_path.is_dir():
        return []
    photos = [f for f in dir_path.iterdir() if f.is_file() and f.suffix in IMG_EXTS]
    photos.sort(key=lambda x: natural_key(x.name))
    return photos

def resize_or_copy(src: Path, dst: Path, max_width: int = RESIZE_MAX_WIDTH, max_retries: int = 4):
    """Če je izvorna > 800KB, resize + recompress. Sicer samo copy.
    Ima retry logic za macOS Spotlight/mount deadlock napake."""
    import time
    size = src.stat().st_size
    last_err = None
    for attempt in range(max_retries):
        try:
            if size > COMPRESS_THRESHOLD:
                subprocess.run([
                    "sips",
                    "-Z", str(max_width),
                    "-s", "formatOptions", str(JPEG_QUALITY),
                    str(src),
                    "--out", str(dst),
                ], check=True, capture_output=True)
            else:
                shutil.copy2(src, dst)
            # Verify destination has reasonable size
            if dst.exists() and dst.stat().st_size > 1000:
                return
            last_err = "output file empty or missing"
        except (subprocess.CalledProcessError, OSError) as e:
            last_err = str(e)
        # Retry with backoff
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"resize_or_copy failed after {max_retries} tries: {last_err}")

def find_hero_dir(cat_src: Path):
    """HERO ali 'HERO ' (s presledkom)."""
    if not cat_src.is_dir():
        return None
    for item in cat_src.iterdir():
        if item.is_dir() and item.name.strip().upper() == "HERO":
            return item
    return None

def extract_title_from_html(html_path: Path) -> str | None:
    """Prebere <h1 class="page-title">...</h1> iz obstoječega HTML-ja."""
    if not html_path.is_file():
        return None
    try:
        content = html_path.read_text(encoding="utf-8")
        m = re.search(r'<h1 class="page-title">([^<]+)</h1>', content)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return None

def build_gallery_html(count: int, title: str) -> str:
    lines = []
    for i in range(1, count + 1):
        pad = f"{i:02d}"
        lines.append(
            f'      <div class="gallery-item"><img src="photos/{pad}.jpg" '
            f'data-full="photos/{pad}.jpg" alt="{title} — kader {pad}" loading="lazy"></div>'
        )
    return "\n".join(lines)

def active_flags(current_slug: str):
    """Vrne dict za $active_kom/dog/spo/kon."""
    return {
        "active_kom": "active" if current_slug == "komercialno" else "",
        "active_dog": "active" if current_slug == "dogodki" else "",
        "active_spo": "active" if current_slug == "sport" else "",
        "active_kon": "active" if current_slug == "koncerti" else "",
    }

# ═══════════════════════════════════════════════════════════════════
# GLAVNA LOGIKA
# ═══════════════════════════════════════════════════════════════════

def process_hero(cat_upper: str, cat_slug: str) -> str | None:
    cat_src = SRC / cat_upper
    hero_dir = find_hero_dir(cat_src)
    if not hero_dir:
        return None
    photos = list_photos(hero_dir)
    if not photos:
        return None
    dst = DST / "images" / "hero" / f"{cat_slug}.jpg"
    dst.parent.mkdir(parents=True, exist_ok=True)
    resize_or_copy(photos[0], dst, max_width=HERO_MAX_WIDTH)
    return f"{dst.stat().st_size // 1024} KB"

def process_project(cat_upper: str, cat_slug: str, cat_display: str, project_src: Path):
    """
    Obdela en projekt. Vrne (slug, title, photo_count, is_new).
    is_new = True če je HTML na novo generiran; False če je HTML že obstajal.
    """
    project_name = project_src.name.strip()  # očisti leading/trailing whitespace
    slug = slugify(project_name)
    project_dst = DST / cat_slug / slug
    photos_dst = project_dst / "photos"
    photos_dst.mkdir(parents=True, exist_ok=True)

    # 1) Fotke
    photos = list_photos(project_src)
    # Če user posebej označi cover.jpg (v Desktop mapi), ga izloči iz galerije
    custom_cover = None
    filtered = []
    for p in photos:
        if p.name.lower() == "cover.jpg":
            custom_cover = p
        else:
            filtered.append(p)
    photos = filtered

    for i, src_file in enumerate(photos, start=1):
        pad = f"{i:02d}"
        dst_file = photos_dst / f"{pad}.jpg"
        try:
            resize_or_copy(src_file, dst_file)
        except subprocess.CalledProcessError as e:
            print(f"      {RED('⚠')} {src_file.name}: {e.stderr.decode(errors='replace')[:80]}")

    # 2) Cover
    cover_dst = photos_dst / "cover.jpg"
    if custom_cover:
        try:
            resize_or_copy(custom_cover, cover_dst)
        except subprocess.CalledProcessError:
            pass
    else:
        first = photos_dst / "01.jpg"
        if first.exists():
            shutil.copy2(first, cover_dst)

    # 3) Naslov: preberi iz obstoječega HTML-ja ali uporabi ime mape
    project_html = project_dst / "index.html"
    existing_title = extract_title_from_html(project_html)
    title = existing_title if existing_title else project_name

    # 4) Če HTML še ne obstaja → generiraj
    is_new = not project_html.exists()
    if is_new:
        count = len(photos)
        tpl_data = {
            "title": title,
            "cat_slug": cat_slug,
            "cat_display": cat_display,
            "cat_display_lower": cat_display.lower(),
            "count": count,
            "date": datetime.now().strftime("%Y"),
            "gallery": build_gallery_html(count, title),
            "nav_socials": make_nav_socials(),
            "mobile_socials": make_mobile_socials(),
        }
        tpl_data.update(active_flags(cat_slug))
        html = PROJECT_TEMPLATE.substitute(tpl_data)
        project_html.write_text(html, encoding="utf-8")

    return slug, title, len(photos), is_new

def regenerate_category(cat_upper: str, cat_slug: str, cat_display: str, cat_subtitle: str, projects: list):
    """Regenerira /category/index.html z vsemi karticami."""
    if not projects:
        return

    cards = []
    for slug, title, count in projects:
        card = f'''      <a href="{slug}/" class="project-card reveal">
        <div class="project-cover">
          <img src="{slug}/photos/cover.jpg" alt="{title}" loading="lazy">
        </div>
        <div class="project-info">
          <h2 class="project-title">{title}</h2>
          <p class="project-meta">{count} kadrov</p>
        </div>
      </a>'''
        cards.append(card)

    tpl_data = {
        "cat_slug": cat_slug,
        "cat_display": cat_display,
        "cat_display_lower": cat_display.lower(),
        "cat_subtitle": cat_subtitle,
        "cards": "\n\n".join(cards),
        "nav_socials": make_nav_socials(),
        "mobile_socials": make_mobile_socials(),
    }
    tpl_data.update(active_flags(cat_slug))
    html = CATEGORY_TEMPLATE.substitute(tpl_data)

    dst = DST / cat_slug / "index.html"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(html, encoding="utf-8")

def git_sync() -> bool:
    """git add -A + commit + push. Vrne True če je bil push izveden."""
    os.chdir(DST)
    # Počisti lock fajle
    for lock in [".git/HEAD.lock", ".git/index.lock"]:
        try:
            (DST / lock).unlink()
        except FileNotFoundError:
            pass
    # Preveri, ali so kake spremembe
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status.stdout.strip():
        print(f"\n{DIM('  ℹ  Ni sprememb za pushati.')}")
        return False
    # Commit
    subprocess.run(["git", "add", "-A"], check=True)
    msg = f"Sinhronizacija {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    subprocess.run(["git", "commit", "-m", msg], check=True)
    # Push
    try:
        subprocess.run(["git", "push", "origin", "main"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n{RED('  ✗ git push spodletel:')} {e}")
        print(f"{YELLOW('  → Odpri GitHub Desktop in klikni ')}{BOLD('Push')}{YELLOW(', da nastaviš credentiale.')}")
        return False

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    print()
    print(BOLD(CYAN("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")))
    print(BOLD(CYAN(f"  SINHRONIZACIJA — {datetime.now().strftime('%d.%m.%Y %H:%M')}")))
    print(BOLD(CYAN("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")))
    print()
    print(f"  {DIM('Vir:')}  {SRC}")
    print(f"  {DIM('Cilj:')} {DST}")
    print()

    if not SRC.is_dir():
        print(RED(f"  ✗ Ni mape {SRC}"))
        sys.exit(1)
    if not DST.is_dir():
        print(RED(f"  ✗ Ni mape {DST}"))
        sys.exit(1)

    total_photos = 0
    total_new = 0

    for cat_upper, (cat_slug, cat_display, cat_subtitle) in CATEGORIES.items():
        cat_src = SRC / cat_upper
        if not cat_src.is_dir():
            continue

        print(BOLD(f"📂 {cat_upper}"))

        # HERO
        hero_size = process_hero(cat_upper, cat_slug)
        if hero_size:
            print(f"  {GREEN('✓')} hero → images/hero/{cat_slug}.jpg  {DIM('(' + hero_size + ')')}")

        # Projekti
        project_dirs = sorted(
            [d for d in cat_src.iterdir() if d.is_dir() and d.name.strip().upper() != "HERO"],
            key=lambda x: natural_key(x.name.strip())
        )
        projects_info = []
        for proj_src in project_dirs:
            slug, title, count, is_new = process_project(cat_upper, cat_slug, cat_display, proj_src)
            projects_info.append((slug, title, count))
            total_photos += count
            marker = GREEN("★ NEW") if is_new else GREEN("✓")
            if is_new: total_new += 1
            print(f"  {marker} {title}  {DIM(f'({count} fotk → {slug}/)')}")

        # Regeneriraj kategorijsko stran
        if projects_info:
            regenerate_category(cat_upper, cat_slug, cat_display, cat_subtitle, projects_info)
            print(f"  {GREEN('✓')} regeneriral {cat_slug}/index.html  {DIM(f'({len(projects_info)} karticic)')}")

        print()

    # Povzetek
    print(BOLD(f"  ∑ {total_photos} fotk skupaj, {total_new} novih projektnih strani"))
    print()

    # Git push
    print(BOLD("🚀 Objavljam na GitHub..."))
    pushed = git_sync()
    print()

    if pushed:
        print(BOLD(GREEN("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")))
        print(BOLD(GREEN("  ✅ OBJAVLJENO!")))
        print(BOLD(GREEN("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")))
        print()
        print(f"  🌐 {CYAN('https://janursic.github.io/portfolio/')}")
        print(f"  {DIM('  Počakaj 1–2 min, da se GitHub Pages redeploya.')}")
    else:
        print(BOLD(YELLOW("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")))
        print(BOLD(YELLOW("  ⚠  Datoteke posodobljene lokalno, PUSH pa je spodletel.")))
        print(BOLD(YELLOW("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")))
        print()
        print(f"  {DIM('Odpri GitHub Desktop → izberi PORTFOLIO repo → klikni Push.')}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW('⚠  Prekinjeno.')}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED('✗ Napaka:')} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
