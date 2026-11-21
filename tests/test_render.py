"""HTML 渲染单元测试：页面、SVG 尺寸、转义与教学说明。"""

from __future__ import annotations

import re
import unittest
from fractions import Fraction
from typing import List

from fractionkit.model import FractionKitError, Kit
from fractionkit.render import bar_svg, render_html, segment_font_mm

SVG_PATTERN = re.compile(r'<svg class="bar".*?</svg>', re.S)


def split_pages(page: str) -> List[str]:
    return page.split('<section class="sheet"')[1:]


def first_svg(page: str, denominator: int) -> str:
    for block in SVG_PATTERN.findall(page):
        if "分母 %d 的分数条" % denominator in block:
            return block
    raise AssertionError("找不到分母 %d 的分数条" % denominator)


class DocumentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.page = render_html(Kit())

    def test_doctype_and_language(self) -> None:
        self.assertTrue(self.page.startswith("<!doctype html>"))
        self.assertIn('<html lang="zh-CN">', self.page)

    def test_has_viewport_and_charset(self) -> None:
        self.assertIn('<meta charset="utf-8">', self.page)
        self.assertIn('name="viewport"', self.page)

    def test_self_contained(self) -> None:
        for token in ("<script", "<link", "@import", "url(", "src="):
            self.assertNotIn(token, self.page)

    def test_a4_portrait_css(self) -> None:
        self.assertIn("@page { size: A4 portrait; margin: 0; }", self.page)
        self.assertIn("width: 210mm;", self.page)
        self.assertIn("height: 297mm;", self.page)

    def test_responsive_rules(self) -> None:
        self.assertIn("@media screen and (max-width: 860px)", self.page)
        self.assertIn("width: 100%;", self.page)
        self.assertIn("overflow-x: hidden;", self.page)

    def test_default_page_count(self) -> None:
        self.assertEqual(len(split_pages(self.page)), 2)

    def test_page_numbers(self) -> None:
        self.assertIn("第 1 / 2 页", self.page)
        self.assertIn("第 2 / 2 页", self.page)

    def test_title_repeats_on_every_page(self) -> None:
        for chunk in split_pages(self.page):
            self.assertIn("分数条教具", chunk)

    def test_toolbar_summary(self) -> None:
        self.assertIn("共 22 条", self.page)
        self.assertIn("2 套", self.page)


class EscapingTest(unittest.TestCase):
    def test_title_is_escaped(self) -> None:
        title = "<分数&条>"
        page = render_html(Kit(title=title))
        self.assertIn("&lt;分数&amp;条&gt;", page)
        self.assertNotIn("<分数", page)

    def test_title_in_title_tag_escaped(self) -> None:
        page = render_html(Kit(title='a"b'))
        self.assertIn("&quot;", page)


