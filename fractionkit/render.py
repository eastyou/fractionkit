"""把分数条教具渲染成自包含、可打印的 A4 纵向 HTML。"""

from __future__ import annotations

import html
from fractions import Fraction
from typing import List, Sequence

from .model import (
    BAR_WIDTH_MM,
    Bar,
    FractionKitError,
    Kit,
    Segment,
    format_decimal,
    format_mm,
    format_percent,
)

LABEL_WIDTH_MM = Fraction(32, 1)
ROW_WIDTH_MM = Fraction(184, 1)
ROW_HEIGHT_MM = Fraction(15, 1)
BAR_X_MM = LABEL_WIDTH_MM + Fraction(1, 1)
BAR_Y_MM = Fraction(2, 1)
BAR_HEIGHT_MM = Fraction(11, 1)

_MIN_FONT_MM = 1.3
_MAX_FONT_MM = 3.2
_CHAR_WIDTH_EM = 0.6
_SIDE_PADDING_MM = 1.0


def segment_font_mm(width_mm: Fraction, chars: int) -> float:
    """按段宽与单行最多字符数估算字号，保证文字不溢出。"""
    if not isinstance(width_mm, Fraction):
        raise FractionKitError("段宽必须是 Fraction")
    if isinstance(chars, bool) or not isinstance(chars, int) or chars < 1:
        raise FractionKitError("字符数必须是正整数")
    usable = max(0.5, float(width_mm) - _SIDE_PADDING_MM * 2)
    size = usable / (chars * _CHAR_WIDTH_EM)
    return min(_MAX_FONT_MM, max(_MIN_FONT_MM, size))


def _num2(value: float) -> str:
    return "%.2f" % value


def _label_markup(denominator: int) -> str:
    return (
        '<text class="whole" x="16" y="6.4" text-anchor="middle" '
        'font-size="2.5">1 整条 = 1</text>'
        '<text class="parts" x="16" y="9.7" text-anchor="middle" '
        'font-size="1.9">分成 {0} 份</text>'.format(denominator)
    )


def _segment_markup(segment: Segment) -> str:
    x_left = BAR_X_MM + segment.left_mm
    x_mid = x_left + segment.width_mm / 2
    second_line = "%s %s" % (
        format_decimal(segment.fraction),
        format_percent(segment.fraction),
    )
    chars = max(len(segment.label), len(second_line))
    font = segment_font_mm(segment.width_mm, chars)
    gap = max(1.9, font * 1.35)
    first_y = 7.5 - gap / 2 + font * 0.35
    fill_class = "seg-a" if segment.index % 2 == 1 else "seg-b"
    return (
        '<rect class="%s" x="%s" y="%s" width="%s" height="%s"/>'
        '<text class="fraction" x="%s" y="%s" text-anchor="middle" '
        'font-size="%s"><tspan x="%s" dy="0">%s</tspan>'
        '<tspan x="%s" dy="%s">%s</tspan></text>'
        % (
            fill_class,
            format_mm(x_left),
            format_mm(BAR_Y_MM),
            format_mm(segment.width_mm),
            format_mm(BAR_HEIGHT_MM),
            _num2(float(x_mid)),
            _num2(first_y),
            _num2(font),
            _num2(float(x_mid)),
            html.escape(segment.label),
            _num2(float(x_mid)),
            _num2(gap),
            html.escape(second_line),
        )
    )


def _divider_markup(segment: Segment) -> str:
    x = BAR_X_MM + segment.left_mm
    return (
        '<line class="divider" x1="%s" y1="%s" x2="%s" y2="%s"/>'
        % (
            format_mm(x),
            format_mm(BAR_Y_MM),
            format_mm(x),
            format_mm(BAR_Y_MM + BAR_HEIGHT_MM),
        )
    )


