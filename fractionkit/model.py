"""分数条数据模型：精确等分、数值格式化与分页规划。"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Tuple

MIN_DENOMINATOR = 2
MAX_DENOMINATOR = 16
DEFAULT_MAX_DENOMINATOR = 12
MIN_COPIES = 1
MAX_COPIES = 4
MAX_TITLE_LENGTH = 40

BAR_WIDTH_MM = Fraction(150, 1)
ROWS_PER_PAGE = 12
DEFAULT_TITLE = "分数条教具"


class FractionKitError(ValueError):
    """参数或数据不合法。"""


def validate_denominator(value: int) -> int:
    """校验分母是否为 2~16 的整数。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise FractionKitError("分母必须是整数")
    if not MIN_DENOMINATOR <= value <= MAX_DENOMINATOR:
        raise FractionKitError(
            "分母必须在 %d~%d 之间，当前是 %d"
            % (MIN_DENOMINATOR, MAX_DENOMINATOR, value)
        )
    return value


def validate_copies(value: int) -> int:
    """校验重复套数是否为 1~4 的整数。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise FractionKitError("套数必须是整数")
    if not MIN_COPIES <= value <= MAX_COPIES:
        raise FractionKitError(
            "套数必须在 %d~%d 之间，当前是 %d"
            % (MIN_COPIES, MAX_COPIES, value)
        )
    return value


def validate_title(value: str) -> str:
    """校验并规整标题：1~40 个字符。"""
    if not isinstance(value, str):
        raise FractionKitError("标题必须是文本")
    text = value.strip()
    if not text:
        raise FractionKitError("标题不能为空")
    if len(text) > MAX_TITLE_LENGTH:
        raise FractionKitError(
            "标题最多 %d 个字符，当前是 %d 个" % (MAX_TITLE_LENGTH, len(text))
        )
    return text


def _round_scaled(value: Fraction, places: int) -> int:
    """把分数按指定小数位四舍五入（half up），返回放大后的整数。"""
    if not isinstance(value, Fraction):
        raise FractionKitError("数值必须是 Fraction")
    if isinstance(places, bool) or not isinstance(places, int) or places < 0:
        raise FractionKitError("小数位数必须是非负整数")
    scale = 10 ** places
    scaled = value * scale
    quotient, remainder = divmod(scaled.numerator, scaled.denominator)
    if remainder * 2 >= scaled.denominator:
        quotient += 1
    return quotient


def _strip_fixed(scaled: int, places: int) -> str:
    """把放大后的整数还原成小数文本，并去掉多余的尾零。"""
    if places <= 0:
        return str(scaled)
    digits = str(scaled).rjust(places + 1, "0")
    whole = str(int(digits[:-places]))
    fraction = digits[-places:].rstrip("0")
    return whole + ("." + fraction if fraction else "")


def format_mm(value: Fraction) -> str:
    """毫米数值转文本，保留最多 3 位小数并去尾零。"""
    return _strip_fixed(_round_scaled(value, 3), 3)


def format_fraction(value: Fraction) -> str:
    """分数转文本，例如 ``1/3``；取值为整数时输出整数。"""
    if not isinstance(value, Fraction):
        raise FractionKitError("数值必须是 Fraction")
    if value.denominator == 1:
        return str(value.numerator)
    return "%d/%d" % (value.numerator, value.denominator)


def format_decimal(value: Fraction) -> str:
    """分数转小数文本，保留 3 位小数并去尾零。"""
    return _strip_fixed(_round_scaled(value, 3), 3)


def format_percent(value: Fraction) -> str:
    """分数转百分数文本，保留 1 位小数并去尾零。"""
    return _strip_fixed(_round_scaled(value * 100, 1), 1) + "%"


@dataclass(frozen=True)
class Segment:
    """一条分数条中的一段：位置与宽度都用 Fraction 精确表示。"""

    index: int
    denominator: int
    fraction: Fraction
    left_mm: Fraction
    width_mm: Fraction

    @property
    def label(self) -> str:
        """该段显示用的分数，保留分母写法，例如 2/4。"""
        return "%d/%d" % (self.index, self.denominator)


@dataclass(frozen=True)
class Bar:
    """一条分数条：分母与所有等分小段。"""

    denominator: int
    segments: Tuple[Segment, ...]


def build_segments(denominator: int) -> Tuple[Segment, ...]:
    """按分母把 150mm 均分，返回 1/n 到 n/n 的 n 段。"""
    denominator = validate_denominator(denominator)
    width = BAR_WIDTH_MM / denominator
    segments: List[Segment] = []
    for index in range(1, denominator + 1):
        segments.append(
            Segment(
                index=index,
                denominator=denominator,
                fraction=Fraction(index, denominator),
                left_mm=width * (index - 1),
                width_mm=width,
            )
        )
    return tuple(segments)


def segment_width_mm(denominator: int) -> Fraction:
    """每段宽度（mm），用 Fraction 精确计算。"""
    return BAR_WIDTH_MM / validate_denominator(denominator)


@dataclass(frozen=True)
class Kit:
    """一套完整的分数条教具配置。"""

    max_denominator: int = DEFAULT_MAX_DENOMINATOR
    copies: int = 2
    title: str = DEFAULT_TITLE

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "max_denominator", validate_denominator(self.max_denominator)
        )
        object.__setattr__(self, "copies", validate_copies(self.copies))
        object.__setattr__(self, "title", validate_title(self.title))

    def bars(self) -> Tuple[Bar, ...]:
        """按「第 1 套 1/2→1/n，第 2 套 …」的顺序生成全部分数条。"""
        bars: List[Bar] = []
        for _ in range(self.copies):
            for denominator in range(MIN_DENOMINATOR, self.max_denominator + 1):
                bars.append(Bar(denominator, build_segments(denominator)))
        return tuple(bars)

    def row_count(self) -> int:
        """总行数：每套从 1/2 到 1/n，共 n-1 条。"""
        return self.copies * (self.max_denominator - 1)

    def page_count(self) -> int:
        """按每页 12 行计算所需页数。"""
        return (self.row_count() + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE

    def pages(self) -> Tuple[Tuple[Bar, ...], ...]:
        """把分数条按页切分，最后一页可能不满。"""
        bars = self.bars()
        return tuple(
            bars[start:start + ROWS_PER_PAGE]
            for start in range(0, len(bars), ROWS_PER_PAGE)
        )
