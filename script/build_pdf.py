import html
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MD_PATH = REPO_ROOT / "docs" / "course_report.md"
HTML_PATH = REPO_ROOT / "docs" / "course_report.html"
PDF_PATH = REPO_ROOT / "docs" / "course_report.pdf"


def fmt_math(s: str) -> str:
    repl = [
        (r"\text{TPOT}", "TPOT"),
        (r"\text{draft}", "draft"),
        (r"\text{verify}", "verify"),
        (r"\text{net}", "net"),
        (r"\text{post}", "post"),
        (r"\text{overlap}", "overlap"),
        (r"\text{pro}", "pro"),
        (r"\text{wait}", "wait"),
        (r"\text{5060Ti}", "5060Ti"),
        (r"\text{M4}", "M4"),
        (r"\text{B}", "B"),
        (r"\text{ ms}", " ms"),
        (r"\text{–}", "–"),
        (r"\mathbb{E}", "E"),
        (r"\mathrm{d}", "d"),
        (r"\ln", "ln"),
        (r"\tau", "τ"),
        (r"\rho", "ρ"),
        (r"\alpha", "α"),
        (r"\gamma", "γ"),
        (r"\kappa", "κ"),
        (r"\gg", "≫"),
        (r"\approx", "≈"),
        (r"\le", "≤"),
        (r"\in", "∈"),
        (r"\cdot", "·"),
        (r"\big(", "("),
        (r"\big)", ")"),
        (r"\{", "{"),
        (r"\}", "}"),
        (r"\,", " "),
        (r"\ ", " "),
    ]
    for a, b in repl:
        s = s.replace(a, b)
    s = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", s)
    s = re.sub(r"\^\{([^}]+)\}", r"<sup>\1</sup>", s)
    return s


def fmt_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\$([^$]+)\$", lambda m: f'<span class="math">{fmt_math(m.group(1))}</span>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text.replace("&lt;br&gt;", "<br>")


def build():
    lines = MD_PATH.read_text(encoding="utf-8").splitlines()
    out = []
    in_ul = False
    in_ol = False
    in_table = False
    table_rows = []

    def flush_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def flush_table():
        nonlocal in_table, table_rows
        if not in_table:
            return
        out.append("<table>")
        for idx, row in enumerate(table_rows):
            cells = [c.strip() for c in row.strip("|").split("|")]
            if idx == 1 and all(set(c.replace(":", "").replace("-", "")) == set() for c in cells):
                continue
            tag = "th" if idx == 0 else "td"
            out.append("<tr>" + "".join(f"<{tag}>{fmt_inline(c)}</{tag}>" for c in cells) + "</tr>")
        out.append("</table>")
        in_table = False
        table_rows = []

    for line in lines:
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            flush_lists()
            in_table = True
            table_rows.append(s)
            continue
        flush_table()
        if not s:
            flush_lists()
            continue
        if s == "---":
            flush_lists()
            out.append("<hr>")
        elif s.startswith("$$") and s.endswith("$$"):
            flush_lists()
            eq = s[2:-2].strip()
            eq = re.sub(
                r"\\frac\{(.+?)\}\{(.+?)\}",
                r'<span class="frac"><span class="num">\1</span><span class="den">\2</span></span>',
                eq,
            )
            out.append(f'<div class="eq-block">{fmt_math(eq)}</div>')
        elif s.startswith("!["):
            flush_lists()
            m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", s)
            if m:
                alt, src = m.group(1), m.group(2)
                out.append(f'<figure><img src="{src}" alt="{html.escape(alt)}"><figcaption>{html.escape(alt)}</figcaption></figure>')
        elif s.startswith("### "):
            flush_lists()
            out.append(f"<h3>{fmt_inline(s[4:])}</h3>")
        elif s.startswith("## "):
            flush_lists()
            out.append(f"<h2>{fmt_inline(s[3:])}</h2>")
        elif s.startswith("# "):
            flush_lists()
            out.append(f"<h1>{fmt_inline(s[2:])}</h1>")
        elif s.startswith("> "):
            flush_lists()
            out.append(f"<blockquote>{fmt_inline(s[2:])}</blockquote>")
        elif s.startswith("- "):
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{fmt_inline(s[2:])}</li>")
        elif re.match(r"^\d+\.\s+", s):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f'<li>{fmt_inline(re.sub(r"^\d+\.\s+", "", s))}</li>')
        else:
            flush_lists()
            out.append(f"<p>{fmt_inline(s)}</p>")

    flush_table()
    flush_lists()

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<style>
@page {{ size: A4; margin: 17mm 17mm 17mm 17mm; }}
body {{ font-family: "Microsoft YaHei", "PingFang SC", "SimSun", sans-serif; font-size: 10pt; line-height: 1.65; color: #1f2937; max-width: 820px; margin: 0 auto; }}
h1 {{ font-size: 16.5pt; color: #1B365D; text-align: center; margin-bottom: 6px; line-height: 1.35; }}
h2 {{ font-size: 12.5pt; color: #1B365D; border-bottom: 1.5px solid #1B365D; padding-bottom: 3px; margin-top: 18px; page-break-after: avoid; }}
h3 {{ font-size: 10.8pt; color: #2A9D8F; margin-top: 13px; page-break-after: avoid; }}
p {{ text-align: justify; margin: 6px 0; }}
blockquote {{ border-left: 3.5px solid #E07A5F; background: #FFF8F5; padding: 8px 12px; margin: 10px 0; color: #333; }}
code {{ background: #F1F5F9; padding: 1px 4px; border-radius: 3px; font-family: Consolas, monospace; font-size: 9pt; }}
.math {{ font-family: "Cambria Math", "Times New Roman", serif; font-style: italic; }}
.eq-block {{ text-align: center; margin: 10px 0; padding: 8px 12px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 4px; font-family: "Cambria Math", "Times New Roman", serif; font-size: 10.8pt; }}
.frac {{ display: inline-flex; flex-direction: column; vertical-align: middle; text-align: center; margin: 0 4px; }}
.frac .num {{ border-bottom: 1px solid #222; padding: 0 4px 2px; }}
.frac .den {{ padding: 2px 4px 0; }}
table {{ width: 100%; border-collapse: collapse; margin: 10px 0 14px; font-size: 8.5pt; page-break-inside: avoid; }}
th {{ background: #1B365D; color: white; padding: 6px 5px; text-align: center; font-weight: 600; }}
td {{ border-bottom: 1px solid #D1D5DB; padding: 5px 5px; text-align: center; }}
tr:nth-child(even) td {{ background: #F8FAFC; }}
td:first-child, th:first-child {{ text-align: left; }}
figure {{ text-align: center; margin: 12px 0 14px; page-break-inside: avoid; }}
figure img {{ max-width: 96%; height: auto; border: 1px solid #E5E7EB; border-radius: 4px; }}
figcaption {{ font-size: 8.8pt; color: #4B5563; margin-top: 4px; font-weight: 600; }}
ul, ol {{ margin: 5px 0 8px 18px; padding-left: 10px; }}
li {{ margin: 3px 0; }}
hr {{ border: none; border-top: 1px solid #CBD5E1; margin: 10px 0; }}
</style></head><body>{"".join(out)}</body></html>"""

    HTML_PATH.write_text(doc, encoding="utf-8")
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={PDF_PATH}",
            HTML_PATH.as_uri(),
        ],
        check=True,
    )
    HTML_PATH.unlink(missing_ok=True)
    print(f"BUILT PDF: {PDF_PATH} ({PDF_PATH.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    build()
