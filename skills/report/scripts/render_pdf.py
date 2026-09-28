#!/usr/bin/env python3
"""Render a Markdown report to PDF with headless Chrome, then prove the PDF text layer matches the source.

Usage:
    python3 render_pdf.py report.md [-o report.pdf] [--css custom.css] [--keep-html]

Requires pandoc and Google Chrome / Chromium / Edge. The text-layer check needs pdftotext (poppler).
```mermaid fenced blocks are drawn by mermaid.js inside Chrome: loaded from the jsDelivr CDN, or from
a local mermaid.min.js named by the MERMAID_JS environment variable when the machine is offline.
Exit codes: 0 rendered and verified, 1 text layer or a diagram is wrong, 2 rendered but not verified.

Chrome is the renderer because WeasyPrint subsets Thai fonts with a broken glyph-to-Unicode map:
the page looks right, but extracted text turns "ภาพ" into "ภำพ" and detaches tone marks.
"""

import argparse
import html
import os
import shutil
import string
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CSS_PATH = SKILL_DIR / "assets" / "report.css"

# Dollar math and ~sub~/^super^ would swallow report text such as "$1,200" or "~3.5 s".
PANDOC_INPUT_FORMAT = "markdown-tex_math_dollars-subscript-superscript"

CHROME_NAMES_ON_PATH = [
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "microsoft-edge",
    "msedge",
]
CHROME_INSTALL_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
]

MERMAID_CDN_URL = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"
REPORT_FONT_STACK = '"Noto Sans", "Noto Sans Thai", "Helvetica Neue", Arial, "Thonburi", "Leelawadee UI", sans-serif'
# pandoc emits <pre class="mermaid"><code>...</code></pre>; mermaid reads innerHTML and rejects the
# <code> tag as a syntax error, so the diagram text is moved into a bare div before rendering.
MERMAID_SETUP_SCRIPT = """
for (const pre of document.querySelectorAll("pre.mermaid")) {
  const diagram = document.createElement("div");
  diagram.className = "mermaid";
  diagram.textContent = pre.textContent;
  pre.replaceWith(diagram);
}
mermaid.initialize({
  startOnLoad: false,
  theme: "neutral",
  fontFamily: '""" + REPORT_FONT_STACK + """',
  flowchart: { htmlLabels: false },
});
mermaid.run({ querySelector: "div.mermaid" });
"""
MERMAID_ERROR_TEXT = "Syntax error in text"

MAX_MISSING_TOKENS_SHOWN = 20
TOKEN_EDGE_CHARACTERS = string.punctuation + "“”‘’…–—•·│─┼├┤"


def main():
    args = parse_args()

    markdown_path = Path(args.markdown).resolve()
    if not markdown_path.is_file():
        sys.exit(f"error: markdown file not found: {markdown_path}")
    if args.output:
        pdf_path = Path(args.output).resolve()
    else:
        pdf_path = markdown_path.with_suffix(".pdf")
    css_path = Path(args.css).resolve() if args.css else DEFAULT_CSS_PATH

    pandoc_path = shutil.which("pandoc")
    if pandoc_path is None:
        sys.exit("error: pandoc not found on PATH — install it from https://pandoc.org/installing.html")
    chrome_path = find_chrome()

    # Stage 1: Markdown -> standalone HTML page
    body_html = run_command([pandoc_path, str(markdown_path), "--from", PANDOC_INPUT_FORMAT, "--to", "html5"])
    title = find_title(markdown_path)
    diagram_script = ""
    if '<pre class="mermaid">' in body_html:
        diagram_script = build_mermaid_script()
    page_html = build_page(body_html, title, css_path, markdown_path.parent, diagram_script)

    # Stage 2: HTML page -> PDF
    with tempfile.TemporaryDirectory() as work_dir:
        html_path = Path(work_dir) / "report.html"
        html_path.write_text(page_html, encoding="utf-8")
        print_pdf(chrome_path, html_path, pdf_path)
    if args.keep_html:
        pdf_path.with_suffix(".html").write_text(page_html, encoding="utf-8")
    print(f"wrote {pdf_path}")

    # Stage 3: prove the PDF text is extractable, matches the source, and every diagram rendered
    exit_code = verify_pdf(pandoc_path, markdown_path, pdf_path)
    sys.exit(exit_code)


