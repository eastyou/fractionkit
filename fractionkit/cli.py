"""命令行入口：生成 A4 可打印的分数条教具。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import NoReturn, Optional, Sequence

from .model import (
    DEFAULT_MAX_DENOMINATOR,
    DEFAULT_TITLE,
    MAX_COPIES,
    MAX_DENOMINATOR,
    MAX_TITLE_LENGTH,
    MIN_COPIES,
    MIN_DENOMINATOR,
    FractionKitError,
    Kit,
    validate_title,
)
from .render import render_html

VERSION = "0.1.0"


class _Parser(argparse.ArgumentParser):
    """把 argparse 的错误提示也改成中文。"""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, "错误: %s\n" % message)


def _int_arg(text: str, option: str, low: int, high: int) -> int:
    try:
        value = int(text)
    except (TypeError, ValueError):
        raise FractionKitError("%s 必须是整数" % option)
    if not low <= value <= high:
        raise FractionKitError(
            "%s 必须在 %d~%d 之间，当前是 %d" % (option, low, high, value)
        )
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="fractionkit",
        description="分数条教具：生成 A4 可打印、可裁剪的分数/小数/百分数对照卡",
    )
    parser.add_argument("--version", action="version", version="fractionkit " + VERSION)
    parser.add_argument(
        "--max-denominator",
        default=str(DEFAULT_MAX_DENOMINATOR),
        metavar="N",
        help="最大分母，%d~%d，默认 %d"
        % (MIN_DENOMINATOR, MAX_DENOMINATOR, DEFAULT_MAX_DENOMINATOR),
    )
    parser.add_argument(
        "--copies",
        default="2",
        metavar="N",
        help="整套重复次数，%d~%d，默认 2" % (MIN_COPIES, MAX_COPIES),
    )
    parser.add_argument(
        "--title",
        default=DEFAULT_TITLE,
        help="页面标题，1~%d 个字符，默认「%s」" % (MAX_TITLE_LENGTH, DEFAULT_TITLE),
    )
    parser.add_argument(
        "-o",
        "--output",
        default="分数条教具.html",
        help="输出 HTML 路径，默认「分数条教具.html」",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        kit = Kit(
            max_denominator=_int_arg(
                args.max_denominator,
                "--max-denominator",
                MIN_DENOMINATOR,
                MAX_DENOMINATOR,
            ),
            copies=_int_arg(args.copies, "--copies", MIN_COPIES, MAX_COPIES),
            title=validate_title(args.title),
        )
        page = render_html(kit)
    except FractionKitError as exc:
        parser.error(str(exc))
        return 2

    try:
        Path(args.output).write_text(page, encoding="utf-8")
    except OSError as exc:
        print("错误: 写入文件失败: %s" % exc, file=sys.stderr)
        return 1

    print(
        "已生成 %s：%d 套，共 %d 条分数条，%d 页"
        % (args.output, kit.copies, kit.row_count(), kit.page_count())
    )
    print("用浏览器打开后按 Ctrl/Cmd + P，纸张选 A4 纵向、缩放 100% 即可打印")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
