# Partner logos

`all-logos.jpg` is the shared website and poster image. `all-logos.svg` is the
self-contained, editable composition, with each institution embedded as a separate
image object. Both use a white 780 × 370 layout and export at 2340 × 1110 pixels.

To rebuild from the local sources, run:

```bash
npm run logos:build
```

The builder uses the project's existing Playwright dependency and Chromium. On a
new machine, run `npm install` and `npm run screenshot:install-browsers` first.
Rebuilding requires no network access. Edit the placement records in
`scripts/build-partner-logos.mjs` to adjust the composition; editing the generated
SVG directly is also possible, but those edits will be replaced on the next build.

## Sources and rights

Collected in September 2026. The logos are trademarks of their respective
institutions; the repository's software licence does not grant rights to them.
Colours and aspect ratios are preserved. The arrangement follows the previous
NAIF composite, including swissuniversities as the ninth logo.

| Institution | Local source | Official source and preparation |
| --- | --- | --- |
| ETH Library | `sources/eth-library.svg`, `sources/eth-zurich.svg` | ETH wordmark extracted from the inline SVG on [E-Periodica](https://www.e-periodica.ch/), an ETH Library service. The existing NAIF library lockup was reconstructed around that artwork: separator line and “ETH Library” descriptor in outlined Arial. This is a reconstructed lockup, not a downloaded official library master. |
| University of Zurich | `sources/uzh.svg` | [Official SVG](https://cd.uzh.ch/dam/jcr:e2f01a3c-e263-427a-91d7-723fc337af4b/uzh-logo.svg) from the [corporate design resources](https://cd.uzh.ch/de/elements.html). |
| EPFL | `sources/epfl.svg` | [Official website SVG](https://static.epfl.ch/latest/images/logo.svg). |
| ZHAW | `sources/zhaw.jpg` | [Official RGB JPEG](https://www.zhaw.ch/storage/engineering/ueber-uns/medien/zhaw_rgb.jpg) from the [media resources](https://www.zhaw.ch/de/engineering/ueber-uns/medien). |
| PHSG | `PHSG-Logo-Wortmarke_farbig.svg` | New artwork supplied by the project owner. The supplied JPEG and PNG are alternative formats; the composite uses the SVG master. |
| University of Fribourg | `sources/unifr.svg` | Compact logo extracted without redrawing from glyph U+E00A of the [official icon font](https://cdn.unifr.ch/uf/v2.4.5/fonts/fonticons.woff), used by the [official website](https://www.unifr.ch/home/en/). Glyph outlines were converted with fontTools, flipping the font's vertical coordinate system for SVG. |
| University of Neuchâtel | `sources/unine.svg` | Desktop logo extracted from the inline SVG on the [official homepage](https://www.unine.ch/). |
| University of St.Gallen | `sources/hsg.svg` | German-language logo extracted from the inline SVG on the [official homepage](https://www.unisg.ch/de/). |
| swissuniversities | `sources/swissuniversities.svg` | [Official website SVG](https://www.swissuniversities.ch/_assets/feb1d86054ab2e718cccf9db6ed46074/Partials/Logo/Images/Logo.svg). |

The Fribourg font and Arial are only needed when preparing their outlined source
assets from scratch. They are not runtime or rebuild dependencies.