def parse_args():
    parser = argparse.ArgumentParser(description="Render a Markdown report to a verified PDF.")
    parser.add_argument("markdown", help="path to the report .md file")
    parser.add_argument("-o", "--output", help="PDF path (default: next to the .md)")
    parser.add_argument("--css", help="stylesheet replacing the skill's assets/report.css")
    parser.add_argument("--keep-html", action="store_true", help="also write the intermediate .html beside the PDF")
    return parser.parse_args()


def find_chrome():
    configured_path = os.environ.get("CHROME_PATH")
    if configured_path:
        if not Path(configured_path).is_file():
            sys.exit(f"error: CHROME_PATH points to a missing file: {configured_path}")
        return configured_path

    for name in CHROME_NAMES_ON_PATH:
        found_path = shutil.which(name)
        if found_path:
            return found_path

    for candidate in CHROME_INSTALL_PATHS:
        if Path(candidate).is_file():
            return candidate

    sys.exit("error: no Chrome, Chromium, or Edge found — install one or set CHROME_PATH")


def find_title(markdown_path):
    for line in markdown_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return markdown_path.stem


def build_mermaid_script():
    configured_path = os.environ.get("MERMAID_JS")
    if not configured_path:
        return f'<script src="{MERMAID_CDN_URL}"></script>\n<script>{MERMAID_SETUP_SCRIPT}</script>\n'
    local_path = Path(configured_path).resolve()
    if not local_path.is_file():
        sys.exit(f"error: MERMAID_JS points to a missing file: {local_path}")
    return f'<script src="{local_path.as_uri()}"></script>\n<script>{MERMAID_SETUP_SCRIPT}</script>\n'


def build_page(body_html, title, css_path, asset_dir, diagram_script):
    css_text = css_path.read_text(encoding="utf-8")
    running_title = title.replace("\\", "\\\\").replace('"', '\\"')
    footer_rule = (
        "@page { @bottom-left { content: \"" + running_title + "\"; "
        "font-size: 8pt; color: #6b7280; } }"
    )
    # <base> makes relative image paths in the Markdown resolve from the report's own folder.
    return (
        "<!DOCTYPE html>\n"
        "<html>\n<head>\n"
        '<meta charset="utf-8">\n'
        f"<title>{html.escape(title)}</title>\n"
        f'<base href="{asset_dir.as_uri()}/">\n'
        f"<style>\n{css_text}\n{footer_rule}\n</style>\n"
        "</head>\n<body>\n"
        f"{body_html}\n"
        f"{diagram_script}"
        "</body>\n</html>\n"
    )


def print_pdf(chrome_path, html_path, pdf_path):
    command = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--allow-file-access-from-files",
        "--virtual-time-budget=15000",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]
    # --virtual-time-budget lets asynchronous diagram rendering finish before the page is printed.
    # No --user-data-dir: headless Chrome then uses a throwaway profile, while a fresh
    # explicit profile dir was observed to hang Chrome after the PDF is written.
    # Chrome refuses to start as root (common in containers) unless the sandbox is disabled.
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        command.insert(1, "--no-sandbox")

    if pdf_path.exists():
        pdf_path.unlink()
    run_command(command)
    if not pdf_path.is_file():
        sys.exit(f"error: Chrome finished but did not write {pdf_path}")


