# Fotografski portfolio – Arhitektura strani
## Home = single-viewport cover (no scroll)

---

## Spremenjen koncept

Stran ni klasičen scrollable landing page. Home (`/`) je **statična cover stran** — ena slika čez cel ekran, brez možnosti scrollanja. Vsa vsebina živi na **podstraneh**, ki se odpirajo iz menija.

To je drznejša, bolj galerijska postavitev. Deluje, ker:
- Slika dobi 100% pozornosti — ni "above the fold" stresa
- Stranke se same odločijo, kaj jih zanima (klik kategorija)
- Občutek je bližje umetniški razstavi kot prodajni strani

---

## Sitemap

```
/                      Home (single viewport, no scroll)
├── /sport            Šport
├── /komercialno      Komercialno
├── /dogodki          Dogodki
├── /koncerti         Koncerti
├── /avtomoto         Avtomoto
├── /about            About me
└── /contact          Contact
```

Vsaka kategorijska podstran je svoj scrollable portfolio te zvrsti.

---

## Home page – elementi (`/`)

| Pozicija | Element | Vsebina |
|----------|---------|---------|
| Full-bleed | **Hero slika** | Ena signature fotografija, fills viewport. To je tvoj "vstopni" kader. |
| Top-left | **Logo / ime** | `JAN URŠIČ`, all caps, razprto |
| Top-right | **Utility menu** | `About` · `Contact` (drobno, sekundarno) |
| Center | **Tagline** *(opcijsko)* | npr. *"Foto produkcija · Slovenija"* — drobna oznaka |
| Lower-center | **Kategorije** | `Šport` · `Komercialno` · `Dogodki` · `Koncerti` · `Avtomoto` |
| Bottom-left | **Copyright** | `© 2026 Jan Uršič` |
| Bottom-right | **Družbena omrežja** | `IG · Behance · Vimeo` |

**Vse je overlaid čez sliko.** Subtilen vertikalen gradient na sliki (tema zgoraj, tema spodaj) zagotovi berljivost teksta.

---

## Hero slika – kako jo izbrati

Ker je to edino, kar obiskovalec vidi v prvem trenutku:

- **Karakter > tehnična perfekcija.** Slika z atmosfero pretehta sliko, ki je samo "lepa".
- **Močna kompozicija.** Asimetrija, vodilne linije, prazen prostor (kjer gre tekst čez).
- **Kar reprezentativna celoto, ne nišo.** Če pokriješ 5 kategorij, naj slika ne bo tipično športna ali tipično avto. Naj bo nekaj atmosferskega, ki bi delovalo v vsaki zvrsti.
- **Razmisli o orientaciji teksta.** Logo gre top-left, kategorije bottom-center → svetlejši subjekt naj ne bo na teh območjih, drugače je tekst neberljiv.

**Bonus ideja:** če imaš tehnične vire, lahko hero slika **menja vsakih 5–10 sekund** (subtilen crossfade) — 4–5 različnih signature kadrov. Ali še bolje: ko hover-aš kategorijo, se slika spremeni v reprezentativno za tisto zvrst (športni avto pri "Avtomoto", koncert pri "Koncerti", ipd.). Premium detail.

---

## Kategorijska podstran – kako naj zgleda (`/sport`, `/komercialno`, ...)

Vsaka podstran:

1. **Top nav:** isti logo + utility (About, Contact) + povezave do drugih kategorij.
2. **Naslov kategorije** (npr. "Šport") in kratka 1-stavčna definicija (npr. *"Akcija, znoj, trenutki, ko štejejo stotinke."*).
3. **Projekti v gridu** — 4:5 ali mešani razmerji, z oznakami `[Žanr] / [Naslov]` à la Rok Mlinar.
4. **Klik na projekt** odpre ali lightbox ali svojo podstran z več slikami iz tega shootinga.
5. **Footer** identičen home-u.

