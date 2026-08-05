#!/usr/bin/env python3
"""Thin CLI: run the cryptanalysis helpers on a message and print results.

All logic lives in src/bond_utilities/ciphers.py; this script only parses
flags and renders output through src/bond_utilities/reporting.py.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bond_utilities.ciphers import (  # noqa: E402
    caesar_break,
    index_of_coincidence,
    kasiski_key_lengths,
    letter_frequency,
    vigenere_break,
)
from bond_utilities.reporting import banner, print_kv, print_table  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Cryptanalysis helpers on a message.")
    parser.add_argument("text", nargs="*", help="message text (defaults to QBRANCH)")
    parser.add_argument(
        "--vigenere-length",
        type=int,
        default=None,
        help="known Vigenere key length to break",
    )
    args = parser.parse_args()

    text = " ".join(args.text) if args.text else "QBRANCH"
    print(banner("CRYPTANALYSIS"))
    print_kv(
        [
            ("text", text),
            ("index_of_coincidence", f"{index_of_coincidence(text):.4f}"),
            ("kasiski_key_lengths", ", ".join(str(k) for k in kasiski_key_lengths(text))),
        ]
    )
    shift, plaintext = caesar_break(text)
    print_kv([("caesar_shift", str(shift)), ("caesar_plaintext", plaintext)])
    if args.vigenere_length is not None:
        key, decipher = vigenere_break(text, args.vigenere_length)
        print_kv([("vigenere_key", key), ("vigenere_plaintext", decipher)])
    counts = letter_frequency(text)
    print_table(
        [[letter, str(counts[letter])] for letter in sorted(counts)],
        headers=["letter", "count"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
