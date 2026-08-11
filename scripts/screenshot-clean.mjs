#!/usr/bin/env node

import { mkdir } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { chromium } from "playwright";

const DEFAULT_WAIT_MS = 6000;
const DEFAULT_TIMEOUT_MS = 45000;
const DEFAULT_WIDTH = 1600;
const DEFAULT_HEIGHT = 900;

const COOKIE_TEXTS = [
  "accept",
  "accept all",
  "accept all cookies",
  "agree",
  "allow all",
  "yes, i agree",
  "alle akzeptieren",
  "akzeptieren",
  "einverstanden",
  "zustimmen",
  "tout accepter",
  "accepter",
  "j'accepte",
  "j accepte",
  "autoriser",
];

const REJECT_TEXTS = [
  "reject",
  "reject all",
  "only necessary",
  "necessary only",
  "decline",
  "refuse",
  "deny",
  "save preferences",
  "alle ablehnen",
  "ablehnen",
  "nur notwendige",
  "tout refuser",
  "refuser",
  "uniquement necessaires",
  "uniquement nécessaires",
  "enregistrer",
];

const OVERLAY_SELECTORS = [
  "#onetrust-banner-sdk",
  "#onetrust-consent-sdk",
  ".onetrust-pc-dark-filter",
  "#CybotCookiebotDialog",
  "#CookiebotWidget",
  "#cookie-law-info-bar",
  ".cookie-banner",
  ".cookies-banner",
  ".cookie-consent",
  ".cookie-consent-banner",
  ".cc-window",
  ".qc-cmp2-container",
  ".qc-cmp2-ui",
  ".osano-cm-window",
  ".osano-cm-dialog",
  "[id*='cookie']",
  "[class*='cookie']",
  "[id*='consent']",
  "[class*='consent']",
  "[data-nosnippet='true']",
  ".modal-backdrop",
  ".overlay",
  ".newsletter-popup",
];

const CONSENT_CONTAINER_SELECTORS = [
  "#onetrust-consent-sdk",
  "#onetrust-banner-sdk",
  "#CybotCookiebotDialog",
  ".qc-cmp2-container",
  ".qc-cmp2-ui",
  ".osano-cm-window",
  ".osano-cm-dialog",
  "[id*='cookie']",
  "[class*='cookie']",
  "[id*='consent']",
  "[class*='consent']",
  "[data-testid*='consent']",
  "[data-testid*='cookie']",
  "[aria-label*='cookie']",
  "[aria-label*='consent']",
];

function parseViewport(viewportValue) {
  const match = /^(\d+)x(\d+)$/.exec(viewportValue);
  if (!match) {
    throw new Error(`Invalid --viewport value '${viewportValue}'. Use <width>x<height>.`);
  }
  return { width: Number(match[1]), height: Number(match[2]) };
}

function parseArgs(rawArgs) {
  const args = {
    hide: [],
    click: [],
    timeoutMs: DEFAULT_TIMEOUT_MS,
    waitMs: DEFAULT_WAIT_MS,
    viewport: { width: DEFAULT_WIDTH, height: DEFAULT_HEIGHT },
  };

  const positionals = [];
  for (let i = 0; i < rawArgs.length; i += 1) {
    const token = rawArgs[i];
    if (!token.startsWith("--")) {
      positionals.push(token);
      continue;
    }

    const [key, inlineValue] = token.split("=", 2);
    const nextValue = inlineValue ?? rawArgs[i + 1];

    if (key === "--wait-ms") {
      args.waitMs = Number(nextValue);
      if (!inlineValue) {
        i += 1;
      }
      continue;
    }

    if (key === "--timeout-ms") {
      args.timeoutMs = Number(nextValue);
      if (!inlineValue) {
        i += 1;
      }
      continue;
    }

    if (key === "--viewport") {
      args.viewport = parseViewport(nextValue);
      if (!inlineValue) {
        i += 1;
      }
      continue;
    }

    if (key === "--hide") {
      const selectors = nextValue
        .split(",")
        .map((selector) => selector.trim())
        .filter(Boolean);
      args.hide.push(...selectors);
      if (!inlineValue) {
        i += 1;
      }
      continue;
    }

    if (key === "--click") {
      // Not comma-split: selectors such as a:has-text("Publication counts (2012, 2022)")
      // may legitimately contain commas.  Repeat --click to click several elements.
      const selector = (nextValue ?? "").trim();
      if (!selector || (!inlineValue && selector.startsWith("--"))) {
        throw new Error("--click requires a selector.");
      }
      args.click.push(selector);
      if (!inlineValue) {
        i += 1;
      }
      continue;
    }

    if (key === "--full-page") {
      args.fullPage = true;
      continue;
    }

    if (key === "--help") {
      args.help = true;
      continue;
    }

    throw new Error(`Unknown option '${token}'.`);
  }

  args.url = positionals[0];
  args.output = positionals[1];
  return args;
}

