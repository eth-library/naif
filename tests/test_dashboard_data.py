"""Validate dashboard CSV data against Pydantic schemas."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from pydantic import BaseModel, field_validator

DATA_DIR = Path(__file__).resolve().parent.parent / "dashboards" / "_data"
HEI_CHANGELOG_PATH = DATA_DIR / "hei-changelog.json"

VALID_TYPES = {"University", "Univ. Inst.", "UAS", "UAS Inst.", "UTE"}


def required_text_cell(value: object) -> str:
    """Normalise required text cells so missing values fail validation."""
    if pd.isna(value):
        return ""
    return str(value)


def split_identifier_cell(value: object) -> set[str]:
    """Split a pipe-separated identifier cell into unique values."""
    text = required_text_cell(value).strip()
    if not text:
        return set()
    return {part.strip() for part in text.split("|") if part.strip()}


# ---------------------------------------------------------------------------
# HEI schema
# ---------------------------------------------------------------------------

HEI_REQUIRED_COLUMNS = [
    "name",
    "short_name",
    "type",
    "town",
    "lat",
    "lon",
    "ror_id",
    "wikidata_id",
    "coara_signatory",
    "dora_signatory",
    "coara_member",
    "openalex_primary_id",
    "openalex_ids",
    "openorgs_ids",
]


class HEIRecord(BaseModel):
    """Schema for a single row in hei.csv."""

    name: str
    short_name: str
    type: str
    town: str
    lat: float | None = None
    lon: float | None = None

    @field_validator("name", "short_name", "type", "town")
    @classmethod
    def must_be_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("type")
    @classmethod
    def must_be_valid_type(cls, v: str) -> str:
        if v not in VALID_TYPES:
            raise ValueError(f"{v!r} is not a valid institution type")
        return v

    @field_validator("lat")
    @classmethod
    def lat_in_range(cls, v: float | None) -> float | None:
        if v is not None and not (45.0 <= v <= 48.0):
            raise ValueError(f"latitude {v} is outside Switzerland bounds")
        return v

    @field_validator("lon")
    @classmethod
    def lon_in_range(cls, v: float | None) -> float | None:
        if v is not None and not (5.0 <= v <= 11.0):
            raise ValueError(f"longitude {v} is outside Switzerland bounds")
        return v


# ---------------------------------------------------------------------------
# TOBI schema
# ---------------------------------------------------------------------------

TOBI_REQUIRED_COLUMNS = [
    "name",
    "short_name",
    "type",
    "town",
    "tobi_findable_dim",
    "tobi_findable_scopus",
    "tobi_findable_wos",
    "tobi_findable_openaire",
    "tobi_findable_openalex",
]


class TOBIRecord(BaseModel):
    """Schema for a single row in tobi.csv."""

    name: str
    short_name: str
    type: str
    town: str

    @field_validator("name", "short_name", "type", "town")
    @classmethod
    def must_be_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("type")
    @classmethod
    def must_be_valid_type(cls, v: str) -> str:
        if v not in VALID_TYPES:
            raise ValueError(f"{v!r} is not a valid institution type")
        return v


# ---------------------------------------------------------------------------
# HEI changelog schema
# ---------------------------------------------------------------------------


class HEIChangelogCommit(BaseModel):
    """Schema for a single git reference in the HEI changelog."""

    sha: str
    message: str

    @field_validator("sha")
    @classmethod
    def sha_looks_like_commit(cls, v: str) -> str:
        text = v.strip()
        if len(text) < 7 or any(ch not in "0123456789abcdef" for ch in text.lower()):
            raise ValueError("commit sha must be a hexadecimal git hash")
        return text

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("commit message must not be empty")
        return v


class HEIChangelogEntry(BaseModel):
    """Schema for a single entry in hei-changelog.json."""

    date: str
    scope: str
    title: str
    summary: str
    row_count_before: int | None = None
    row_count_after: int
    changes: list[str]
    corrections: list[str]
    commits: list[HEIChangelogCommit]

    @field_validator("date")
    @classmethod
    def date_must_be_iso(cls, v: str) -> str:
        date.fromisoformat(v)
        return v

    @field_validator("scope", "title", "summary")
    @classmethod
    def required_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("row_count_before", "row_count_after")
    @classmethod
    def row_count_must_be_positive(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("row count must be positive")
        return v

    @field_validator("changes", "corrections")
    @classmethod
    def text_lists_must_not_be_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("list must contain at least one entry")
        if any(not item or not item.strip() for item in v):
            raise ValueError("list items must not be empty")
        return v

    @field_validator("commits")
    @classmethod
    def commits_must_not_be_empty(
        cls, v: list[HEIChangelogCommit]
    ) -> list[HEIChangelogCommit]:
        if not v:
            raise ValueError("entry must include at least one commit")
        return v


# ---------------------------------------------------------------------------
# Tests – hei.csv
# ---------------------------------------------------------------------------


class TestHEIData:
    """Validate dashboards/_data/hei.csv."""

    @pytest.fixture(scope="class")
    def hei_df(self) -> pd.DataFrame:
        path = DATA_DIR / "hei.csv"
        assert path.exists(), f"hei.csv not found at {path}"
        return pd.read_csv(path)

    def test_has_required_columns(self, hei_df: pd.DataFrame) -> None:
        missing = set(HEI_REQUIRED_COLUMNS) - set(hei_df.columns)
        assert not missing, f"Missing columns: {missing}"

    def test_not_empty(self, hei_df: pd.DataFrame) -> None:
        assert len(hei_df) > 0, "hei.csv must contain at least one row"

    def test_no_duplicate_names(self, hei_df: pd.DataFrame) -> None:
        duplicates = hei_df["name"][hei_df["name"].duplicated()].tolist()
        assert not duplicates, f"Duplicate institution names: {duplicates}"

    def test_valid_types(self, hei_df: pd.DataFrame) -> None:
        invalid = set(hei_df["type"].dropna().unique()) - VALID_TYPES
        assert not invalid, f"Invalid types: {invalid}"

    def test_each_row_validates(self, hei_df: pd.DataFrame) -> None:
        errors: list[str] = []
        for idx, row in hei_df.iterrows():
            try:
                HEIRecord(
                    name=required_text_cell(row["name"]),
                    short_name=required_text_cell(row["short_name"]),
                    type=required_text_cell(row["type"]),
                    town=required_text_cell(row["town"]),
                    lat=row["lat"] if pd.notna(row["lat"]) else None,
                    lon=row["lon"] if pd.notna(row["lon"]) else None,
                )
            # Broad on purpose: collect every row's failure, not just the first.
            except Exception as exc:  # noqa: BLE001
                errors.append(f"Row {idx} ({row.get('name', '?')}): {exc}")
        assert not errors, "\n".join(errors)

    def test_signatory_values(self, hei_df: pd.DataFrame) -> None:
        allowed = {"Yes", "No"}
        for col in ("dora_signatory", "coara_signatory", "coara_member"):
            values = set(hei_df[col].dropna().unique())
            invalid = values - allowed
            assert not invalid, f"{col} has invalid values: {invalid}"

    def test_openalex_primary_ids_align_with_aliases(
        self,
        hei_df: pd.DataFrame,
    ) -> None:
        errors: list[str] = []
        for idx, row in hei_df.iterrows():
            primary_id = required_text_cell(row.get("openalex_primary_id", "")).strip()
            openalex_ids = split_identifier_cell(row.get("openalex_ids", ""))

            if primary_id and primary_id not in openalex_ids:
                errors.append(
                    f"Row {idx} ({row.get('name', '?')}): openalex_primary_id '{primary_id}' "
                    "must be included in openalex_ids"
                )

            if openalex_ids and not primary_id:
                errors.append(
                    f"Row {idx} ({row.get('name', '?')}): missing openalex_primary_id "
                    "for row with openalex_ids"
                )

        assert not errors, "\n".join(errors)


class TestHEIChangelog:
    """Validate dashboards/_data/hei-changelog.json."""

    @pytest.fixture(scope="class")
    def hei_changelog(self) -> list[dict[str, object]]:
        assert HEI_CHANGELOG_PATH.exists(), (
            f"hei-changelog.json not found at {HEI_CHANGELOG_PATH}"
        )
        with HEI_CHANGELOG_PATH.open(encoding="utf-8") as handle:
            return json.load(handle)

    def test_not_empty(self, hei_changelog: list[dict[str, object]]) -> None:
        assert hei_changelog, "hei-changelog.json must contain at least one entry"

    def test_each_entry_validates(self, hei_changelog: list[dict[str, object]]) -> None:
        errors: list[str] = []
        for idx, entry in enumerate(hei_changelog):
            try:
                HEIChangelogEntry.model_validate(entry)
            # Broad on purpose: collect every entry's failure, not just the first.
            except Exception as exc:  # noqa: BLE001
                errors.append(f"Entry {idx}: {exc}")
        assert not errors, "\n".join(errors)

    def test_entries_are_sorted_by_date(
        self,
        hei_changelog: list[dict[str, object]],
    ) -> None:
        dates = [str(entry["date"]) for entry in hei_changelog]
        assert dates == sorted(dates), "HEI changelog entries must be date-sorted"


# ---------------------------------------------------------------------------
# Tests – tobi.csv
# ---------------------------------------------------------------------------


class TestTOBIData:
    """Validate dashboards/_data/tobi.csv."""

    @pytest.fixture(scope="class")
    def tobi_df(self) -> pd.DataFrame:
        path = DATA_DIR / "tobi.csv"
        assert path.exists(), f"tobi.csv not found at {path}"
        return pd.read_csv(path)

    def test_has_required_columns(self, tobi_df: pd.DataFrame) -> None:
        missing = set(TOBI_REQUIRED_COLUMNS) - set(tobi_df.columns)
        assert not missing, f"Missing columns: {missing}"

    def test_not_empty(self, tobi_df: pd.DataFrame) -> None:
        assert len(tobi_df) > 0, "tobi.csv must contain at least one row"

    def test_no_duplicate_names(self, tobi_df: pd.DataFrame) -> None:
        duplicates = tobi_df["name"][tobi_df["name"].duplicated()].tolist()
        assert not duplicates, f"Duplicate institution names: {duplicates}"

    def test_valid_types(self, tobi_df: pd.DataFrame) -> None:
        invalid = set(tobi_df["type"].dropna().unique()) - VALID_TYPES
        assert not invalid, f"Invalid types: {invalid}"

    def test_each_row_validates(self, tobi_df: pd.DataFrame) -> None:
        errors: list[str] = []
        for idx, row in tobi_df.iterrows():
            try:
                TOBIRecord(
                    name=required_text_cell(row["name"]),
                    short_name=required_text_cell(row["short_name"]),
                    type=required_text_cell(row["type"]),
                    town=required_text_cell(row["town"]),
                )
            # Broad on purpose: collect every row's failure, not just the first.
            except Exception as exc:  # noqa: BLE001
                errors.append(f"Row {idx} ({row.get('name', '?')}): {exc}")
        assert not errors, "\n".join(errors)

    def test_findability_values(self, tobi_df: pd.DataFrame) -> None:
        allowed = {"Yes", "No"}
        findability_cols = [
            c for c in tobi_df.columns if c.startswith("tobi_findable_")
        ]
        for col in findability_cols:
            values = set(tobi_df[col].dropna().unique())
            invalid = values - allowed
            assert not invalid, f"{col} has invalid values: {invalid}"

    def test_output_columns_numeric(self, tobi_df: pd.DataFrame) -> None:
        output_cols = [
            c for c in tobi_df.columns if c.startswith("tobi_total_outputs_")
        ]
        for col in output_cols:
            non_null = tobi_df[col].dropna()
            numeric = pd.to_numeric(non_null, errors="coerce")
            bad_count = numeric.isna().sum()
            assert bad_count == 0, f"{col} has {bad_count} non-numeric values"
