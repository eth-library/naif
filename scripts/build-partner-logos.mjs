import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

// Coordinates use the original 780 × 370 canvas. Export at 3× for print and retina screens.
const directory = new URL("../images/logos/", import.meta.url);
const logos = [
  { name: "ETH Library", file: "sources/eth-library.svg", x: 56, y: 38, width: 186, height: 80 },
  { name: "University of Zurich", file: "sources/uzh.svg", x: 330, y: 27, width: 187, height: 65 },
  { name: "EPFL", file: "sources/epfl.svg", x: 603, y: 37, width: 114, height: 55.2 },
  { name: "ZHAW", file: "sources/zhaw.jpg", x: 143, y: 165, width: 65, height: 68.2 },
  { name: "PHSG", file: "PHSG-Logo-Wortmarke_farbig.svg", x: 345, y: 162, width: 60, height: 75.1 },
  {
    name: "University of Fribourg",
    file: "sources/unifr.svg",
    x: 548,
    y: 167,
    width: 62,
    height: 75,
  },
  {
    name: "University of Neuchâtel",
    file: "sources/unine.svg",
    x: 56,
    y: 283,
    width: 121,
    height: 36.4,
  },
  {
    name: "University of St.Gallen",
    file: "sources/hsg.svg",
    x: 222,
    y: 274,
    width: 225,
    height: 48.1,
  },
  {
    name: "swissuniversities",
    file: "sources/swissuniversities.svg",
    x: 494,
    y: 296,
    width: 222,
    height: 25.7,
  },
];

const images = await Promise.all(
  logos.map(async ({ name, file, x, y, width, height }) => {
    const data = await readFile(new URL(file, directory));
    const mime = file.endsWith(".svg") ? "image/svg+xml" : "image/jpeg";
    return `  <image x="${x}" y="${y}" width="${width}" height="${height}" preserveAspectRatio="xMidYMid meet" href="data:${mime};base64,${data.toString("base64")}"><title>${name}</title></image>`;
  }),
);
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="2340" height="1110" viewBox="0 0 780 370" role="img" aria-labelledby="title description">
  <title id="title">NAIF partner institutions and swissuniversities</title>
  <desc id="description">${logos.map(({ name }) => name).join(", ")}.</desc>
  <rect width="780" height="370" fill="white"/>
${images.join("\n")}
</svg>
`;

const browser = await chromium.launch();
try {
  const page = await browser.newPage({
    viewport: { width: 2340, height: 1110 },
    deviceScaleFactor: 1,
  });
  // Decode each original separately so a broken nested SVG cannot silently disappear.
  await page.setContent(
    `<body style="margin:0;background:white">${images.join("\n").replaceAll("<image ", "<img ").replaceAll("href=", "src=")}</body>`,
  );
  await page
    .locator("img")
    .evaluateAll((elements) => Promise.all(elements.map((element) => element.decode())));
  await page.setContent(
    `<body style="margin:0;background:white"><img width="2340" height="1110" src="data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}"></body>`,
  );
  await page.locator("img").evaluate((element) => element.decode());
  await page.screenshot({
    path: fileURLToPath(new URL("all-logos.jpg", directory)),
    type: "jpeg",
    quality: 95,
  });
  await writeFile(new URL("all-logos.svg", directory), svg);
} finally {
  await browser.close();
}
console.log("Built images/logos/all-logos.svg and all-logos.jpg (2340 × 1110).");
