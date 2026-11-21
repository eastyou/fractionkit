"""分数条数据模型单元测试：精确分段、格式化与分页。"""

from __future__ import annotations

import unittest
from fractions import Fraction

from fractionkit.model import (
    BAR_WIDTH_MM,
    MAX_TITLE_LENGTH,
    ROWS_PER_PAGE,
    FractionKitError,
    Kit,
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


class SegmentTest(unittest.TestCase):
    def test_segment_count_matches_denominator(self) -> None:
        for denominator in range(2, 17):
            segments = build_segments(denominator)
            self.assertEqual(len(segments), denominator)

    def test_segments_are_equal_width(self) -> None:
        for denominator in range(2, 17):
            widths = {seg.width_mm for seg in build_segments(denominator)}
            self.assertEqual(len(widths), 1)

    def test_width_is_exact_fraction(self) -> None:
        self.assertEqual(segment_width_mm(3), Fraction(50, 1))
        self.assertEqual(segment_width_mm(7), Fraction(150, 7))
        self.assertIsInstance(segment_width_mm(7), Fraction)

    def test_widths_sum_to_bar_width(self) -> None:
        for denominator in range(2, 17):
            total = sum(
                (seg.width_mm for seg in build_segments(denominator)),
                Fraction(0, 1),
            )
            self.assertEqual(total, BAR_WIDTH_MM)

    def test_left_positions_are_exact(self) -> None:
        segments = build_segments(3)
        self.assertEqual(
            [seg.left_mm for seg in segments],
            [Fraction(0, 1), Fraction(50, 1), Fraction(100, 1)],
        )
        seventh = build_segments(7)
        for index, seg in enumerate(seventh):
            self.assertEqual(seg.left_mm, Fraction(150 * index, 7))

    def test_fraction_values(self) -> None:
        segments = build_segments(3)
        self.assertEqual(
            [seg.fraction for seg in segments],
            [Fraction(1, 3), Fraction(2, 3), Fraction(1, 1)],
        )
        for seg in segments:
            self.assertEqual(seg.fraction, Fraction(seg.index, seg.denominator))

    def test_labels_keep_original_denominator(self) -> None:
        labels = [seg.label for seg in build_segments(4)]
        self.assertEqual(labels, ["1/4", "2/4", "3/4", "4/4"])

    def test_invalid_denominator_in_segments(self) -> None:
        for value in (1, 17, 0, -3):
            with self.assertRaises(FractionKitError):
                build_segments(value)

    def test_invalid_denominator_in_width(self) -> None:
        with self.assertRaises(FractionKitError):
            segment_width_mm(17)


class FormatterTest(unittest.TestCase):
    def test_format_mm_integer(self) -> None:
        self.assertEqual(format_mm(Fraction(50, 1)), "50")

    def test_format_mm_three_decimals(self) -> None:
        self.assertEqual(format_mm(Fraction(150, 7)), "21.429")
        self.assertEqual(format_mm(Fraction(1, 3)), "0.333")

    def test_format_mm_rounds_half_up(self) -> None:
        self.assertEqual(format_mm(Fraction(1, 6)), "0.167")
        self.assertEqual(format_mm(Fraction(2, 3)), "0.667")

    def test_format_fraction_simple(self) -> None:
        self.assertEqual(format_fraction(Fraction(2, 3)), "2/3")

    def test_format_fraction_integer(self) -> None:
        self.assertEqual(format_fraction(Fraction(4, 2)), "2")

    def test_format_fraction_rejects_text(self) -> None:
        with self.assertRaises(FractionKitError):
            format_fraction("1/2")  # type: ignore[arg-type]

    def test_decimal_third(self) -> None:
        self.assertEqual(format_decimal(Fraction(1, 3)), "0.333")

    def test_decimal_half_without_trailing_zero(self) -> None:
        self.assertEqual(format_decimal(Fraction(1, 2)), "0.5")

    def test_decimal_quarter(self) -> None:
        self.assertEqual(format_decimal(Fraction(1, 4)), "0.25")

    def test_decimal_sixteenth(self) -> None:
        self.assertEqual(format_decimal(Fraction(1, 16)), "0.063")

    def test_decimal_two_thirds(self) -> None:
        self.assertEqual(format_decimal(Fraction(2, 3)), "0.667")

    def test_decimal_rejects_non_fraction(self) -> None:
        with self.assertRaises(FractionKitError):
            format_decimal(0.5)  # type: ignore[arg-type]

    def test_percent_third(self) -> None:
        self.assertEqual(format_percent(Fraction(1, 3)), "33.3%")

    def test_percent_half(self) -> None:
        self.assertEqual(format_percent(Fraction(1, 2)), "50%")

    def test_percent_sixteenth(self) -> None:
        self.assertEqual(format_percent(Fraction(1, 16)), "6.3%")

    def test_percent_sixth(self) -> None:
        self.assertEqual(format_percent(Fraction(1, 6)), "16.7%")

    def test_percent_eighth(self) -> None:
        self.assertEqual(format_percent(Fraction(1, 8)), "12.5%")

    def test_percent_rejects_non_fraction(self) -> None:
        with self.assertRaises(FractionKitError):
            format_percent(25)  # type: ignore[arg-type]


class ValidationTest(unittest.TestCase):
    def test_denominator_valid_range(self) -> None:
        for value in range(2, 17):
            self.assertEqual(validate_denominator(value), value)

    def test_denominator_too_small(self) -> None:
        with self.assertRaises(FractionKitError):
            validate_denominator(1)

    def test_denominator_too_large(self) -> None:
        with self.assertRaises(FractionKitError):
            validate_denominator(17)

    def test_denominator_not_integer_text(self) -> None:
        with self.assertRaises(FractionKitError):
            validate_denominator("3")  # type: ignore[arg-type]

    def test_denominator_float(self) -> None:
        with self.assertRaises(FractionKitError):
            validate_denominator(3.0)  # type: ignore[arg-type]

    def test_denominator_bool(self) -> None:
        with self.assertRaises(FractionKitError):
            validate_denominator(True)

    def test_copies_valid_range(self) -> None:
        for value in range(1, 5):
            self.assertEqual(validate_copies(value), value)

    def test_copies_too_small(self) -> None:
        with self.assertRaises(FractionKitError):
            validate_copies(0)

    def test_copies_too_large(self) -> None:
        with self.assertRaises(FractionKitError):
            validate_copies(5)

    def test_copies_bool(self) -> None:
        with self.assertRaises(FractionKitError):
            validate_copies(False)

    def test_title_strips_spaces(self) -> None:
        self.assertEqual(validate_title("  分数条  "), "分数条")

    def test_title_max_length(self) -> None:
        title = "字" * MAX_TITLE_LENGTH
        self.assertEqual(validate_title(title), title)

    def test_title_too_long(self) -> None:
        with self.assertRaises(FractionKitError):
            validate_title("字" * (MAX_TITLE_LENGTH + 1))

    def test_title_empty(self) -> None:
        with self.assertRaises(FractionKitError):
            validate_title("")

    def test_title_blank(self) -> None:
        with self.assertRaises(FractionKitError):
            validate_title("   ")

    def test_title_not_text(self) -> None:
        with self.assertRaises(FractionKitError):
            validate_title(123)  # type: ignore[arg-type]

    def test_error_is_value_error(self) -> None:
        self.assertTrue(issubclass(FractionKitError, ValueError))


class KitTest(unittest.TestCase):
    def test_defaults(self) -> None:
        kit = Kit()
        self.assertEqual(kit.max_denominator, 12)
        self.assertEqual(kit.copies, 2)
        self.assertEqual(kit.title, "分数条教具")

    def test_bars_order(self) -> None:
        kit = Kit(max_denominator=3, copies=2)
        self.assertEqual(
            [bar.denominator for bar in kit.bars()],
            [2, 3, 2, 3],
        )

    def test_bar_count(self) -> None:
        self.assertEqual(len(Kit(max_denominator=12, copies=2).bars()), 22)

    def test_row_count(self) -> None:
        self.assertEqual(Kit(max_denominator=12, copies=3).row_count(), 33)
        self.assertEqual(Kit(max_denominator=2, copies=1).row_count(), 1)

    def test_page_count_single_page(self) -> None:
        self.assertEqual(Kit(max_denominator=2, copies=1).page_count(), 1)

    def test_page_count_default(self) -> None:
        self.assertEqual(Kit().page_count(), 2)

    def test_page_count_maximum(self) -> None:
        self.assertEqual(Kit(max_denominator=16, copies=4).page_count(), 5)

    def test_pages_chunks_partial_last(self) -> None:
        pages = Kit(max_denominator=16, copies=1).pages()
        self.assertEqual([len(page) for page in pages], [ROWS_PER_PAGE, 3])

    def test_pages_chunks_full_last(self) -> None:
        pages = Kit(max_denominator=16, copies=4).pages()
        self.assertEqual([len(page) for page in pages], [12, 12, 12, 12, 12])

    def test_page_count_matches_pages(self) -> None:
        for denominator in (2, 5, 12, 16):
            for copies in (1, 2, 3, 4):
                kit = Kit(max_denominator=denominator, copies=copies)
                self.assertEqual(kit.page_count(), len(kit.pages()))

    def test_invalid_kit_denominator(self) -> None:
        with self.assertRaises(FractionKitError):
            Kit(max_denominator=1)

    def test_invalid_kit_title(self) -> None:
        with self.assertRaises(FractionKitError):
            Kit(title="")


if __name__ == "__main__":
    unittest.main()
