// Reusable Typst report template package for NAIF documents.
// Brand source: ../../../_brand.yml and ../../../base_colors.scss.

#let naif-primary = rgb("#A1AB71")
#let naif-secondary = rgb("#E8E1D0")
#let naif-dark = rgb("#181818")
#let naif-accent = rgb("#1F3A5F")
#let naif-accent-dark = rgb("#162A45")
#let naif-white = rgb("#FFFFFF")

#let naif-font-stack = ("Barlow", "Inter", "Arial", "Helvetica")
#let naif-barlow-font-stack = ("Barlow", "Inter", "Arial", "Helvetica")
#let naif-mono-font-stack = ("Menlo", "DejaVu Sans Mono")

#let _is-empty(value) = value == none or value == "" or value == []

#let _meta-line(date, version) = {
  if date != none and version != none {
    [#date | #version]
  } else if date != none {
    date
  } else if version != none {
    version
  } else {
    none
  }
}

#let _author-card(author) = {
  let name = author.at("name", default: [])
  let affiliation = author.at("affiliation", default: none)
  let email = author.at("email", default: none)

  [
    #text(weight: 700)[#name]
    #if not _is-empty(affiliation) [
      #v(2pt)
      #text(size: 9pt)[#affiliation]
    ]
    #if not _is-empty(email) [
      #v(2pt)
      #link("mailto:" + email)[#email]
    ]
  ]
}

#let _authors-block(authors) = {
  if authors.len() > 0 {
    let ncols = calc.min(authors.len(), 3)
    grid(
      columns: (1fr,) * ncols,
      gutter: 10pt,
      row-gutter: 12pt,
      ..authors.map(author => _author-card(author)),
    )
  }
}

#let _title-block(title, subtitle, authors, date, version, abstract, keywords) = {
  let meta = _meta-line(date, version)

  rect(width: 100%, fill: naif-secondary, radius: 8pt, inset: 20pt)[
    #align(center)[
      #text(size: 8pt, weight: 700, tracking: 0.08em, fill: naif-accent)[NAIF REPORT]
      #v(9pt)
      #text(size: 28pt, weight: 800, fill: naif-dark)[#title]
      #v(5pt)
      #line(length: 35%, stroke: 2pt + naif-primary)
      #if subtitle != none [
        #v(9pt)
        #text(size: 14pt, weight: 500, fill: naif-accent-dark)[#subtitle]
      ]
      #if meta != none [
        #v(10pt)
        #text(size: 9pt, weight: 500)[#meta]
      ]
    ]
  ]

  if authors.len() > 0 {
    v(14pt)
    _authors-block(authors)
  }

  if abstract != none {
    v(16pt)
    rect(
      width: 100%,
      fill: naif-white,
      stroke: 0.7pt + naif-secondary,
      radius: 6pt,
      inset: 12pt,
    )[
      #text(weight: 700, fill: naif-accent)[Abstract]
      #v(4pt)
      #abstract
      #if keywords.len() > 0 [
        #v(8pt)
        #text(weight: 700)[Keywords.] #keywords.join(", ")
      ]
    ]
  }

  v(20pt)
}