class SvgTest(unittest.TestCase):
    def setUp(self) -> None:
        self.page = render_html(Kit())

    def test_bar_count(self) -> None:
        self.assertEqual(len(SVG_PATTERN.findall(self.page)), 22)

    def test_svg_width_is_184mm(self) -> None:
        self.assertEqual(self.page.count('width="184mm"'), 22)
        self.assertNotIn("width: 184px", self.page)

    def test_bar_width_is_150mm(self) -> None:
        self.assertIn('width="150" height="11"', self.page)

    def test_row_height_is_15mm(self) -> None:
        self.assertIn('height="15mm"', self.page)

    def test_segment_rect_count(self) -> None:
        self.assertEqual(self.page.count('class="seg-'), 154)

    def test_whole_bar_label_on_every_row(self) -> None:
        self.assertEqual(self.page.count("1 整条 = 1"), 22)

    def test_dashed_cut_border(self) -> None:
        self.assertIn("stroke-dasharray: 1.2 1;", self.page)
        self.assertIn('class="cut"', self.page)

    def test_solid_divider(self) -> None:
        self.assertIn("svg.bar .divider { stroke: #334155; stroke-width: 0.25; }", self.page)

    def test_fraction_decimal_percent_labels(self) -> None:
        block = first_svg(self.page, 3)
        for text in ("1/3", "2/3", "0.333", "0.667", "33.3%", "66.7%"):
            self.assertIn(text, block)

    def test_unreduced_segment_label(self) -> None:
        block = first_svg(self.page, 4)
        self.assertIn("2/4", block)
        self.assertIn("0.5 50%", block)

    def test_sixteenth_labels(self) -> None:
        page = render_html(Kit(max_denominator=16, copies=1))
        block = first_svg(page, 16)
        self.assertIn("1/16", block)
        self.assertIn("0.063 6.3%", block)
        self.assertIn("15/16", block)
        self.assertIn("0.938 93.8%", block)
        self.assertIn("16/16", block)
        self.assertIn("1 100%", block)

    def test_segment_geometry_exact(self) -> None:
        block = first_svg(self.page, 3)
        self.assertIn('x="33" y="2" width="50" height="11"', block)
        self.assertIn('x="83" y="2" width="50" height="11"', block)
        self.assertIn('x="133" y="2" width="50" height="11"', block)

    def test_segment_widths_do_not_drift(self) -> None:
        page = render_html(Kit(max_denominator=16, copies=1))
        block = first_svg(page, 16)
        widths = re.findall(r'class="seg-[ab]" x="[0-9.]+" y="2" width="([0-9.]+)"', block)
        self.assertEqual(len(widths), 16)
        self.assertEqual(set(widths), {"9.375"})

    def test_font_shrinks_with_denominator(self) -> None:
        page = render_html(Kit(max_denominator=16, copies=1))
        wide = first_svg(self.page, 2)
        narrow = first_svg(page, 16)
        wide_fonts = [float(v) for v in re.findall(r'font-size="([0-9.]+)"', wide)]
        narrow_fonts = [float(v) for v in re.findall(r'font-size="([0-9.]+)"', narrow)]
        self.assertLess(min(narrow_fonts), min(wide_fonts))

    def test_parts_label_present(self) -> None:
        self.assertIn("分成 16 份", render_html(Kit(max_denominator=16, copies=1)))

    def test_two_line_text_structure(self) -> None:
        block = first_svg(self.page, 12)
        self.assertEqual(block.count("<tspan"), 2 * 12)
        self.assertIn('dy="0"', block)


class LayoutTest(unittest.TestCase):
    def test_copies_four_pages(self) -> None:
        page = render_html(Kit(max_denominator=16, copies=4))
        self.assertEqual(len(split_pages(page)), 5)

    def test_single_bar_kit(self) -> None:
        page = render_html(Kit(max_denominator=2, copies=1))
        self.assertEqual(len(SVG_PATTERN.findall(page)), 1)
        block = first_svg(page, 2)
        self.assertIn("1/2", block)
        self.assertIn("0.5 50%", block)
        self.assertEqual(page.count('class="seg-'), 2)

    def test_guide_only_on_last_page(self) -> None:
        pages = split_pages(render_html(Kit()))
        self.assertNotIn("怎么用", pages[0])
        self.assertIn("怎么用", pages[-1])

    def test_guide_mentions_three_activities(self) -> None:
        page = render_html(Kit(max_denominator=2, copies=1))
        for text in ("比大小", "找等值分数", "分数 · 小数 · 百分数对照", "沿虚线剪下"):
            self.assertIn(text, page)

    def test_header_range(self) -> None:
        page = render_html(Kit(max_denominator=8, copies=1))
        self.assertIn("1/2 – 1/8", page)

    def test_invalid_kit_type(self) -> None:
        with self.assertRaises(FractionKitError):
            render_html("kit")  # type: ignore[arg-type]

    def test_bar_svg_rejects_non_bar(self) -> None:
        with self.assertRaises(FractionKitError):
            bar_svg("bar")  # type: ignore[arg-type]


class FontSizingTest(unittest.TestCase):
    def test_wider_segment_gets_larger_font(self) -> None:
        wide = segment_font_mm(Fraction(75), 8)
        narrow = segment_font_mm(Fraction(150, 16), 11)
        self.assertGreater(wide, narrow)

    def test_font_is_clamped(self) -> None:
        self.assertEqual(segment_font_mm(Fraction(1, 100), 40), 1.3)
        self.assertEqual(segment_font_mm(Fraction(150), 1), 3.2)

    def test_font_fits_segment_width(self) -> None:
        width = Fraction(150, 16)
        font = segment_font_mm(width, 11)
        self.assertLessEqual(11 * font * 0.6, float(width) - 0.5)

    def test_invalid_chars(self) -> None:
        with self.assertRaises(FractionKitError):
            segment_font_mm(Fraction(10), 0)


if __name__ == "__main__":
    unittest.main()
