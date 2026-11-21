"""fractionkit：A4 可打印、可裁剪的分数条教具。"""

from __future__ import annotations

from .model import (
    BAR_WIDTH_MM,
    DEFAULT_MAX_DENOMINATOR,
    DEFAULT_TITLE,
    MAX_COPIES,
    MAX_DENOMINATOR,
    MAX_TITLE_LENGTH,
    MIN_COPIES,
    MIN_DENOMINATOR,
    ROWS_PER_PAGE,
    Bar,
    FractionKitError,
    Kit,
    Segment,
    build_segments,
    format_decimal,
    format_fraction,
    format_mm,
    format_percent,
    segment_width_mm,
    validate_copies,
    validate_denominator,
    validate_title,
)
from .render import bar_svg, render_html, segment_font_mm

__version__ = "0.1.0"

__all__ = [
    "BAR_WIDTH_MM",
    "DEFAULT_MAX_DENOMINATOR",
    "DEFAULT_TITLE",
    "MAX_COPIES",
    "MAX_DENOMINATOR",
    "MAX_TITLE_LENGTH",
    "MIN_COPIES",
    "MIN_DENOMINATOR",
    "ROWS_PER_PAGE",
    "Bar",
    "FractionKitError",
    "Kit",
    "Segment",
    "bar_svg",
    "build_segments",
    "format_decimal",
    "format_fraction",
    "format_mm",
    "format_percent",
    "render_html",
    "segment_font_mm",
    "segment_width_mm",
    "validate_copies",
    "validate_denominator",
    "validate_title",
    "__version__",
]
