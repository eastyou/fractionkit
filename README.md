# fractionkit

[![CI](https://github.com/eastyou/fractionkit/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/fractionkit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

分数条教具生成器：一条命令生成 A4 纵向、可打印、可裁剪的分数条，让分数、小数、百分数在同一根条上对齐。**零第三方依赖，不联网，打印即用。**

每条分数条宽 150mm，按分母精确等分。每段同时标注分数（如 `1/3`）、小数（`0.333`）和百分数（`33.3%`），字号随分母增大自动缩小。学生可以剪下来叠放、比长短、找等值分数。

## 特性

- **1/2 到 1/N**：`--max-denominator` 控制最大分母（2~16），默认生成 1/2~1/12 共 11 条
- **精确等分**：用 `fractions.Fraction` 计算段宽与位置，不使用浮点累加，150mm 条宽不漂移
- **三值对照**：每段显示分数、小数（3 位小数去尾零）和百分数（1 位小数去尾零）
- **自动字号**：段越窄字号越小，最多两行，不溢出
- **裁剪友好**：虚线裁剪边框、实线分割线，左侧标注「1 整条 = 1」
- **整套重复**：`--copies 1~4` 一次打印多套，方便小组分发
- **自动分页**：每页 12 条，重复标题并标注页码，最后一页附「怎么用」
- **A4 纵向**：屏幕自适应不横向溢出，打印保持真实毫米尺寸
- **严格校验**：参数越界或非整数给出中文错误，退出码 2；写入失败退出码 1
- **114 个单元测试**：覆盖精确分段、数值格式、边界参数、分页、HTML 转义与命令行

## 安装

```bash
pip install .
```

也可以直接下载源码，在项目目录里运行：

```bash
python -m fractionkit --help
```

要求 Python 3.9 及以上，仅使用标准库。

## 用法

生成默认教具（1/2~1/12，两套）：

```bash
python -m fractionkit --max-denominator 12 --copies 2 --title 分数条教具 -o examples/分数条教具.html
```

再用浏览器打开生成的 HTML，按 `Ctrl/Cmd + P` 打印。

### 参数

| 参数 | 说明 | 范围 / 默认 |
| --- | --- | --- |
| `--max-denominator` | 最大分母，生成 1/2 到 1/N | 2~16，默认 12 |
| `--copies` | 整套重复次数 | 1~4，默认 2 |
| `--title` | 页面标题，每页重复显示 | 1~40 字，默认「分数条教具」 |
| `-o, --output` | 输出 HTML 路径 | 默认 `分数条教具.html` |
| `--version` | 查看版本 | — |
| `-h, --help` | 查看帮助 | — |

### 退出码

| 退出码 | 含义 |
| --- | --- |
| 0 | 生成成功 |
| 1 | 写入文件失败（如目录不存在、无权限） |
| 2 | 参数非法（非整数、越界、标题为空或过长） |

## 打印与裁剪

1. 浏览器打印设置里选择 **A4 纵向**。
2. 缩放选择 **100% / 实际大小**，不要选「适合页面」，否则毫米尺寸会变。
3. 边距选「默认」或「无」；勾选「背景图形」可保留浅色分段底色。
4. 沿每条外侧的**虚线**剪下，保留左侧「1 整条 = 1」标注。
5. 用直尺抽检：每条分割后的总长应为 150mm。

打印后可以按分母从小到大叠放，或把同一套分给不同小组。

## 教学用法

- **比大小**：把两条分数条左端对齐，占用更长的那条分数更大；也可与 1/2 条对比。
- **找等值分数**：叠放 1/2 与 2/4、3/6、4/8，观察哪些分割线正好对齐。
- **分数 · 小数 · 百分数对照**：读同一段上的三个标注，例如 1/4 = 0.25 = 25%，1/3 ≈ 0.333 = 33.3%。
- **凑整**：用 1/3 + 1/3 + 1/3、1/4 + 1/4 + 1/4 + 1/4 拼回「1 整条」。
- **小组分发**：`--copies 4` 一次打印四套，按组分剪。

## 项目结构

```text
fractionkit/
├── fractionkit/
│   ├── model.py    # Fraction 精确分段、数值格式化、分页
│   ├── render.py   # A4 纵向 HTML/CSS/SVG 排版
│   ├── cli.py      # 参数校验与命令行入口
│   └── __main__.py # python -m fractionkit
├── tests/          # 114 个单元测试
├── examples/       # 示例教具 HTML
└── .github/workflows/ci.yml
```

## 开发

```bash
python -m unittest discover -s tests
python -m fractionkit --max-denominator 12 --copies 2 -o examples/分数条教具.html
```

CI 在 Ubuntu / macOS / Windows 的 Python 3.10 与 3.13 上运行，并额外覆盖 Ubuntu 22.04 + Python 3.9。

## 许可证

[MIT](LICENSE) © 2026 eastyou
