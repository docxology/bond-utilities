"""Classic cipher primitives used to protect mission codenames and payloads.

Every cipher here is an educational utility with a hard round-trip
guarantee: ``decrypt(encrypt(x)) == x`` for every supported input.
Cryptographic strength is explicitly out of scope — the suite uses these
for deterministic test vectors, obfuscation, and teaching classic
cryptography, never for real secrecy.

Ciphers:

- :func:`caesar_encrypt` / :func:`caesar_decrypt` — classic shift cipher,
  letters only, case preserved, non-letters pass through untouched.
- :func:`vigenere_encrypt` / :func:`vigenere_decrypt` — polyalphabetic
  cipher; the key advances only over letters.
- :func:`xor_bytes` — symmetric byte-wise XOR with a cyclically repeated key.
- :func:`one_time_pad` — XOR with a key at least as long as the data.
- :func:`generate_otp_key` — deterministic random key material from a seed.
- :func:`obfuscate_codename` / :func:`restore_codename` — letter+digit shift
  helper for codenames; :func:`codename_token` derives a stable token.
"""

from __future__ import annotations

import hashlib

from .randomness import derive_seed, make_rng

#: Canonical cipher names, used by reporting and manuscript variables.
CIPHER_NAMES = ("caesar", "vigenere", "one_time_pad", "xor")

_ALPHABET_SIZE = 26
_DIGIT_SIZE = 10


def _shift_letter(char: str, shift: int) -> str:
    """Shift one ASCII letter by ``shift`` positions, preserving case."""
    if not char.isalpha():
        return char
    base = ord("a") if char.islower() else ord("A")
    return chr(base + (ord(char) - base + shift) % _ALPHABET_SIZE)


def caesar_encrypt(text: str, shift: int) -> str:
    """Encrypt ``text`` with a Caesar shift (letters only, case preserved).

    Args:
        text: Plaintext (any characters; non-letters pass through).
        shift: Number of positions to shift; any integer is valid.

    Returns:
        The shifted ciphertext.
    """
    return "".join(_shift_letter(char, shift) for char in text)


def caesar_decrypt(text: str, shift: int) -> str:
    """Invert :func:`caesar_encrypt` for the same ``shift``."""
    return caesar_encrypt(text, -shift)


def _vigenere(text: str, key: str, encrypt: bool) -> str:
    """Shared Vigenère engine; only letters advance the key position."""
    if not key:
        raise ValueError("vigenere key must not be empty")
    if not key.isalpha():
        raise ValueError("vigenere key must contain only letters")
    out: list[str] = []
    key_index = 0
    direction = 1 if encrypt else -1
    for char in text:
        if not char.isalpha():
            out.append(char)
            continue
        shift = direction * (ord(key[key_index % len(key)].lower()) - ord("a"))
        out.append(_shift_letter(char, shift))
        key_index += 1
    return "".join(out)


def vigenere_encrypt(text: str, key: str) -> str:
    """Encrypt ``text`` with the Vigenère cipher.

    Args:
        text: Plaintext; non-letters pass through without advancing the key.
        key: Non-empty alphabetic keyword.

    Returns:
        The ciphertext.
    """
    return _vigenere(text, key, True)


def vigenere_decrypt(text: str, key: str) -> str:
    """Invert :func:`vigenere_encrypt` for the same ``key``."""
    return _vigenere(text, key, False)


def xor_bytes(data: bytes, key: bytes) -> bytes:
    """Byte-wise XOR of ``data`` with a cyclically repeated ``key``.

    Symmetric: ``xor_bytes(xor_bytes(data, key), key) == data``.

    Args:
        data: Payload bytes.
        key: Key bytes; must be non-empty.

    Returns:
        The XORed bytes, same length as ``data``.

    Raises:
        ValueError: If ``key`` is empty.
    """
    if not key:
        raise ValueError("xor key must not be empty")
    return bytes(byte ^ key[index % len(key)] for index, byte in enumerate(data))


def one_time_pad(data: bytes, key: bytes) -> bytes:
    """Apply a one-time pad: XOR ``data`` with a key at least as long.

    Only the first ``len(data)`` key bytes are consumed. Symmetric:
    ``one_time_pad(one_time_pad(data, key), key) == data``.

    Args:
        data: Payload bytes.
        key: Key bytes with ``len(key) >= len(data)``.

    Returns:
        The ciphertext bytes, same length as ``data``.

    Raises:
        ValueError: If the key is shorter than the data.
    """
    if len(key) < len(data):
        raise ValueError(f"one-time-pad key must be at least {len(data)} bytes, got {len(key)}")
    return bytes(a ^ b for a, b in zip(data, key))


def generate_otp_key(length: int, seed: int | str) -> bytes:
    """Generate a deterministic random key of ``length`` bytes from ``seed``.

    Args:
        length: Key length in bytes (>= 1).
        seed: Seed; strings are hashed via :func:`derive_seed`.

    Returns:
        Deterministic key bytes, reproducible for the same seed.

    Raises:
        ValueError: If ``length`` is less than 1.
    """
    if length < 1:
        raise ValueError("otp key length must be >= 1")
    rng = make_rng(seed)
    return bytes(rng.randrange(256) for _ in range(length))


def obfuscate_codename(codename: str, shift: int) -> str:
    """Shift letters and digits of ``codename`` by ``shift`` positions.

    Non-alphanumeric characters (spaces, hyphens) pass through unchanged, so
    hyphenated codenames keep their shape. Digits use a 10-position cycle.

    Args:
        codename: The codename to obfuscate.
        shift: Shift amount; any integer is valid.

    Returns:
        The obfuscated codename.
    """
    out: list[str] = []
    for char in codename:
        if char.isalpha():
            base = ord("a") if char.islower() else ord("A")
            out.append(chr(base + (ord(char) - base + shift) % _ALPHABET_SIZE))
        elif char.isdigit():
            out.append(chr(ord("0") + (ord(char) - ord("0") + shift) % _DIGIT_SIZE))
        else:
            out.append(char)
    return "".join(out)


def restore_codename(codename: str, shift: int) -> str:
    """Invert :func:`obfuscate_codename` for the same ``shift``."""
    return obfuscate_codename(codename, -shift)


def codename_token(name: str, seed: int | str, length: int = 6) -> str:
    """Derive a stable uppercase hex token for a codename.

    The token is a truncated SHA-256 digest over the derived seed and the
    name, so it is deterministic across runs and processes.

    Args:
        name: Codename or mission name.
        seed: Seed; strings are hashed via :func:`derive_seed`.
        length: Token length in hex characters (>= 1).

    Returns:
        Uppercase hex token of ``length`` characters.

    Raises:
        ValueError: If ``length`` is less than 1.
    """
    if length < 1:
        raise ValueError("token length must be >= 1")
    digest = hashlib.sha256(f"{derive_seed(seed)}:{name}".encode("utf-8")).hexdigest()
    return digest[:length].upper()


__all__ = [
    "CIPHER_NAMES",
    "caesar_encrypt",
    "caesar_decrypt",
    "vigenere_encrypt",
    "vigenere_decrypt",
    "xor_bytes",
    "one_time_pad",
    "generate_otp_key",
    "obfuscate_codename",
    "restore_codename",
    "codename_token",
]