def bar_svg(bar: Bar) -> str:
    """渲染一条分数条（含左侧整条标注与虚线裁剪边框）。"""
    if not isinstance(bar, Bar):
        raise FractionKitError("bar 必须是 Bar 对象")
    pieces: List[str] = [
        '<rect class="cut" x="0.3" y="0.3" width="183.4" height="14.4" rx="1"/>',
        '<rect class="frame" x="%s" y="%s" width="%s" height="%s"/>'
        % (
            format_mm(BAR_X_MM),
            format_mm(BAR_Y_MM),
            format_mm(BAR_WIDTH_MM),
            format_mm(BAR_HEIGHT_MM),
        ),
    ]
    for segment in bar.segments:
        pieces.append(_segment_markup(segment))
        pieces.append(_divider_markup(segment))
    pieces.append(_label_markup(bar.denominator))
    return (
        '<svg class="bar" width="%dmm" height="%dmm" viewBox="0 0 %d %d" '
        'role="img" aria-label="%s" xmlns="http://www.w3.org/2000/svg">%s</svg>'
        % (
            int(ROW_WIDTH_MM),
            int(ROW_HEIGHT_MM),
            int(ROW_WIDTH_MM),
            int(ROW_HEIGHT_MM),
            html.escape("分母 %d 的分数条" % bar.denominator),
            "".join(pieces),
        )
    )


def _guide_markup() -> str:
    return (
        '<section class="guide"><h2>怎么用</h2><ul>'
        "<li><strong>比大小：</strong>把两条分数条左端对齐，"
        "占用长度更长的那条分数更大。</li>"
        "<li><strong>找等值分数：</strong>叠放 1/2 与 2/4、3/6，"
        "看哪些分割线正好对齐。</li>"
        "<li><strong>分数 · 小数 · 百分数对照：</strong>读同一条上的三段标注，"
        "例如 1/4 = 0.25 = 25%。</li>"
        "</ul>"
        '<p class="tip">沿虚线剪下分数条，按分母从小到大叠放，随时对照。</p>'
        "</section>"
    )


def _head_markup(kit: Kit) -> str:
    return (
        '<header class="head"><h1>%s</h1>'
        '<p class="sub">分数 · 小数 · 百分数对照 · 1/2 – 1/%d · %d 套</p>'
        "</header>"
        % (html.escape(kit.title), kit.max_denominator, kit.copies)
    )


def _foot_markup(page: int, total: int, pushed: bool) -> str:
    classes = "foot push" if pushed else "foot"
    return (
        '<footer class="%s"><span>fractionkit · A4 纵向 · 实际尺寸打印</span>'
        "<span>第 %d / %d 页</span></footer>" % (classes, page, total)
    )


def _page_markup(
    bars: Sequence[Bar],
    kit: Kit,
    page: int,
    total: int,
    with_guide: bool,
) -> str:
    rows = "".join(bar_svg(bar) for bar in bars)
    guide = _guide_markup() if with_guide else ""
    return (
        '<section class="sheet" aria-label="第 %d 页">%s'
        '<div class="rows">%s</div>%s%s</section>'
        % (
            page,
            _head_markup(kit),
            rows,
            guide,
            _foot_markup(page, total, not with_guide),
        )
    )


def render_html(kit: Kit) -> str:
    """生成完整 HTML 文档；不引用任何外部资源。"""
    if not isinstance(kit, Kit):
        raise FractionKitError("kit 必须是 Kit 对象")
    pages = kit.pages()
    total = len(pages)
    body: List[str] = []
    for index, bars in enumerate(pages, start=1):
        body.append(
            _page_markup(bars, kit, index, total, with_guide=index == total)
        )
    toolbar = (
        '<div class="toolbar"><strong>%s</strong>'
        "<span>1/2 – 1/%d · 共 %d 条 · %d 套</span></div>"
        % (
            html.escape(kit.title),
            kit.max_denominator,
            kit.row_count(),
            kit.copies,
        )
    )
    return (
        "<!doctype html>\n"
        '<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n"
        '<div class="board">%s%s</div>\n</body>\n</html>\n'
        % (html.escape(kit.title), _style(), toolbar, "".join(body))
    )


