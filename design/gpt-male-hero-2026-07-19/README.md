# Autonome — male hero redesign

This folder is a complete, self-contained website package. It applies the supplied premium black-and-white visual treatment, replaces the female hero with an original male portrait, and retains the Autonome site’s wording and factual boundaries.

## Open it

Open `index.html` directly in a browser. No build command, package manager, framework, webfont, CDN or remote image is required.

For local development, serve the folder with any static server. Example:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Source of truth

1. `index.html` is the source of truth for layout, responsive behaviour, links and final visible copy.
2. `COPY_LOCK.md` is the copy and claims lock.
3. `CLAUDE_IMPLEMENTATION_PROMPT.md` is the handoff instruction for Claude.
4. The `assets` folder contains every required graphic.
5. `preview-desktop-hero.png`, `preview-desktop-full.png`, `preview-mobile-hero.png` and `preview-mobile-full.png` show the intended result.

## Design boundaries

- Keep the male portrait, upward gaze, close crop, black canvas and blue rim light.
- Keep the restrained premium product-design language: black, warm white, fine borders, large typography and quiet motion.
- Do not reintroduce the female face.
- Do not use Apple branding or imply Apple affiliation. The laptop carries the Autonome mark.
- Do not add metrics, customers, endorsements, deployment claims or working instances. Max is the only working instance named by the page; the other three examples remain explicitly illustrative.
- Do not rewrite the copy into generic AI-company language.

## Technical notes

- Responsive breakpoints: 1160, 900 and 620 pixels.
- Mobile navigation, escape-to-close, scroll reveal and active navigation are included in vanilla JavaScript.
- Reduced-motion preferences are respected.
- Local asset paths are relative, so the folder can be deployed unchanged at any static host.
- Browser checks were run at 390, 768, 1024 and 1440 pixels with no horizontal overflow or JavaScript errors.