def verify_pdf(pandoc_path, markdown_path, pdf_path):
    pdftotext_path = shutil.which("pdftotext")
    if pdftotext_path is None:
        print("WARNING: pdftotext not found — PDF NOT verified. Install poppler, then re-run.")
        return 2

    markdown_text = markdown_path.read_text(encoding="utf-8")
    prose_markdown, diagram_first_lines = split_mermaid_blocks(markdown_text)
    source_text = run_command(
        [pandoc_path, "--from", PANDOC_INPUT_FORMAT, "--to", "plain", "--wrap=none"],
        input_text=prose_markdown,
    )
    pdf_text = run_command([pdftotext_path, "-enc", "UTF-8", str(pdf_path), "-"])
    # Line wrapping differs between source and PDF, so compare with all whitespace removed.
    searchable_pdf_text = squash_whitespace(pdf_text)

    # Check 1: every word and number of the prose survives into the text layer
    expected_tokens = collect_tokens(source_text)
    missing_tokens = []
    for token in expected_tokens:
        if squash_whitespace(token) not in searchable_pdf_text:
            missing_tokens.append(token)

    # Check 2: every diagram was drawn — raw Mermaid source or mermaid's error text means it was not
    diagram_problems = []
    if squash_whitespace(MERMAID_ERROR_TEXT) in searchable_pdf_text:
        diagram_problems.append(f'a diagram failed to parse ("{MERMAID_ERROR_TEXT}" is in the PDF)')
    for first_line in diagram_first_lines:
        if squash_whitespace(first_line) in searchable_pdf_text:
            diagram_problems.append(f'diagram "{first_line}" was printed as source text — mermaid.js did not run')

    if not missing_tokens and not diagram_problems:
        print(f"PDF OK: all {len(expected_tokens)} source tokens found, {len(diagram_first_lines)} diagram(s) rendered")
        return 0

    if missing_tokens:
        print(f"TEXT LAYER MISMATCH: {len(missing_tokens)} of {len(expected_tokens)} source tokens not found in the PDF")
        for token in missing_tokens[:MAX_MISSING_TOKENS_SHOWN]:
            print(f"  missing: {token}")
    for problem in diagram_problems:
        print(f"DIAGRAM PROBLEM: {problem}")
    return 1


def split_mermaid_blocks(markdown_text):
    """Return the Markdown without ```mermaid blocks, plus each block's first line.

    Diagram source is not prose, so it is excluded from the token check and verified separately.
    Fence length is tracked like pandoc does, so a mermaid example shown inside a longer
    ```` code fence stays ordinary code instead of counting as a diagram.
    """
    prose_lines = []
    diagram_first_lines = []
    open_fence = ""
    inside_diagram = False
    waiting_for_first_line = False
    for line in markdown_text.splitlines():
        stripped_line = line.strip()
        fence = leading_fence(stripped_line)

        # Outside any code block: a fence opens one
        if not open_fence:
            if fence:
                open_fence = fence
                inside_diagram = stripped_line[len(fence):].strip() == "mermaid"
                waiting_for_first_line = inside_diagram
            if not inside_diagram:
                prose_lines.append(line)
            continue

        # Inside a code block: only a bare fence of the same kind and at least the same length closes it
        closes_block = fence != "" and fence[0] == open_fence[0] and len(fence) >= len(open_fence)
        if closes_block and stripped_line == fence:
            open_fence = ""
            if not inside_diagram:
                prose_lines.append(line)
            inside_diagram = False
            continue

        if not inside_diagram:
            prose_lines.append(line)
        elif waiting_for_first_line and stripped_line:
            diagram_first_lines.append(stripped_line)
            waiting_for_first_line = False
    return "\n".join(prose_lines), diagram_first_lines


def leading_fence(stripped_line):
    for fence_character in ("`", "~"):
        run_length = len(stripped_line) - len(stripped_line.lstrip(fence_character))
        if run_length >= 3:
            return fence_character * run_length
    return ""


def collect_tokens(text):
    tokens = []
    seen = set()
    for raw_token in text.split():
        token = raw_token.strip(TOKEN_EDGE_CHARACTERS)
        has_letter_or_digit = any(character.isalnum() for character in token)
        if not has_letter_or_digit or token in seen:
            continue
        seen.add(token)
        tokens.append(token)
    return tokens


def squash_whitespace(text):
    normalized_text = unicodedata.normalize("NFKC", text)
    return "".join(normalized_text.split())


def run_command(command, input_text=None):
    # Chrome must get a closed stdin; pandoc reads its input from stdin when input_text is given.
    stdin_source = subprocess.DEVNULL if input_text is None else None
    try:
        result = subprocess.run(
            command,
            stdin=stdin_source,
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        sys.exit(f"error: {Path(command[0]).name} did not finish within 180 s")
    if result.returncode != 0:
        sys.exit(f"error: {Path(command[0]).name} exited {result.returncode}\n{result.stderr.strip()}")
    return result.stdout


if __name__ == "__main__":
    main()
