#!/usr/bin/env python3
"""Tek satıra sıkıştırılmış Lua kodunu okunabilir hale getirir (heuristic formatter)."""

from __future__ import annotations

import argparse
from pathlib import Path

OPENERS = {"do", "then", "function", "repeat"}
CLOSERS = {"end", "until"}
MID = {"else", "elseif"}


def is_ident_char(ch: str) -> bool:
    return ch.isalnum() or ch == "_"


def tokenize(src: str) -> list[str]:
    out: list[str] = []
    i = 0
    n = len(src)
    while i < n:
        ch = src[i]

        if ch in " \t\r\n":
            i += 1
            continue

        if ch in ('"', "'"):
            q = ch
            j = i + 1
            esc = False
            while j < n:
                c = src[j]
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == q:
                    j += 1
                    break
                j += 1
            out.append(src[i:j])
            i = j
            continue

        if ch == "-" and i + 1 < n and src[i + 1] == "-":
            j = i + 2
            while j < n and src[j] != "\n":
                j += 1
            out.append(src[i:j])
            i = j
            continue

        if is_ident_char(ch):
            j = i + 1
            while j < n and is_ident_char(src[j]):
                j += 1
            out.append(src[i:j])
            i = j
            continue

        # Çok karakterli operatörler
        if i + 1 < n and src[i : i + 2] in {"<=", ">=", "==", "~=", ".."}:
            out.append(src[i : i + 2])
            i += 2
            continue

        out.append(ch)
        i += 1

    return out


def format_lua(src: str) -> str:
    tokens = tokenize(src)
    indent = 0
    line: list[str] = []
    lines: list[str] = []

    def flush() -> None:
        nonlocal line
        txt = "".join(line).strip()
        if txt:
            lines.append("    " * max(indent, 0) + txt)
        line = []

    prev = ""
    for tok in tokens:
        low = tok.lower()

        if low in CLOSERS:
            flush()
            indent -= 1

        if low in MID:
            flush()
            indent -= 1
            lines.append("    " * max(indent, 0) + tok)
            indent += 1
            prev = tok
            continue

        if tok == ";":
            line.append(tok)
            flush()
            prev = tok
            continue

        # Basit spacing kuralı
        if line and tok not in {",", ")", "]", "}", ";"} and prev not in {"(", "[", "{"}:
            if prev not in {"", ".", ":"} and tok not in {".", ":", ".."}:
                line.append(" ")
        line.append(tok)

        if low in OPENERS:
            flush()
            indent += 1
        elif tok == "," and len("".join(line)) > 120:
            flush()
        elif low == "return":
            # devasa return satırlarını böl
            flush()

        prev = tok

    flush()
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    src = args.input.read_text(encoding="utf-8", errors="replace")
    formatted = format_lua(src)
    args.output.write_text(formatted, encoding="utf-8")
    print(f"Okunabilir çıktı yazıldı: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
