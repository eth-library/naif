# NAIF Typst report template

This directory contains a reusable Typst report template package for NAIF PDFs. It follows the
website branding from `_brand.yml`, `base_colors.scss`, and `custom.scss`:

- Font family: `Barlow`, with common sans-serif fallbacks for local compilation.
- Primary colour: `#A1AB71`.
- Secondary colour: `#E8E1D0`.
- Text colour: `#181818`.
- Accent colours: `#1F3A5F` and `#162A45`.

## Use

Create a report next to the template or import it with a relative path:

```typst
#import "lib.typ": naif-report, naif-callout, naif-stat

#show: naif-report.with(
  doc-category: [NAIF report],
  title: [Repository metadata quality in Switzerland],
  subtitle: [A short report],
  authors: (
    (
      name: "NAIF team",
      affiliation: "ETH Library",
      email: "naif@library.ethz.ch",
    ),
  ),
  date: "24 April 2026",
  version: "Draft",
  abstract: [Short report summary.],
  keywords: ("interoperability", "metadata quality", "repositories"),
  show-outline: true,
  compact-mode: false,
)
```

Then write the report body with regular Typst markup.

## Package layout

- `lib.typ`: Typst package entrypoint.
- `example.typ`: starter document referenced by `typst.toml` and used for quick compilation checks.
- `typst.toml`: package metadata and template declaration.

## Options

The main template function is `naif-report`. It accepts these common options:

- `doc-category`: label shown on the title page, default `[NAIF report]`.
- `title`: report title.
- `subtitle`: optional subtitle.
- `authors`: array of dictionaries with `name`, `affiliation`, and `email`.
- `date`: report date.
- `version`: optional version or status label.
- `abstract`: optional abstract block.
- `keywords`: array of keyword strings.
- `logo`: optional Typst image, for example `image("path/to/logo.svg", width: 25mm)`.
- `show-outline`: show a contents page after the title page, default `true`.
- `compact-mode`: put the title metadata on the first content page instead of creating a separate
  title page, default `false`.
- `number-headings`: number headings, default `true`.
- `heading-numbering`: Typst heading numbering pattern, default `"1."`.
- `font-stack`: body and heading font stack, default `("Barlow", "Inter", "Arial", "Helvetica")`.
- `mono-font-stack`: monospace font stack, default `("Menlo", "DejaVu Sans Mono")`.

## Compile

Use Quarto's bundled Typst CLI in this repository:

```bash
uv run quarto typst compile reports/templates/typst/example.typ reports/templates/typst/example.pdf
```

For reports authored in Quarto, use the repository extension format `naif-report-typst`. See
`reports/templates/quarto/naif-report-example.qmd` for a starter document.

The website uses Barlow from Google Fonts, but Typst does not load web fonts from the website CSS.
Install Barlow locally before compiling if Typst reports `unknown font family: barlow`:

```bash
brew install --cask font-barlow
```

You can also override the font stack explicitly:

```typst
#import "lib.typ": naif-report, naif-barlow-font-stack

#show: naif-report.with(
  title: [Repository metadata quality in Switzerland],
  font-stack: naif-barlow-font-stack,
)
```

Compile with an explicit font path if the Barlow font files are not installed system-wide or through
Homebrew:

```bash
uv run quarto typst compile --font-path path/to/fonts reports/templates/typst/example.typ reports/templates/typst/example.pdf
```