def _style() -> str:
    return """
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  html, body { overflow-x: hidden; }
  body {
    margin: 0;
    padding: 7mm 0 10mm;
    background: #e2e8f0;
    color: #0f172a;
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  }
  .board { width: 210mm; max-width: 100%; margin: 0 auto; }
  .toolbar {
    width: 210mm;
    max-width: 100%;
    margin: 0 auto 4mm;
    padding: 0 12mm;
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    justify-content: space-between;
    gap: 10px;
    color: #334155;
    font-size: 12px;
  }
  .toolbar strong { font-size: 15px; letter-spacing: 1px; overflow-wrap: anywhere; }
  .toolbar span { color: #64748b; font-size: 12px; }
  .sheet {
    width: 210mm;
    height: 297mm;
    margin: 0 auto 7mm;
    padding: 12mm 12mm 10mm;
    background: #fff;
    box-shadow: 0 6px 22px rgba(15, 23, 42, 0.14);
    display: flex;
    flex-direction: column;
    page-break-after: always;
    break-after: page;
    overflow: hidden;
  }
  .sheet:last-child { page-break-after: auto; break-after: auto; }
  .head { text-align: center; margin-bottom: 3mm; }
  .head h1 {
    margin: 0;
    font-size: 15pt;
    font-weight: 600;
    letter-spacing: 2pt;
    overflow-wrap: anywhere;
  }
  .head .sub { margin: 1.2mm 0 0; font-size: 8.5pt; color: #475569; }
  .rows { display: flex; flex-direction: column; gap: 1.5mm; min-width: 0; }
  svg.bar {
    display: block;
    width: 184mm;
    height: 15mm;
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  }
  svg.bar text { fill: #0f172a; }
  svg.bar .cut {
    fill: #fff;
    stroke: #94a3b8;
    stroke-width: 0.2;
    stroke-dasharray: 1.2 1;
  }
  svg.bar .frame { fill: none; stroke: #0f172a; stroke-width: 0.35; }
  svg.bar .divider { stroke: #334155; stroke-width: 0.25; }
  svg.bar .seg-a { fill: #eff6ff; }
  svg.bar .seg-b { fill: #ffffff; }
  svg.bar .whole { font-weight: 600; }
  svg.bar .parts { fill: #475569; }
  svg.bar .fraction { letter-spacing: 0; }
  .guide {
    margin-top: auto;
    padding-top: 3mm;
    border-top: 0.3mm dashed #94a3b8;
    font-size: 9pt;
    color: #334155;
  }
  .guide h2 {
    margin: 0 0 1.5mm;
    font-size: 11pt;
    letter-spacing: 1pt;
    color: #0f172a;
  }
  .guide ul { margin: 0; padding-left: 5mm; }
  .guide li { margin: 0.8mm 0; line-height: 1.55; overflow-wrap: anywhere; }
  .guide .tip { margin: 1.5mm 0 0; color: #64748b; font-size: 8.5pt; }
  .foot {
    padding-top: 2mm;
    display: flex;
    justify-content: space-between;
    font-size: 8pt;
    color: #64748b;
    border-top: 0.2mm solid #e2e8f0;
  }
  .foot.push { margin-top: auto; }
  @page { size: A4 portrait; margin: 0; }
  @media print {
    body { background: #fff; padding: 0; }
    .toolbar { display: none; }
    .sheet { margin: 0; box-shadow: none; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
  @media screen and (max-width: 860px) {
    body { padding: 4mm 0; background: #fff; }
    .toolbar { width: 100%; padding: 0 4mm; }
    .sheet {
      width: 100%;
      height: auto;
      min-height: 0;
      margin: 0 auto 5mm;
      padding: 6mm 4mm 7mm;
      box-shadow: none;
    }
    .head h1 { font-size: 16pt; }
    .rows { gap: 3mm; width: 100%; }
    svg.bar { width: 100%; max-width: 100%; height: auto; }
    .guide { font-size: 10pt; }
  }
"""
