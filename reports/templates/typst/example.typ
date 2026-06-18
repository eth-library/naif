#import "lib.typ": naif-report, naif-callout, naif-stat

#show: naif-report.with(
  doc-category: [NAIF report],
  title: [Repository metadata quality in Switzerland],
  subtitle: [A short NAIF report template example],
  authors: (
    (
      name: "NAIF team",
      affiliation: "ETH Library",
      email: "naif@library.ethz.ch",
    ),
  ),
  date: "24 April 2026",
  version: "Draft",
  abstract: [
    This example shows how to apply the reusable NAIF Typst report template. It mirrors the website typography and colour palette while keeping the document structure simple enough for project reports, briefing notes, and public deliverables.
  ],
  keywords: ("interoperability", "metadata quality", "repositories"),
  show-outline: true,
  compact-mode: false,
)

= Executive summary

NAIF improves interoperability and metadata quality across Swiss institutional repositories. This template provides a branded report layout for project deliverables that need a consistent visual identity across PDF outputs.

#naif-callout(title: [Main message])[
  Use `#show: naif-report.with(...)` once at the top of a Typst document, then write the report body with regular Typst headings, paragraphs, figures, tables, and citations.
]

== Example indicators

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 8pt,
  naif-stat([8], [Partner institutions], detail: [Project initiators and funders]),
  naif-stat([4], [Work tracks], detail: [Governance, assessment, repositories, standards]),
  naif-stat([1], [National approach], detail: [Findable research results]),
)

== Example table

#table(
  columns: (1.1fr, 2fr),
  inset: 6pt,
  [Area], [Purpose],
  [Metadata], [Improve quality, consistency, and reuse across repository records.],
  [Governance], [Coordinate decisions and responsibilities across institutions.],
  [Assessment], [Connect metadata quality with responsible research assessment.],
)

= Next steps

Replace this file with report-specific content, update the title metadata, and compile it with the Typst CLI.