function printHelp() {
  const usage = [
    "Usage:",
    "  npm run screenshot:clean -- <url> <output-file> [options]",
    "",
    "Options:",
    `  --wait-ms <n>       Wait after page load (default: ${DEFAULT_WAIT_MS})`,
    `  --timeout-ms <n>    Navigation timeout (default: ${DEFAULT_TIMEOUT_MS})`,
    `  --viewport <WxH>    Viewport size (default: ${DEFAULT_WIDTH}x${DEFAULT_HEIGHT})`,
    "  --hide <sel1,sel2>  Additional selectors to remove before screenshot",
    "  --click <selector>  Click before capturing (repeatable, e.g. a dashboard tab)",
    "  --full-page         Capture full page (default is 16:9 viewport)",
  ];
  process.stdout.write(`${usage.join("\n")}\n`);
}

async function tryClickConsentByText(page, texts) {
  const clicked = await page.evaluate((candidates) => {
    const normalise = (value) =>
      (value || "")
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/\s+/g, " ")
        .trim();

    const wanted = new Set(candidates.map((text) => normalise(text)));
    const consentSelectors = [
      "#onetrust-consent-sdk",
      "#onetrust-banner-sdk",
      "#CybotCookiebotDialog",
      ".qc-cmp2-container",
      ".qc-cmp2-ui",
      ".osano-cm-window",
      ".osano-cm-dialog",
      "[id*='cookie']",
      "[class*='cookie']",
      "[id*='consent']",
      "[class*='consent']",
      "[data-testid*='consent']",
      "[data-testid*='cookie']",
      "[aria-label*='cookie']",
      "[aria-label*='consent']",
    ];

    const roots = new Set();
    for (const selector of consentSelectors) {
      for (const element of document.querySelectorAll(selector)) {
        roots.add(element);
      }
    }

    const nodeSelector =
      "button, a[role='button'], [role='button'], input[type='button'], input[type='submit']";
    const nodes = [];
    for (const root of roots) {
      for (const node of root.querySelectorAll(nodeSelector)) {
        nodes.push(node);
      }
    }

    if (nodes.length === 0) {
      return "";
    }

    const extractText = (element) => {
      if (element instanceof HTMLInputElement) {
        return element.value || "";
      }
      return element.textContent || "";
    };

    for (const node of nodes) {
      const text = normalise(extractText(node));
      if (!text) {
        continue;
      }
      for (const candidate of wanted) {
        if (text === candidate || text.includes(candidate)) {
          node.click();
          return text;
        }
      }
    }
    return "";
  }, texts);

  return clicked;
}

async function waitForImagesToLoad(page, timeoutMs) {
  const maxWaitMs = Math.min(timeoutMs, 12000);
  const start = Date.now();

  while (Date.now() - start < maxWaitMs) {
    const status = await page.evaluate(() => {
      const styleVisible = (element) => {
        const style = window.getComputedStyle(element);
        if (
          style.display === "none" ||
          style.visibility === "hidden" ||
          Number(style.opacity) === 0
        ) {
          return false;
        }
        const rect = element.getBoundingClientRect();
        return rect.width > 2 && rect.height > 2;
      };

      const images = Array.from(document.querySelectorAll("img")).filter(styleVisible);
      if (images.length === 0) {
        return { visibleCount: 0, pendingCount: 0 };
      }

      let pending = 0;
      for (const image of images) {
        if (!image.complete || image.naturalWidth === 0) {
          pending += 1;
        }
      }
      return { visibleCount: images.length, pendingCount: pending };
    });

    if (status.visibleCount === 0 || status.pendingCount === 0) {
      return;
    }

    await page.waitForTimeout(250);
  }
}

