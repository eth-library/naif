#show: doc => naif-report(
$if(doc-category)$
  doc-category: [$doc-category$],
$endif$
$if(title)$
  title: [$title$],
$endif$
$if(subtitle)$
  subtitle: [$subtitle$],
$endif$
$if(by-author)$
  authors: (
$for(by-author)$
$if(it.name.literal)$
    (
      name: [$it.name.literal$],
      affiliation: [$for(it.affiliations)$$it.name$$sep$, $endfor$],
      email: [$it.email$],
    ),
$endif$
$endfor$
  ),
$endif$
$if(date)$
  date: [$date$],
$endif$
$if(report-version)$
  version: [$report-version$],
$elseif(version)$
  version: [$version$],
$endif$
$if(abstract)$
  abstract: [$abstract$],
$endif$
$if(keywords)$
  keywords: ($for(keywords)$"$it$"$sep$, $endfor$),
$endif$
$if(lang)$
  language: "$lang$",
$endif$
$if(logo-path)$
  logo: image("$logo-path$"),
$endif$
$if(mainfont)$
  font-stack: ("$mainfont$", "Barlow", "Inter", "Arial", "Helvetica"),
$endif$
$if(codefont)$
  mono-font-stack: ("$codefont$", "Menlo", "DejaVu Sans Mono"),
$endif$
$if(website)$
  website: "$website$",
$endif$
$if(toc)$
  show-outline: true,
$else$
  show-outline: false,
$endif$
$if(compact-mode)$
  compact-mode: true,
$else$
  compact-mode: false,
$endif$
$if(section-numbering)$
  number-headings: true,
  heading-numbering: "$section-numbering$",
$else$
  number-headings: false,
$endif$
  doc,
)
