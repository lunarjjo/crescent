#!/usr/bin/env python3
"""Regenerasi EXAMPLES.md — jalankan setiap contoh, rekam outputnya.

Deterministik: tidak ada contoh yang memakai clock()/random().
Dipakai lokal maupun CI (lihat .github/workflows/ci.yml).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from crescent import run_source  # noqa: E402

GAL = os.path.join(HERE, "examples")
OUT = os.path.join(HERE, "EXAMPLES.md")

ORDER = [
    "fizzbuzz.cres",
    "fibonacci.cres",
    "closures.cres",
    "higher_order.cres",
    "primes.cres",
    "wordcount.cres",
    "matrix.cres",
    "agent_memory.cres",
]

TITLES = {
    "fizzbuzz.cres": "FizzBuzz — kontrol alir klasik",
    "fibonacci.cres": "Fibonacci — rekursi + memoization via closure",
    "closures.cres": "Closures — counter berbagi vs per instansi",
    "higher_order.cres": "Fungsi orde tinggi — map/filter/reduce/sort",
    "primes.cres": "Sieve of Eratosthenes — array & loop while",
    "wordcount.cres": "Word count — map + string tools",
    "matrix.cres": "Matriks — array nested & indeks",
    "agent_memory.cres": "Mini memory bank — 'luna' dalam 50 baris Crescent",
}


def main():
    parts = [
        "# Contoh Program Crescent",
        "",
        "Setiap contoh di bawah ini **dijalankan sungguhan** oleh interpreter",
        "saat dokumen ini diregenerasi — output yang tampil adalah output",
        "asli VM, bukan ditulis tangan.",
        "",
    ]
    for fname in ORDER:
        path = os.path.join(GAL, fname)
        src = open(path, encoding="utf-8").read()
        out = []
        run_source(src, print_fn=out.append)
        parts.append("---")
        parts.append("")
        parts.append("## {0}".format(TITLES.get(fname, fname)))
        parts.append("")
        parts.append("```crescent")
        parts.append(src.rstrip())
        parts.append("```")
        parts.append("")
        parts.append("Output:")
        parts.append("")
        parts.append("```")
        parts.append("\n".join(out))
        parts.append("```")
        parts.append("")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(parts) + "\n")
    print("EXAMPLES.md diregenerasi dari {0} contoh".format(len(ORDER)))


if __name__ == "__main__":
    main()
