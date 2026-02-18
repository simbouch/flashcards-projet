from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor


RED_TODO = RGBColor(0xC0, 0x00, 0x00)


class HtmlToDocx(HTMLParser):
    def __init__(self, doc: Document):
        super().__init__(convert_charrefs=True)
        self.doc = doc
        self.block_stack: list[tuple[str, set[str]]] = []
        self.segments: list[tuple[str, bool, bool]] = []  # (text, is_todo, mono)
        self.in_todo = False
        self.in_code = False
        self.in_pre = False

    @staticmethod
    def _classes(attrs) -> set[str]:
        d = dict(attrs)
        raw = d.get("class", "")
        return {c for c in raw.split() if c}

    def handle_starttag(self, tag, attrs):
        classes = self._classes(attrs)

        if tag == "div" and "pagebreak" in classes:
            self.doc.add_page_break()
            return

        if tag == "span" and "todo" in classes:
            self.in_todo = True
            return

        if tag == "code":
            self.in_code = True

        if tag == "pre":
            self.in_pre = True

        # Start a new block only for tags we explicitly map
        if tag in {"h1", "h2", "h3", "h4", "p", "li", "pre"}:
            self._start_block(tag, classes)
        elif tag == "div" and ("big" in classes or "mid" in classes or "small" in classes or "figure" in classes):
            self._start_block(tag, classes)

    def handle_endtag(self, tag):
        if tag == "span" and self.in_todo:
            self.in_todo = False
            return

        if tag == "code":
            self.in_code = False

        if tag == "pre":
            self.in_pre = False

        if self.block_stack and self.block_stack[-1][0] == tag:
            _, classes = self.block_stack.pop()
            self._flush_block(tag, classes)

    def handle_data(self, data):
        text = data.replace("\r", "")
        if not text:
            return
        self.segments.append((text, self.in_todo, self.in_pre or self.in_code))

    def _start_block(self, tag: str, classes: set[str]):
        # If a previous block is still open, we keep collecting (nested tags), but
        # the actual flush happens on endtag for the outer block.
        self.block_stack.append((tag, classes))

    def _flush_block(self, tag: str, classes: set[str]):
        raw_text = "".join(t for t, _, _ in self.segments)
        text = raw_text.strip()
        if not text:
            self.segments.clear()
            return

        if tag in {"h1", "h2", "h3", "h4"}:
            level = int(tag[1])
            self.doc.add_heading(text, level=level)
            self.segments.clear()
            return

        if tag == "pre":
            p = self.doc.add_paragraph()
            # Preserve line breaks for code blocks
            code_text = raw_text.strip("\n")
            lines = code_text.split("\n")
            for i, line in enumerate(lines):
                run = p.add_run(line)
                run.font.name = "Consolas"
                run.font.size = Pt(10)
                if i < len(lines) - 1:
                    run.add_break()
            self.segments.clear()
            return

        if tag == "li":
            p = self.doc.add_paragraph(style="List Bullet")
        else:
            p = self.doc.add_paragraph()

        # Styling for special div blocks
        if tag == "div" and ("big" in classes or "mid" in classes or "small" in classes):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if tag == "div" and "figure" in classes:
            p.style = "Quote"

        # Apply font size for cover blocks
        size = None
        if tag == "div" and "big" in classes:
            size = Pt(18)
        elif tag == "div" and "mid" in classes:
            size = Pt(13)
        elif tag == "div" and "small" in classes:
            size = Pt(11)

        # Write runs with red TODO and monospace where needed
        for chunk, is_todo, mono in self.segments:
            if not chunk:
                continue
            run = p.add_run(chunk)
            if size is not None:
                run.font.size = size
            if is_todo:
                run.font.color.rgb = RED_TODO
                run.bold = True
            if mono:
                run.font.name = "Consolas"

        self.segments.clear()


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert E1 Word-friendly HTML report to .docx")
    ap.add_argument("--in", dest="inp", default="e1/docs/rapport_e1_word.html")
    ap.add_argument("--out", dest="out", default="e1/docs/rapport_e1_KHRIBECH_B.docx")
    args = ap.parse_args()

    inp = Path(args.inp)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    html = inp.read_text(encoding="utf-8")
    doc = Document()

    # Slightly nicer default
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    parser = HtmlToDocx(doc)
    parser.feed(html)
    doc.save(out)
    print(f"[OK] Wrote: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

