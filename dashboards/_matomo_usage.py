"""Helpers for building the site usage dashboard from Matomo data."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

DATA_DIR: Path = Path(__file__).resolve().parent / "_data"
SNAPSHOT_PATH: Path = DATA_DIR / "matomo-usage.json"

DEFAULT_MATOMO_BASE_URL: str = "https://library-ethz.opsone-analytics.ch"
DEFAULT_MATOMO_SITE_ID: str = "81"
DEFAULT_PUBLIC_SITE_URL: str = "https://eth-library.github.io/naif/"
DEFAULT_REPORT_START_DATE: str = "2025-07-01"
REQUEST_TIMEOUT_SECONDS: float = 30.0
USER_AGENT: str = (
    "naif-matomo-dashboard/1.0 "
    "(https://github.com/eth-library/naif; mailto:info@naif.ch)"
)

TRAFFIC_SOURCE_KEYS: list[tuple[str, str]] = [
    ("Search engines", "Referrers_visitorsFromSearchEngines"),
    ("Social networks", "Referrers_visitorsFromSocialNetworks"),
    ("Websites", "Referrers_visitorsFromWebsites"),
    ("Direct entry", "Referrers_visitorsFromDirectEntry"),
    ("AI assistants", "Referrers_visitorsFromAIAssistants"),
    ("Campaigns", "Referrers_visitorsFromCampaigns"),
]


@dataclass(frozen=True)
class MatomoConfig:
    """Configuration needed to query the Matomo Reporting API."""

    token_auth: str
    base_url: str = DEFAULT_MATOMO_BASE_URL
    site_id: str = DEFAULT_MATOMO_SITE_ID
    public_site_url: str = DEFAULT_PUBLIC_SITE_URL
    report_start_date: str = DEFAULT_REPORT_START_DATE

    @property
    def api_endpoint(self) -> str:
        """Return the API endpoint used for POST requests."""
        return f"{self.base_url.rstrip('/')}/index.php"


@dataclass(frozen=True)
class UsageTotals:
    """Lifetime summary metrics for the reporting window."""

    visits: int
    pageviews: int
    downloads: int
    outlinks: int
    avg_time_on_site_seconds: int
    bounce_rate: str


@dataclass(frozen=True)
class TrafficSource:
    """One traffic-source bucket from Matomo referrer metrics."""

    label: str
    visits: int
    share: str


@dataclass(frozen=True)
class MonthlyUsage:
    """Historic month-by-month usage metrics."""

    month: str
    visits: int
    pageviews: int
    downloads: int
    outlinks: int
    avg_time_on_site_seconds: int
    bounce_rate: str


@dataclass(frozen=True)
class TopPage:
    """All-time page-level usage for a single page."""

    path: str
    href: str
    pageviews: int
    visits: int
    avg_time_on_page_seconds: int
    bounce_rate: str


@dataclass(frozen=True)
class UsageSnapshot:
    """Serialisable snapshot consumed by the Quarto dashboard page."""

    status: str
    message: str | None
    generated_at: str | None
    report_start_date: str
    report_end_date: str | None
    totals: UsageTotals | None
    traffic_sources: list[TrafficSource] = field(default_factory=list)
    history: list[MonthlyUsage] = field(default_factory=list)
    top_pages: list[TopPage] = field(default_factory=list)


def load_matomo_config() -> MatomoConfig | None:
    """Return config from environment variables, or ``None`` if no token is set."""
    token_auth = os.getenv("MATOMO_TOKEN_AUTH", "").strip()
    if not token_auth:
        return None

    return MatomoConfig(
        token_auth=token_auth,
        base_url=os.getenv("MATOMO_BASE_URL", DEFAULT_MATOMO_BASE_URL).strip()
        or DEFAULT_MATOMO_BASE_URL,
        site_id=os.getenv("MATOMO_SITE_ID", DEFAULT_MATOMO_SITE_ID).strip()
        or DEFAULT_MATOMO_SITE_ID,
        public_site_url=os.getenv(
            "MATOMO_PUBLIC_SITE_URL", DEFAULT_PUBLIC_SITE_URL
        ).strip()
        or DEFAULT_PUBLIC_SITE_URL,
        report_start_date=os.getenv(
            "MATOMO_REPORT_START_DATE",
            DEFAULT_REPORT_START_DATE,
        ).strip()
        or DEFAULT_REPORT_START_DATE,
    )


def format_duration(seconds: int) -> str:
    """Format a duration in seconds as a short human-readable string."""
    total_seconds = max(0, int(seconds))
    minutes, remaining_seconds = divmod(total_seconds, 60)
    hours, remaining_minutes = divmod(minutes, 60)

    parts: list[str] = []
    if hours:
        parts.append(f"{hours}h")
    if hours or remaining_minutes:
        parts.append(f"{remaining_minutes}m")
    parts.append(f"{remaining_seconds}s")
    return " ".join(parts)


def format_month_label(month: str) -> str:
    """Format ``YYYY-MM`` month keys as ``Mon YYYY``."""
    parsed = datetime.strptime(month, "%Y-%m").replace(tzinfo=UTC).date()
    return parsed.strftime("%b %Y")


def _coerce_int(value: Any) -> int:
    """Return API values as integers, falling back to ``0``."""
    try:
        return int(float(value))
    except TypeError:
        return 0
    except ValueError:
        return 0


def _normalise_rate(value: Any) -> str:
    """Return percentage-style values as display strings."""
    if value is None:
        return "-"

    text = str(value).strip()
    if not text:
        return "-"
    if text.endswith("%"):
        return text

    try:
        return f"{float(text):.1f}%"
    except ValueError:
        return text


def normalise_page_path(
    url: str | None,
    label: str | None,
    public_site_url: str,
) -> tuple[str, str]:
    """Return a stable display path and href for a Matomo page record."""
    site_parts = urlparse(public_site_url)
    site_prefix = site_parts.path.rstrip("/")

    raw_label = (label or "").strip()
    raw_url = (url or "").strip()

    if raw_url:
        parsed_url = urlparse(raw_url)
        href = raw_url
        same_site = (
            parsed_url.scheme == site_parts.scheme
            and parsed_url.netloc == site_parts.netloc
        )
        if same_site:
            raw_path = parsed_url.path or "/"
            if site_prefix and raw_path.startswith(site_prefix):
                trimmed_path = raw_path[len(site_prefix) :]
            else:
                trimmed_path = raw_path
            display_path = _clean_relative_path(trimmed_path)
            return display_path, _join_site_url(public_site_url, display_path)

        display_path = raw_label or raw_url
        return display_path, href

    if raw_label:
        display_path = raw_label
        if site_prefix and display_path.startswith(site_prefix):
            display_path = display_path[len(site_prefix) :]
        display_path = _clean_relative_path(display_path)
        return display_path, _join_site_url(public_site_url, display_path)

    return "/", "/"


def _clean_relative_path(raw_path: str) -> str:
    """Normalise an internal page path for display and linking."""
    cleaned = raw_path.strip() or "/"
    if not cleaned.startswith("/"):
        cleaned = f"/{cleaned}"

    if cleaned.endswith("/index.html"):
        cleaned = cleaned[: -len("index.html")]
    if cleaned != "/" and cleaned.endswith(".html"):
        cleaned = cleaned[: -len(".html")] + "/"
    if not cleaned.endswith("/") and "." not in cleaned.rsplit("/", 1)[-1]:
        cleaned = f"{cleaned}/"
    return cleaned


def _join_site_url(public_site_url: str, relative_path: str) -> str:
    """Join the public site URL to a normalised relative page path."""
    site_base = public_site_url.rstrip("/")
    if relative_path == "/":
        return f"{site_base}/"
    return f"{site_base}{relative_path}"


def _matomo_request(config: MatomoConfig, method: str, **params: str) -> Any:
    """Issue a POST request to the Matomo Reporting API and decode JSON."""
    payload = urlencode(
        {
            "module": "API",
            "method": method,
            "format": "JSON",
            "idSite": config.site_id,
            **params,
            "token_auth": config.token_auth,
        }
    ).encode()

    request = Request(
        config.api_endpoint,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.load(response)
    except HTTPError as exc:  # pragma: no cover - exercised via integration only
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Matomo API request failed with HTTP {exc.code}: {detail}"
        ) from exc
    except URLError as exc:  # pragma: no cover - exercised via integration only
        raise RuntimeError(f"Matomo API request failed: {exc.reason}") from exc


def build_snapshot(
    config: MatomoConfig,
    totals_payload: dict[str, Any],
    history_payload: dict[str, dict[str, Any]],
    top_pages_payload: list[dict[str, Any]],
    *,
    generated_at: datetime,
    report_end_date: str,
) -> UsageSnapshot:
    """Build a serialisable snapshot from raw Matomo payloads."""
    totals = UsageTotals(
        visits=_coerce_int(totals_payload.get("nb_visits")),
        pageviews=_coerce_int(totals_payload.get("nb_pageviews")),
        downloads=_coerce_int(totals_payload.get("nb_downloads")),
        outlinks=_coerce_int(totals_payload.get("nb_outlinks")),
        avg_time_on_site_seconds=_coerce_int(totals_payload.get("avg_time_on_site")),
        bounce_rate=_normalise_rate(totals_payload.get("bounce_rate")),
    )

    traffic_sources = [
        TrafficSource(
            label=label,
            visits=_coerce_int(totals_payload.get(metric_key)),
            share=_normalise_rate(totals_payload.get(f"{metric_key}_percent")),
        )
        for label, metric_key in TRAFFIC_SOURCE_KEYS
        if _coerce_int(totals_payload.get(metric_key)) > 0
    ]

    history = [
        MonthlyUsage(
            month=month,
            visits=_coerce_int(values.get("nb_visits")),
            pageviews=_coerce_int(values.get("nb_pageviews")),
            downloads=_coerce_int(values.get("nb_downloads")),
            outlinks=_coerce_int(values.get("nb_outlinks")),
            avg_time_on_site_seconds=_coerce_int(values.get("avg_time_on_site")),
            bounce_rate=_normalise_rate(values.get("bounce_rate")),
        )
        for month, values in sorted(history_payload.items())
    ]

    top_pages = [
        TopPage(
            path=page_path,
            href=href,
            pageviews=_coerce_int(entry.get("nb_hits")),
            visits=_coerce_int(entry.get("nb_visits")),
            avg_time_on_page_seconds=_coerce_int(entry.get("avg_time_on_page")),
            bounce_rate=_normalise_rate(entry.get("bounce_rate")),
        )
        for entry in top_pages_payload
        for page_path, href in [
            normalise_page_path(
                entry.get("url"),
                entry.get("label") or entry.get("Actions_PageUrl"),
                config.public_site_url,
            )
        ]
    ]

    return UsageSnapshot(
        status="ok",
        message=None,
        generated_at=generated_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        report_start_date=config.report_start_date,
        report_end_date=report_end_date,
        totals=totals,
        traffic_sources=traffic_sources,
        history=history,
        top_pages=top_pages,
    )


def fetch_usage_snapshot(
    config: MatomoConfig,
    *,
    today: date | None = None,
) -> UsageSnapshot:
    """Fetch lifetime and month-by-month usage metrics from Matomo."""
    report_end = today or datetime.now(UTC).date()
    report_window = f"{config.report_start_date},{report_end.isoformat()}"

    totals_payload = _matomo_request(
        config,
        "API.get",
        period="range",
        date=report_window,
    )
    history_payload = _matomo_request(
        config,
        "API.get",
        period="month",
        date=report_window,
    )
    top_pages_payload = _matomo_request(
        config,
        "Actions.getPageUrls",
        period="range",
        date=report_window,
        flat="1",
        filter_limit="10",
        filter_sort_column="nb_hits",
        filter_sort_order="desc",
    )

    if not isinstance(totals_payload, dict):
        raise TypeError("Matomo totals payload was not a JSON object")
    if not isinstance(history_payload, dict):
        raise TypeError("Matomo history payload was not a JSON object")
    if not isinstance(top_pages_payload, list):
        raise TypeError("Matomo top-pages payload was not a JSON array")

    return build_snapshot(
        config,
        totals_payload,
        history_payload,
        top_pages_payload,
        generated_at=datetime.now(UTC),
        report_end_date=report_end.isoformat(),
    )


def make_placeholder_snapshot(message: str) -> UsageSnapshot:
    """Return a placeholder snapshot for renders without Matomo credentials."""
    return UsageSnapshot(
        status="missing_config",
        message=message,
        generated_at=None,
        report_start_date=DEFAULT_REPORT_START_DATE,
        report_end_date=None,
        totals=None,
    )


def write_snapshot(snapshot: UsageSnapshot, output_path: Path = SNAPSHOT_PATH) -> Path:
    """Write a usage snapshot to disk as formatted JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(asdict(snapshot), indent=2)
    output_path.write_text(f"{payload}\n", encoding="utf-8")
    return output_path