async function hideOverlays(page, customSelectors) {
  const selectors = [...OVERLAY_SELECTORS, ...CONSENT_CONTAINER_SELECTORS, ...customSelectors];

  await page.addStyleTag({
    content: [
      "* { animation: none !important; transition: none !important; }",
      `${selectors.join(",")} { display: none !important; visibility: hidden !important; opacity: 0 !important; }`,
      "html, body { overflow: auto !important; }",
    ].join("\n"),
  });

  await page.evaluate((selectorList) => {
    const removeElement = (element) => {
      element.style.setProperty("display", "none", "important");
      element.style.setProperty("visibility", "hidden", "important");
      element.style.setProperty("opacity", "0", "important");
      element.setAttribute("aria-hidden", "true");
    };

    for (const selector of selectorList) {
      for (const element of document.querySelectorAll(selector)) {
        removeElement(element);
      }
    }

    const width = window.innerWidth;
    const height = window.innerHeight;
    const allNodes = Array.from(document.querySelectorAll("body *"));

    for (const element of allNodes) {
      const style = window.getComputedStyle(element);
      const position = style.position;
      const zIndex = Number.parseInt(style.zIndex || "0", 10);
      if (position !== "fixed" && position !== "sticky") {
        continue;
      }

      if (!Number.isFinite(zIndex) || zIndex < 1000) {
        continue;
      }

      const rect = element.getBoundingClientRect();
      const visibleArea = Math.max(0, rect.width) * Math.max(0, rect.height);
      const viewportArea = width * height;

      const blocksLargeArea = visibleArea >= viewportArea * 0.15;
      const blocksTopOrBottomBar = rect.width >= width * 0.9 && rect.height >= height * 0.08;
      const overlaysMiddle =
        rect.top < height * 0.75 && rect.bottom > height * 0.25 && rect.width >= width * 0.5;

      if (blocksLargeArea || blocksTopOrBottomBar || overlaysMiddle) {
        removeElement(element);
      }
    }
  }, selectors);
}

async function clickTargets(page, selectors) {
  for (const selector of selectors) {
    try {
      await page.click(selector, { timeout: 10000 });
      // Quarto dashboards re-layout tab panes (and re-fit Leaflet maps) on shown.bs.tab.
      await page.waitForTimeout(750);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      process.stderr.write(`WARNING: could not click '${selector}': ${message}\n`);
    }
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help || !args.url || !args.output) {
    printHelp();
    process.exit(args.help ? 0 : 1);
  }

  if (!Number.isFinite(args.waitMs) || args.waitMs < 0) {
    throw new Error("--wait-ms must be a non-negative number.");
  }

  if (!Number.isFinite(args.timeoutMs) || args.timeoutMs <= 0) {
    throw new Error("--timeout-ms must be a positive number.");
  }

  const outputDir = path.dirname(args.output);
  await mkdir(outputDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: args.viewport });
  const page = await context.newPage();

  try {
    const response = await page.goto(args.url, {
      waitUntil: "domcontentloaded",
      timeout: args.timeoutMs,
    });
    const status = response?.status();
    if (typeof status === "number" && status >= 400) {
      process.stderr.write(
        `WARNING: ${args.url} returned HTTP ${status}; screenshot may show an error page.\n`,
      );
    }
    await page.waitForLoadState("networkidle", { timeout: args.timeoutMs }).catch(() => null);

    await tryClickConsentByText(page, REJECT_TEXTS);
    await page.waitForTimeout(400);
    await tryClickConsentByText(page, COOKIE_TEXTS);
    await page.waitForTimeout(400);

    await waitForImagesToLoad(page, args.timeoutMs);

    await hideOverlays(page, args.hide);
    await clickTargets(page, args.click);
    await page.waitForTimeout(args.waitMs);

    await page.screenshot({
      path: args.output,
      fullPage: Boolean(args.fullPage),
      type: "png",
    });

    process.stdout.write(`Saved screenshot: ${args.output}\n`);
  } finally {
    await context.close();
    await browser.close();
  }
}

main().catch((error) => {
  process.stderr.write(`Screenshot failed: ${error.message}\n`);
  process.exit(1);
});