#let _cover-page(doc-category, title, subtitle, authors, date, version, logo) = {
  let meta = _meta-line(date, version)

  set page(
    paper: "a4",
    margin: (top: 26mm, bottom: 32mm, left: 30mm, right: 26mm),
    header: none,
    footer: none,
  )

  place(
    top + right,
    if logo == none {
      text(size: 20pt, weight: 800, fill: naif-primary)[NAIF]
    } else {
      logo
    },
  )

  v(64mm)
  text(size: 11pt, weight: 700, tracking: 0.08em, fill: naif-accent)[#doc-category]
  v(9pt)
  text(size: 36pt, weight: 800, fill: naif-dark)[#title]
  v(10pt)
  rect(width: 42mm, height: 4pt, fill: naif-primary)

  if subtitle != none {
    v(16pt)
    text(size: 16pt, weight: 500, fill: naif-accent-dark)[#subtitle]
  }

  let author-names = authors.map(author => author.at("name", default: [])).filter(name => name != [] and name != "")

  place(bottom + left)[
    #text(size: 9.5pt, weight: 700, fill: naif-accent)[National Approach for Interoperable repositories and Findable research results]
    #v(6pt)
    #if author-names.len() > 0 [#author-names.join(", ")]
    #if meta != none [
      #if author-names.len() > 0 [#linebreak()]
      #meta
    ]
  ]

  pagebreak()
}

#let naif-report(
  doc-category: [NAIF report],
  title: [Untitled NAIF report],
  subtitle: none,
  authors: (),
  date: none,
  version: none,
  abstract: none,
  keywords: (),
  language: "en",
  logo: none,
  show-outline: true,
  compact-mode: false,
  number-headings: true,
  heading-numbering: "1.",
  font-stack: naif-font-stack,
  mono-font-stack: naif-mono-font-stack,
  website: "https://eth-library.github.io/naif/",
  body,
) = {
  set document(title: title)
  set text(lang: language)
  set text(font: font-stack, size: 10.5pt, fill: naif-dark)

  if not compact-mode {
    counter(page).update(1)
    _cover-page(doc-category, title, subtitle, authors, date, version, logo)
  }

  set page(
    paper: "a4",
    margin: (top: 24mm, bottom: 26mm, left: 23mm, right: 23mm),
    header: [
      #set text(font: font-stack, size: 8pt, fill: naif-dark)
      #grid(
        columns: (1fr, auto),
        [#text(weight: 700, fill: naif-primary)[NAIF]],
        [#text(size: 7.5pt)[#link(website)[#website]]],
      )
    ],
    footer: [
      #set text(font: font-stack, size: 8pt, fill: naif-dark)
      #line(length: 100%, stroke: 0.6pt + naif-secondary)
      #v(4pt)
      #grid(
        columns: (1fr, auto),
        [National Approach for Interoperable repositories and Findable research results],
        [#context { counter(page).display("1") }],
      )
    ],
  )
  set text(font: font-stack, size: 10.5pt, fill: naif-dark)
  set par(justify: true, leading: 0.62em)
  show raw: set text(font: mono-font-stack, size: 9pt)
  set heading(numbering: if number-headings { heading-numbering } else { none })

  show heading.where(level: 1): it => block(above: 20pt, below: 10pt, width: 100%)[
    #text(size: 18pt, weight: 800, fill: naif-dark)[#it.body]
    #v(4pt)
    #line(length: 100%, stroke: 1.2pt + naif-primary)
  ]

  show heading.where(level: 2): it => block(above: 16pt, below: 7pt)[
    #text(size: 14pt, weight: 700, fill: naif-accent)[#it.body]
  ]

  show heading.where(level: 3): it => block(above: 12pt, below: 5pt)[
    #text(size: 11.5pt, weight: 700, fill: naif-dark)[#it.body]
  ]

  show link: set text(fill: naif-accent)

  if show-outline and not compact-mode {
    outline(title: [Contents], indent: auto)
    pagebreak()
    counter(page).update(1)
  }

  if compact-mode {
    _title-block(title, subtitle, authors, date, version, abstract, keywords)
  } else if abstract != none or keywords.len() > 0 {
    rect(
      width: 100%,
      fill: naif-white,
      stroke: 0.7pt + naif-secondary,
      radius: 6pt,
      inset: 12pt,
    )[
      #if abstract != none [
        #text(weight: 700, fill: naif-accent)[Abstract]
        #v(4pt)
        #abstract
      ]
      #if keywords.len() > 0 [
        #v(8pt)
        #text(weight: 700)[Keywords.] #keywords.join(", ")
      ]
    ]
    v(18pt)
  }

  body
}

#let naif-callout(body, title: [Note]) = rect(
  width: 100%,
  fill: naif-secondary,
  stroke: 0.8pt + naif-primary,
  radius: 6pt,
  inset: 11pt,
)[
  #text(weight: 700, fill: naif-accent)[#title]
  #v(4pt)
  #body
]

#let naif-stat(value, label, detail: none) = rect(
  width: 100%,
  fill: naif-white,
  stroke: 0.7pt + naif-secondary,
  radius: 6pt,
  inset: 10pt,
)[
  #text(size: 20pt, weight: 800, fill: naif-accent)[#value]
  #v(2pt)
  #text(weight: 700)[#label]
  #if detail != none [
    #v(3pt)
    #text(size: 8.5pt)[#detail]
  ]
]
