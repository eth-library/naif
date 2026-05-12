# Contributing

Thanks for considering a contribution.

## Ground rules

- Please discuss significant changes via an issue first.
- Be respectful and follow `CODE_OF_CONDUCT.md`.

## Pull request process

1. Create a branch.
2. Make your changes.
3. Run:

   ```bash
    npm install
    uv sync
    npm run validate
   ```

4. Open a pull request.

For tagged releases, also run `npm run release:prepare -- --tag vX.Y.Z` and commit the generated
archive before publishing the release so Zenodo captures the rendered site snapshot.

## Quarto builds

Use the npm scripts or call Quarto through `uv run`; do not call `quarto` directly.

| Task                  | npm script            | Direct Quarto command                 | Configuration                                |
| --------------------- | --------------------- | ------------------------------------- | -------------------------------------------- |
| Render the website    | `npm run render`      | `uv run quarto render`                | `_quarto.yml`                                |
| Preview the website   | `npm run preview`     | `uv run quarto preview`               | `_quarto.yml`                                |
| Render with fork URLs | `npm run render:fork` | `uv run quarto render --profile fork` | `_quarto.yml` + untracked `_quarto-fork.yml` |
| Export DOCX           | `npm run docx`        | `uv run quarto render --profile docx` | `_quarto.yml` + `_quarto-docx.yml`           |
| Render poster PDFs    | `npm run pdf`         | `uv run quarto render --profile pdf`  | `_quarto.yml` + `_quarto-pdf.yml`            |

## Content contributions

- Blog entries must follow the folder-per-entry structure described in `AGENTS.md`.
- British English is preferred for posts and event pages, except reposts where source wording may be
  preserved.
- When setting Quarto language metadata, use `lang: en-UK`.
- Use sentence case for page titles and section headings by default.
- Preserve official branded styling for proper nouns, acronyms, and formal event names.
- Keep images local to the entry folder and include alt text, caption, and rights attribution.
- Posts and events inherit a fallback card image via `posts/_metadata.yml` and
  `events/_metadata.yml`; set a page-level `image:` in each entry to override this default.
- Post and event pages show the front-matter `image:` near the page title via a Quarto template
  partial.
- Use `image-alt:` for accessibility; if omitted, the page title is used as fallback alt text.
- Use `image-caption:` for the on-page image caption, including source and rights attribution;
  directory metadata provides a generic fallback caption.
- To avoid duplicate page images, set `show-page-image: false` in front matter when you add your own
  manual image(s) in the body content.
