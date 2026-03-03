# NAIF

[![DOI](https://zenodo.org/badge/GITHUB_REPO_ID.svg)](https://zenodo.org/badge/latestdoi/ZENODO_RECORD)

National Approach for Interoperable repositories and Findable research results (NAIF) is a project
initiated and funded by eight Swiss Higher Education Institutions and co-funded by
swissuniversities.

- Website: https://eth-library.github.io/naif/
- Repository: https://github.com/eth-library/naif

## About

This repository contains the source for the NAIF project website, built with
[Quarto](https://quarto.org/) (`.qmd` + `_quarto.yml`).

## Getting started

### Requirements

- Quarto
- Node.js (for formatting Markdown with Prettier)
- Python 3.14
- uv

### Install

```bash
npm install
uv sync
```

### Format and build

```bash
npm run format
npm run quarto:render
```

### Preview locally

```bash
npm run quarto:preview
```

### Export all pages/posts/events to one DOCX (including drafts)

This repository includes a dedicated Quarto profile in `_quarto-docx.yml`.

```bash
npm run quarto:docx
```

Output file:

- `_site-docx/NAIF-Website-Export.docx`

### Validate before opening a PR

Run all checks (formatting, linting, type checking, tests, render) in one go:

```bash
npm run validate
```

### npm scripts reference

#### Quarto

| Script                   | Command                               | Description                        |
| ------------------------ | ------------------------------------- | ---------------------------------- |
| `npm run quarto:render`  | `uv run quarto render`                | Render the full site into `_site/` |
| `npm run quarto:preview` | `uv run quarto preview`               | Local dev server with live reload  |
| `npm run quarto:docx`    | `uv run quarto render --profile docx` | Export site to a single DOCX       |

#### Code quality

| Script              | Command                     | Description                    |
| ------------------- | --------------------------- | ------------------------------ |
| `npm run check`     | `prettier --check .`        | Check Markdown/YAML formatting |
| `npm run format`    | `prettier --write .`        | Auto-format Markdown/YAML      |
| `npm run lint`      | `uv run ruff check .`       | Lint Python code               |
| `npm run lint:fix`  | `uv run ruff check --fix .` | Auto-fix Python lint issues    |
| `npm run typecheck` | `uv run ty check`           | Python type checking           |

#### Testing

| Script             | Command               | Description                    |
| ------------------ | --------------------- | ------------------------------ |
| `npm run test`     | `uv run pytest`       | Run Python tests               |
| `npm run test:cov` | `uv run pytest --cov` | Run tests with coverage report |

#### Project maintenance

| Script                          | Command                                                        | Description                                             |
| ------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------- |
| `npm run sync`                  | `uv sync`                                                      | Install/sync Python dependencies                        |
| `npm run validate`              | check + lint + typecheck + test + render + rendered-link-check | Full pre-PR validation                                  |
| `npm run deploy`                | render + jampack + publish                                     | Build, optimise, and deploy to GitHub Pages             |
| `npm run changelog`             | `git-cliff`                                                    | Generate CHANGELOG from commits                         |
| `npm run commit`                | `cz`                                                           | Commitizen guided commit                                |
| `npm run lychee-check`          | `lychee`                                                       | Check for broken links in source `.md` and `.qmd` files |
| `npm run lychee-check:rendered` | `lychee --offline`                                             | Check internal links in rendered `_site/**/*.html`      |

#### Screenshots

| Script                                | Command                             | Description                                         |
| ------------------------------------- | ----------------------------------- | --------------------------------------------------- |
| `npm run screenshot:install-browsers` | install Playwright Chromium         | One-time browser setup                              |
| `npm run screenshot:clean`            | `node scripts/screenshot-clean.mjs` | Capture a clean screenshot (removes cookie banners) |

Positional arguments: `<url>` (page to capture) and `<output-file>` (path to save the image).

Options:

| Flag                 | Default    | Description                                           |
| -------------------- | ---------- | ----------------------------------------------------- |
| `--wait-ms <n>`      | `6000`     | Wait time after page load (ms)                        |
| `--timeout-ms <n>`   | `45000`    | Navigation timeout (ms)                               |
| `--viewport <WxH>`   | `1600x900` | Viewport size                                         |
| `--hide <sel1,sel2>` | —          | Extra CSS selectors to hide before capture            |
| `--full-page`        | off        | Capture full scrollable page instead of 16:9 viewport |
| `--help`             | —          | Print usage info                                      |

Examples:

```bash
# Basic screenshot
npm run screenshot:clean -- "https://example.org" "posts/<entry>/images/shot.png"

# Custom viewport and hide a site-specific overlay
npm run screenshot:clean -- "https://example.org" "posts/<entry>/images/shot.png" \
  --viewport 1920x1080 --hide ".ad-banner,#popup"

# Full-page capture with longer wait
npm run screenshot:clean -- "https://example.org" "posts/<entry>/images/shot.png" \
  --full-page --wait-ms 10000
```

## Content workflow

- Blog entries live in `posts/<yyyy-mm-dd>-<slug>/index.qmd`.
- Every blog entry has its own folder and keeps assets (images) in a local `images/` subfolder.
- Posts and event pages use British English by default.
- Reposts must include a clear source note and link back to the original publication.
- Use front-matter `description` as the teaser shown in the Quarto title block.

## Support

- Bug reports / requests: https://github.com/eth-library/naif/issues
- Security issues: see `SECURITY.md`

## Contributing

See `CONTRIBUTING.md`.

## Citation

If you reuse this repository's code or content, please cite it using `CITATION.cff`.

## License

- Code: GNU AGPLv3, see `LICENSE-AGPL.md`
- Content (text and media unless noted otherwise): CC BY 4.0, see `LICENSE-CCBY.md`
