# Tomáš Zikmund · Digital Creator

Personal website for Tomáš Zikmund. Static HTML, CSS and JS with no build step.

## Run locally

```bash
cd tomas-zikmund
python3 -m http.server 8000
# open http://localhost:8000
```

Any static host works (GitHub Pages, Netlify, Vercel, Cloudflare Pages). Everything is self-hosted: fonts, GSAP, Lenis and images live in `assets/`.

## Before going live, replace

| What | Where |
| --- | --- |
| Instagram / TikTok / YouTube profile URLs | `index.html`, Channels section and footer (currently platform home pages) |
| Email `hello@tomaszikmund.cz` | `index.html`, Contact section (`href`, `data-email`, visible text) |
| More photos | `assets/img/`. The site currently uses one supplied photo, edited and cropped four ways |

## Design

- **Palette:** black `#0A0A0B`, grays `#141416` / `#8B8D94` / `#DCDDE0`, jersey red `#E3261C` (button fill `#C4180E`). All text pairings pass WCAG AA.
- **Type:** Archivo variable (condensed width for display, normal for body) and JetBrains Mono for labels.
- **Photo treatment:** grayscale with the red of the kit kept in colour.
- **Motion:** GSAP + ScrollTrigger with Lenis smooth scroll. Hero intro, word-by-word headings, a manifesto that lights up as you read, a pinned horizontal run through the three formats, and period clocks that count down in the process section. Everything turns off under `prefers-reduced-motion`, and the page stays fully readable without JavaScript.

## Credits

Brand icons: Simple Icons (CC0). Fonts: Archivo and JetBrains Mono (SIL OFL) via Fontsource. Motion: GSAP, Lenis.
