# RDJ-Portfolio

An animated portfolio webpage for **Raj Patel ("RDJ")** — résumé, portrait and roadmap in one page, built as part of [`code-with-RDJ`](https://github.com/raj-famu-dev/code-with-RDJ).

## What's inside

- `index.html` — the portfolio page (Work, About, Résumé, Roadmap, Contact)
- `css/style.css` — design system: Clash Display / Satoshi / JetBrains Mono on a warm charcoal palette with a FAMU-heritage amber accent
- `js/app.js` — all animation systems
- `assets/rdj-portrait.png` — stylized duotone portrait illustration (replace with a real photo anytime — keep the same filename)
- `assets/favicon.svg` — monogram

## The animations

| Effect | Where |
|---|---|
| Terminal boot preloader | Page load |
| Interactive particle constellation (mouse-reactive) | Hero |
| Per-letter name reveal | Hero |
| Scramble-text role rotator | Hero |
| Infinite skills marquee (pauses on hover) | Below hero |
| Opacity scroll reveals (no layout shift) | Every section |
| Count-up statistics | About |
| 3D tilt rows | Work ledger |
| Magnetic buttons | Hero + Contact |
| Scroll-scrubbed roadmap timeline | Roadmap |
| Custom cursor, scroll progress bar, hide-on-scroll nav | Global |

All motion respects `prefers-reduced-motion`.

## Run it

Open `index.html` directly, or serve the folder:

```bash
cd RDJ-Portfolio
python3 -m http.server 8080
```

It is also a GitHub Pages candidate — enable Pages for this repo (main branch) and it will be served at:

```
https://raj-famu-dev.github.io/code-with-RDJ/RDJ-Portfolio/
```

## Integrity

Content on the page is drawn from the repository's own README — stats, project statuses and the AI-assistance disclosure are stated there honestly, and this page keeps that standard. Built with AI assistance (Claude), in the same spirit as the rest of the lab.

## License

MIT © 2026 Raj Patel (RDJ)
