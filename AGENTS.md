# AGENTS.md

## Purpose

This repository contains the NAIF project website.

- Website: https://eth-library.github.io/naif/
- Repository: https://github.com/eth-library/naif

## Tech

- Quarto website (`.qmd` + `_quarto.yml`)
- Output is rendered into `_site/` (do not edit `_site/` manually)

## Required commands (always run)

**Always use `uv run` to invoke Quarto** (e.g. `uv run quarto render`, `uv run quarto preview`).
Never call `quarto` directly — the project venv managed by `uv` provides the correct Python
environment with Jupyter and all dependencies.

Before opening a PR:

```bash
npm run format
uv run quarto render
```

## Python tooling

- Python version: `3.14` (see `.python-version`)
- Environment manager: `uv`
- Quarto execution support: `jupyter`, `ipykernel`
- Dev tooling: `ruff`, `ty`, `pytest`, `pytest-cov`

## Agent workflow

- Treat this repository as a Quarto website project with lightweight Python support.
- Use `uv`-managed tooling only; keep changes compatible with Python 3.14 and Quarto/Jupyter.
- Prefer lightweight dependencies and avoid unnecessary system-level runtime requirements.

### Content defaults

- When generating or editing blog posts and event entries, use British English spelling and style.
- Keep site and page language metadata aligned with that policy by using the language code `en-UK`.
- Exception: reposts may retain original wording when needed for faithful attribution.

### Available tooling

#### Core development

- uv
- ruff
- ty
- pytest
- pytest-cov

#### Quarto execution

- jupyter
- ipykernel

#### Mapping/visualisation

- folium

### Coding guidelines

- **Type safety:** use type hints throughout all code.
- **Data structure:** use Pydantic models or Python dataclasses for structured data.
- **Documentation:** include docstrings for non-trivial Python functions.
- **Testing:** add or update tests for non-trivial logic.
- **Paradigm:** prefer functional programming patterns over object-oriented programming.

Common commands:

```bash
uv sync
uv run ruff check .
uv run ty check
uv run pytest
uv run quarto render
```

## Blog content model

### Folder structure (required)

- Blog posts: `posts/<yyyy-mm-dd>-<slug>/index.qmd`
- Events: `events/<yyyy-mm-dd>-<slug>/index.qmd`
- Post assets live next to the entry: `posts/<entry>/images/*`
- Event assets live next to the entry: `events/<entry>/images/*`

### Front matter (recommended minimum)

- `title`
- `date`
- `author` (for events: organizer)
- `author-title` (for events: set to `Organizer`)
- `description` (teaser)
- `categories`:
  - Blog posts: exactly one of: `Track 1`, `Track 2`, `Track 3`, `Track 4`, `General`
  - Events: exactly one of `Organised by NAIF`, `Participation by NAIF`, `Related Topic`
- `tags`: exactly 3 tags
- `proofread`: `true` or `false`
- `image`: a local image path (used for listing cards)

### Language and spelling

- Blog posts and event pages must use British English.
- Use `en-UK` in Quarto language metadata when setting or updating page or site language.
- Exception: reposts may preserve source-language wording where necessary.

### Cross-linking posts and events

- Use Quarto front matter `other-links` to connect related pages.
- Add links in both directions whenever there is a clear relation (event page <-> post recap).
- Prefer relative links:
  - from posts: `../../events/<yyyy-mm-dd-slug>/`
  - from events: `../../posts/<yyyy-mm-dd-slug>/`

### Author names and titles

- Keep author names and mentions consistent across pages.
- Use academic titles (`Dr`, `Prof`, etc.) consistently for people where the title is known.
- Do not mix titled and untitled variants of the same person across pages.

### Post structure and references

- Use the front matter `description` as the post teaser shown in the Quarto title block.
- Use `## References` only when references are generated with Pandoc citeproc (`bibliography` +
  citation keys such as `[@key]`).
- If citeproc is not used, include links inline in the text or in a `## Sources` /
  `## Further reading` section.

### Images

- Use 1-3 high-resolution images where possible.
- The page hero image is rendered from front matter (Quarto title-block partial). For posts and
  events, set:
  - `image` (local path)
  - `image-alt` (descriptive alt text)
  - `image-caption` (caption including rights attribution, and source URL where relevant)
- If you add manual inline images in the body, also provide alt text and a caption with rights
  attribution.
- For screenshot-based inline figures, include the source URL in the figure caption (`fig-cap`)
  where possible. If that is not possible, keep the source line commented out in the page source.
- If no suitable image is available on first try, add a screenshot of the relevant source page.
- Use Playwright via `npx` for screenshots (do not rely on Python Playwright in this repo).
- Install screenshot tooling once per machine:

```bash
npm install
npm run screenshot:install-browsers
```

- Screenshot outputs should be 16:9 by default.
- Use the reusable clean-capture command to remove common cookie banners and overlays:

```bash
npm run screenshot:clean -- "https://example.org" "posts/<entry>/images/source-screenshot.png"
```

- Add custom selectors when a site-specific overlay still appears:

```bash
npm run screenshot:clean -- "https://example.org" "posts/<entry>/images/source-screenshot.png" --hide ".custom-overlay,#cookie-panel"
```

- Keep Python Playwright as a last-resort fallback only.
- Legacy one-off command (kept for reference):

```bash
npx -y playwright@1.52.0 screenshot --wait-for-timeout 6000 --full-page "https://example.org" "posts/<entry>/images/source-screenshot.png"
```

### Reposts

- Reposts are allowed only with permission.
- Add a visible note near the top linking back to the original URL.

### Events: registration links

- Future events: keep `Registration` and `Event page` as clickable links.
- Past events: disable registration links (render as plain text and strikethrough) and add a short
  note that the event already took place.

## Drafts (work-in-progress content)

- Use `draft: true` in the front matter for work-in-progress posts/events.
- Drafts are not included in navigation, listings, search results, or the sitemap on
  `quarto render`.
- Drafts are visible when using `quarto preview` (they render with a "Draft" banner).

## Links

- Use:
  - https://eth-library.github.io/naif/
  - https://github.com/eth-library/naif

## URL aliases (required)

When pages are moved or deleted, always preserve old URLs by adding `aliases` to the destination
page.

- Quarto reference: https://quarto.org/docs/reference/formats/html.html#website
- Use the previously published sitemap (`https://eth-library.github.io/naif/sitemap.xml`) as the
  source of truth for legacy URLs.
