#!/usr/bin/env python3
"""Basit Lua VM obfuscation çözücü yardımcı aracı.

Bu araç özellikle tek satırlık, `return(function(...) local q={...}` şeklinde başlayan
Lua scriptlerinde ilk aşama string çözümlemesini çalıştırır.

Nasıl çalışır:
1) Kaynak metinden `local q={...}` ile başlayan başlangıç bölümünü çıkarır.
2) VM gövdesi başlamadan önce (ikinci `return(function(q,O,Y,...)`) keser.
3) Bu bölümü geçici bir Lua dosyasında çalıştırıp çözülmüş `q` tablosunu dışarı alır.

Not: Çalışması için sistemde `lua` veya `luajit` bulunmalıdır.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VM_MARKER = "return(function(q,O,Y,s,i,l,L,V,G,v,P,e,k,u,U,g,t,D,X,p,a,H)"
TABLE_MARKER = "local q={"


def pick_lua_runtime() -> str | None:
    for candidate in ("lua", "luajit", "lua5.4", "lua5.3", "lua5.2", "lua5.1"):
        if shutil.which(candidate):
            return candidate
    return None


def extract_bootstrap(source: str) -> str:
    start = source.find(TABLE_MARKER)
    if start == -1:
        raise ValueError("`local q={` bulunamadı.")

    marker = source.find(VM_MARKER)
    if marker == -1:
        raise ValueError("VM başlangıç işareti bulunamadı.")

    return source[start:marker]


def build_probe_chunk(bootstrap: str) -> str:
    return (
        "(function(...)\n"
        + bootstrap
        + "\n"
        + "for idx, value in ipairs(q) do\n"
        + "  io.write(tostring(idx), '\\t', tostring(value), '\\n')\n"
        + "end\n"
        + "end)()\n"
    )


def run_probe(lua_runtime: str, chunk: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".lua", delete=False) as tf:
        tf.write(chunk)
        probe_path = tf.name

    try:
        result = subprocess.run(
            [lua_runtime, probe_path],
            text=True,
            capture_output=True,
            check=False,
        )
    finally:
        Path(probe_path).unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError(
            "Lua çalıştırması başarısız oldu:\n"
            f"STDERR:\n{result.stderr.strip()}\n"
            f"STDOUT:\n{result.stdout.strip()}"
        )

    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description="Obfuscate edilmiş Lua scriptte q tablosunu çözer.")
    parser.add_argument("input", type=Path, help="Çözülmek istenen Lua dosyası")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("decoded_q_table.txt"),
        help="Çözülmüş q tablosunun yazılacağı dosya",
    )
    args = parser.parse_args()

    runtime = pick_lua_runtime()
    if not runtime:
        print(
            "Hata: Bu araç için sistemde bir Lua runtime gerekli (lua/luajit).",
            file=sys.stderr,
        )
        return 2

    source = args.input.read_text(encoding="utf-8", errors="replace")
    bootstrap = extract_bootstrap(source)
    chunk = build_probe_chunk(bootstrap)
    decoded = run_probe(runtime, chunk)

    args.output.write_text(decoded, encoding="utf-8")
    print(f"Çözülen q tablosu yazıldı: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