Razlika od home: tu **scroll obstaja**, ker prikazuješ vse projekte zvrsti.

---

## About stran (`/about`)

- Tvoj portret + osebni copy (pogovorno, max 200 besed)
- Krajša ozadje + pristop ("kako delam")
- Bonus: timeline / "kdaj sem začel" / "kateri shooting mi je obrnil pogled"
- Klic k akciji na koncu: link na `/contact`

---

## Contact stran (`/contact`)

Minimalno:
- Velik email naslov (klikabilen, `mailto:`)
- Družbena omrežja
- Lokacija (Slovenija + ali pokrivaš tujino)
- Opcijsko: kratka forma (Ime, Email, Tip projekta, Datum, Sporočilo)
- Mikro-zaupanje: *"Odgovorim v 24 urah."*

---

## Vizualni jezik

| Element | Priporočilo |
|---------|-------------|
| **Tipografija** | Ena sans-serif (Inter, Helvetica, Söhne). 1 font za vse. |
| **Velikost na home** | Logo 18px, kategorije 14px, utility/copyright 10–11px. Vse CAPS, letter-spacing 3–4px. |
| **Barve** | Bel tekst čez sliko + subtilen črn gradient overlay. Akcent NI potreben. |
| **Hover** | Tanka bela podčrtava pod kategorijo. Ostale 4 se rahlo zatemnijo (focus efekt). |
| **Tranzicije** | 0.2s ease, ne fancy. |
| **Kurzor** | Standard. Brez custom kurzorja (preveč popularno, postaja klise). |

---

## Tehnično – kako to zgraditi

**Najpreprostejši pristop:**
- Statične HTML strani (lahko z Astro, 11ty, ali kar pure HTML/CSS)
- Slike served z CDN-a (Cloudinary, Bunny, ImageKit) z avtomatsko WebP konverzijo
- Hosting: Vercel, Netlify, Cloudflare Pages — vsi brezplačno za to skalo

**Adobe Portfolio (kot Rok Mlinar)** je tudi opcija — če nočeš sam graditi. Slabost: manj kontrole, plus generičen "Adobe Portfolio" footer.

**WordPress / Squarespace** — možno, a overkill. Statična stran je hitrejša, varnejša in cenejša.

---

## Trade-offs no-scroll home

**Plus:**
- Močan vizualen vtis
- Galerijski občutek
- Hitro nalaganje (ena slika)
- Manj odločitvene paralize za obiskovalca

**Minus:**
- SEO je manj robusten (manj teksta na home → manj keyword-ov)
- Ne moreš v hero povedati "kdo si, kaj delaš" za nove obiskovalce, ki te ne poznajo
- Ni "social proof" na prvem stiku
- Nekateri obiskovalci pričakujejo scroll in se zmedejo

**Mitigation:**
- Močan SEO daj na podstrani (`/about`, `/sport` itd.) z dolgimi opisi
- Tagline pod logom lahko prevzame vlogo "kdo si v eni vrstici"
- Stranke, ki pridejo iz priporočila ali Instagrama, te tako ali tako že poznajo — to je tvoj target

---

## Naslednji koraki

1. **Odpri `wireframe.html`** v brskalniku — preveri, kako deluje na desktopu in mobile-u (zmanjšaj okno)
2. **Izberi hero sliko** — eno fotografijo, ki je tvoja. Tista, ki bi jo postavil na razstavo.
3. **Razmisli o tagline-u** — *"Foto produkcija · Slovenija"* je placeholder. Lahko je tudi:
   - "Photo & Visual Storytelling"
   - "Photographer · Slovenia"
   - Brez taglina (še bolj minimalno)
4. **Določi vrstni red kategorij** — trenutno so po abecedi. Lahko jih razvrstiš po prioriteti (npr. tisto, kar prinese največ dela, prvo).
5. **Pošlji nazaj** in povem, ali nadaljujemo s kategorijsko podstranjo, About copyem ali pretvorbo v actual code.
