# NAIF report Quarto format

This Quarto extension exposes the NAIF Typst report template as the custom format
`naif-report-typst`.

## Use

```yaml
format:
  naif-report-typst:
    toc: true
    number-sections: true
```

Common report metadata:

- `title`
- `subtitle`
- `authors`
- `date`
- `report-version`
- `abstract`
- `keywords`
- `doc-category`
- `compact-mode`
- `logo-path`

Render reports with the repository-managed Quarto command:

```bash
uv run quarto render path/to/report.qmd
```
