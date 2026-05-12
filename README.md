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
- Lychee (for local link checks in `npm run validate`)

### Install

```bash
npm install
uv sync
```

The Git hooks managed by `prek` are installed automatically via npm's `prepare` script.

### Format and build

```bash
npm run format
npm run render
```

### Preview locally

```bash
npm run preview
```

### Export all pages/posts/events to one DOCX (including drafts)

This repository includes a dedicated Quarto profile in `_quarto-docx.yml`.

```bash
npm run docx
# or: uv run quarto render --profile docx
```

Output file:

- `_site-docx/NAIF-Website-Export.docx`

### Render all posters to PDF

This repository includes a dedicated Quarto profile in `_quarto-pdf.yml`.

```bash
npm run pdf
# or: uv run quarto render --profile pdf
```

Poster PDFs are written next to each poster source, for example `posters/<entry>/poster.pdf`.

### Validate before opening a PR

Run all checks (formatting, linting, type checking, tests, render, rendered link checks) in one go:

```bash
npm run validate
```

If `lychee` is not available locally yet:

- macOS: `brew install lychee`
- Other platforms: see https://lychee.cli.rs/

GitHub Actions runs the same validation suite before building and deploying the site.

### Prepare a release archive for Zenodo

Create a release-ready snapshot of the rendered site and stage it for commit before tagging a
release:

```bash
npm run release:prepare -- --tag v1.0.0
```

This creates `release-artifacts/site-v1.0.0.zip` and stages it for commit. Commit the archive before
publishing the GitHub release so the tagged repository snapshot contains the rendered site that
Zenodo will archive.

### npm scripts reference

#### Quarto

| Script                 | Command                                | Description                             |
| ---------------------- | -------------------------------------- | --------------------------------------- |
| `npm run render`       | `uv run quarto render`                 | Render the full site into `_site/`      |
| `npm run render:fork`  | `uv run quarto render --profile fork`  | Render the site with fork-specific URLs |
| `npm run preview`      | `uv run quarto preview`                | Local dev server with live reload       |
| `npm run preview:fork` | `uv run quarto preview --profile fork` | Preview locally with fork-specific URLs |
| `npm run docx`         | `uv run quarto render --profile docx`  | Export site to a single DOCX            |
| `npm run pdf`          | `uv run quarto render --profile pdf`   | Render all poster sources to PDF        |
| `npm run site:build`   | `render` + `jampack`                   | Build the optimised release site        |

#### Quarto configuration files

| File                       | Used by                             | Purpose                                                       |
| -------------------------- | ----------------------------------- | ------------------------------------------------------------- |
| `_quarto.yml`              | `npm run render`, `npm run preview` | Main website configuration and shared HTML rendering settings |
| `_quarto-docx.yml`         | `npm run docx`                      | DOCX export profile for site pages, posts, and events         |
| `_quarto-pdf.yml`          | `npm run pdf`                       | PDF export profile for all poster sources under `posters/**`  |
| `_quarto-fork.yml.example` | Manual template                     | Template for local fork-specific URLs                         |
| `_quarto-fork.yml`         | `--profile fork` commands           | Untracked local fork overrides; copy from the example file    |
| `posters/**/_quarto.yml`   | Individual poster directories       | Standalone `docposter` configuration for rendering one poster |

Always invoke Quarto through `uv run`, either directly or via the npm scripts above. Quarto profiles
are selected with `--profile <name>`, which makes Quarto merge `_quarto-<name>.yml` into the base
configuration for that command.

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

| Script                          | Command                                                          | Description                                             |
| ------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------- |
| `npm run sync`                  | `uv sync`                                                        | Install/sync Python dependencies                        |
| `npm run validate`              | check + lint + typecheck + test + render + lychee-check:rendered | Full pre-PR validation                                  |
| `npm run deploy`                | site:build + publish                                             | Build, optimise, and deploy to GitHub Pages             |
| `npm run publish:fork`          | `uv run quarto publish gh-pages --no-render --profile fork`      | Publish a fork build to the fork's GitHub Pages site    |
| `npm run site:archive`          | `uv run python scripts/release_site_archive.py`                  | Create a versioned ZIP of the rendered site             |
| `npm run release:prepare`       | site:build + site:archive --stage                                | Build and stage the Zenodo-ready release archive        |
| `npm run changelog`             | `git-cliff`                                                      | Generate CHANGELOG from commits                         |
| `npm run commit`                | `cz`                                                             | Commitizen guided commit                                |
| `npm run lychee-check`          | `lychee`                                                         | Check for broken links in source `.md` and `.qmd` files |
| `npm run lychee-check:rendered` | `lychee --offline`                                               | Check internal links in rendered `_site/**/*.html`      |

Use the tracked example file `_quarto-fork.yml.example` as the template for local fork overrides.
Copy it to `_quarto-fork.yml`, keep that file untracked, and update the URLs to match your fork.

#### Fork workflow with `_quarto-fork.yml`

Quarto automatically merges `_quarto-fork.yml` into `_quarto.yml` when you run a command with
`--profile fork`. Use that local file only for fork-specific website settings:

- `site-url`: points rendered canonical links and cards at the fork preview site
- `repo-url`: points the website repo links at the fork repository
- `issue-url`: points the website issue links at the fork repository

Use this workflow when working from a fork:

1. Keep all shared project configuration in `_quarto.yml`.
2. Copy `_quarto-fork.yml.example` to `_quarto-fork.yml` and set your fork URLs there.
3. Run `npm run preview:fork` for local development with fork URLs.
4. Run `npm run render:fork` before pushing when you want to verify the full fork build.
5. Run `npm run publish:fork` when you want to publish the branch to your fork's Pages site.
6. Open the pull request against `eth-library/naif` from your fork branch.

This keeps upstream configuration clean while letting a fork publish correct preview URLs.

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
- Site and page language metadata use the code `en-UK`.
- Use sentence case for page titles and section headings by default.
- Preserve official branded styling for proper nouns, acronyms, and formal event names.
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
