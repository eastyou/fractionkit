"""命令行入口单元测试：参数校验、退出码与输出内容。"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from typing import List, Tuple

from fractionkit.cli import main


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.target = self.root / "分数条教具.html"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_cli(self, argv: List[str]) -> Tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = main(argv)
        except SystemExit as exc:
            code = int(exc.code) if exc.code is not None else 0
        return code, out.getvalue(), err.getvalue()

    def test_generate(self) -> None:
        code, out, _ = self.run_cli(
            ["--max-denominator", "12", "--copies", "2", "-o", str(self.target)]
        )
        self.assertEqual(code, 0)
        self.assertTrue(self.target.exists())
        page = self.target.read_text(encoding="utf-8")
        self.assertIn("1/12", page)
        self.assertIn("怎么用", page)
        self.assertIn("已生成", out)

    def test_summary_output(self) -> None:
        code, out, _ = self.run_cli(["-o", str(self.target)])
        self.assertEqual(code, 0)
        self.assertIn("2 套", out)
        self.assertIn("共 22 条分数条", out)
        self.assertIn("2 页", out)

    def test_custom_title(self) -> None:
        code, _, _ = self.run_cli(
            ["--title", "五年级分数条", "-o", str(self.target)]
        )
        self.assertEqual(code, 0)
        self.assertIn(
            "五年级分数条", self.target.read_text(encoding="utf-8")
        )

    def test_custom_denominator_and_copies(self) -> None:
        code, out, _ = self.run_cli(
            ["--max-denominator", "16", "--copies", "4", "-o", str(self.target)]
        )
        self.assertEqual(code, 0)
        self.assertIn("共 60 条分数条", out)
        self.assertIn("5 页", out)

    def test_denominator_too_small(self) -> None:
        code, _, err = self.run_cli(
            ["--max-denominator", "1", "-o", str(self.target)]
        )
        self.assertEqual(code, 2)
        self.assertIn("2~16", err)
        self.assertFalse(self.target.exists())

    def test_denominator_too_large(self) -> None:
        code, _, err = self.run_cli(
            ["--max-denominator", "17", "-o", str(self.target)]
        )
        self.assertEqual(code, 2)
        self.assertIn("2~16", err)

    def test_denominator_not_integer(self) -> None:
        code, _, err = self.run_cli(
            ["--max-denominator", "abc", "-o", str(self.target)]
        )
        self.assertEqual(code, 2)
        self.assertIn("必须是整数", err)

    def test_denominator_decimal_text(self) -> None:
        code, _, err = self.run_cli(
            ["--max-denominator", "3.5", "-o", str(self.target)]
        )
        self.assertEqual(code, 2)
        self.assertIn("必须是整数", err)

    def test_copies_zero(self) -> None:
        code, _, err = self.run_cli(["--copies", "0", "-o", str(self.target)])
        self.assertEqual(code, 2)
        self.assertIn("1~4", err)

    def test_copies_too_many(self) -> None:
        code, _, err = self.run_cli(["--copies", "5", "-o", str(self.target)])
        self.assertEqual(code, 2)
        self.assertIn("1~4", err)

    def test_copies_not_integer(self) -> None:
        code, _, err = self.run_cli(["--copies", "两", "-o", str(self.target)])
        self.assertEqual(code, 2)
        self.assertIn("必须是整数", err)

    def test_title_empty(self) -> None:
        code, _, err = self.run_cli(["--title", "", "-o", str(self.target)])
        self.assertEqual(code, 2)
        self.assertIn("标题不能为空", err)

    def test_title_blank(self) -> None:
        code, _, err = self.run_cli(["--title", "   ", "-o", str(self.target)])
        self.assertEqual(code, 2)
        self.assertIn("标题不能为空", err)

    def test_title_too_long(self) -> None:
        code, _, err = self.run_cli(
            ["--title", "字" * 41, "-o", str(self.target)]
        )
        self.assertEqual(code, 2)
        self.assertIn("最多 40 个字符", err)

    def test_write_failure(self) -> None:
        missing = self.root / "missing_dir" / "out.html"
        code, _, err = self.run_cli(["-o", str(missing)])
        self.assertEqual(code, 1)
        self.assertIn("写入文件失败", err)

    def test_help(self) -> None:
        code, out, _ = self.run_cli(["--help"])
        self.assertEqual(code, 0)
        self.assertIn("分数条教具", out)
        self.assertIn("--max-denominator", out)

    def test_version(self) -> None:
        code, out, _ = self.run_cli(["--version"])
        self.assertEqual(code, 0)
        self.assertIn("fractionkit 0.1.0", out)

    def test_unknown_option(self) -> None:
        code, _, err = self.run_cli(["--unknown", "-o", str(self.target)])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_missing_option_value(self) -> None:
        code, _, err = self.run_cli(["--max-denominator"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_minimum_kit(self) -> None:
        code, _, _ = self.run_cli(
            ["--max-denominator", "2", "--copies", "1", "-o", str(self.target)]
        )
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        self.assertEqual(page.count('<svg class="bar"'), 1)
        self.assertIn("50%", page)


if __name__ == "__main__":
    unittest.main()
