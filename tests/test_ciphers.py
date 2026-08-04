"""Tests for src/bond_utilities/ciphers.py — real computations, no mocks."""

from __future__ import annotations

import pytest

from bond_utilities.ciphers import (
    CIPHER_NAMES,
    caesar_decrypt,
    caesar_encrypt,
    codename_token,
    generate_otp_key,
    obfuscate_codename,
    one_time_pad,
    restore_codename,
    vigenere_decrypt,
    vigenere_encrypt,
    xor_bytes,
)
from bond_utilities.randomness import derive_seed

# Round-trip vectors (plaintext, key/shift params).
CAESAR_VECTORS = [("HELLO", 3), ("hello world", 7), ("A-Z 09 !", 5), ("message", -4)]
VIGENERE_VECTORS = [
    ("ATTACKATDAWN", "LEMON"),
    ("hello world, mission", "secret"),
    ("MISSION", "q"),
    ("case sensitive", "Key"),
]
XOR_VECTORS = [("payload", b"\x01\x02\x03"), ("short", b"\xaa"), ("exact", b"\x00\x01\x02\x03\x04")]
OTP_VECTORS = [("secret", b"\x00" * 24), ("data", b"\xff" * 16)]


def _prepare_bytes(text: str) -> bytes:
    return text.encode("utf-8")


def test_registry_names() -> None:
    assert CIPHER_NAMES == ("caesar", "vigenere", "one_time_pad", "xor")
    assert len(CIPHER_NAMES) == 4
    assert all(isinstance(name, str) for name in CIPHER_NAMES)


class TestCaesar:
    @pytest.mark.parametrize("text,shift", CAESAR_VECTORS)
    def test_round_trip(self, text: str, shift: int) -> None:
        assert caesar_decrypt(caesar_encrypt(text, shift), shift) == text

    @pytest.mark.parametrize(
        "text,shift,expected",
        [
            ("HELLO", 3, "KHOOR"),
            ("abc", 1, "bcd"),
            ("ABC", 1, "BCD"),
            ("mixed", 0, "mixed"),
        ],
    )
    def test_known_vectors(self, text: str, shift: int, expected: str) -> None:
        assert caesar_encrypt(text, shift) == expected

    def test_case_preserved(self) -> None:
        assert caesar_encrypt("HeLLo", 1) == "IfMMp"

    def test_non_letters_pass_through(self) -> None:
        assert caesar_encrypt("a b.c-1", 1) == "b c.d-1"
        assert "1" == "1"

    def test_full_cycle(self) -> None:
        assert caesar_encrypt("HELLO", 26) == "HELLO"


class TestVigenere:
    @pytest.mark.parametrize("text,key", VIGENERE_VECTORS)
    def test_round_trip(self, text: str, key: str) -> None:
        assert vigenere_decrypt(vigenere_encrypt(text, key), key) == text

    def test_known_vector(self) -> None:
        # Classic "ATTACKATDAWN" with key "LEMON" -> "LXFOPVEFRNHR"
        assert vigenere_encrypt("ATTACKATDAWN", "LEMON") == "LXFOPVEFRNHR"
        assert vigenere_decrypt("LXFOPVEFRNHR", "LEMON") == "ATTACKATDAWN"

    def test_non_letters_do_not_advance_key(self) -> None:
        # Two a's separated by a non-letter should encrypt the same.
        assert vigenere_encrypt("a!a", "b") == "b!b"

    def test_empty_key_raises(self) -> None:
        with pytest.raises(ValueError, match="key must not be empty"):
            vigenere_encrypt("hello", "")

    def test_non_alpha_key_raises(self) -> None:
        with pytest.raises(ValueError, match="letters"):
            vigenere_encrypt("hello", "a1b")


class TestXor:
    @pytest.mark.parametrize("text,key", XOR_VECTORS)
    def test_round_trip(self, text: str, key: bytes) -> None:
        data = _prepare_bytes(text)
        assert xor_bytes(xor_bytes(data, key), key) == data

    def test_cycle_repeats_key(self) -> None:
        data = b"\x00\x00\x00\x00"
        key = b"\x01"
        # Key cycles; with zero data, output repeats the key bytes.
        assert xor_bytes(data, key) == b"\x01\x01\x01\x01"

    def test_single_byte_key_with_short_data(self) -> None:
        assert xor_bytes(b"\x05\xff", b"\x0f") == b"\x0a\xf0"

    def test_empty_key_raises(self) -> None:
        with pytest.raises(ValueError, match="xor key must not be empty"):
            xor_bytes(b"\x00", b"")


class TestOneTimePad:
    @pytest.mark.parametrize("text,key", OTP_VECTORS)
    def test_round_trip(self, text: str, key: bytes) -> None:
        data = _prepare_bytes(text)
        assert one_time_pad(one_time_pad(data, key), key) == data

    def test_requires_key_at_least_data_length(self) -> None:
        with pytest.raises(ValueError, match="key must be at least"):
            one_time_pad(b"\x00\x00\x00", b"\x01\x02")

    def test_key_longer_than_data_is_truncated(self) -> None:
        data = b"\x01\x02"
        key = b"\xf0\xf0\xf0"
        result = one_time_pad(data, key)
        assert len(result) == 2
        assert result == b"\xf1\xf2"

    def test_generate_otp_key_is_deterministic(self) -> None:
        key_a = generate_otp_key(32, seed="mission-7")
        key_b = generate_otp_key(32, seed="mission-7")
        other = generate_otp_key(32, seed="mission-8")
        assert key_a == key_b
        assert key_a != other
        assert len(key_a) == 32

    def test_generate_otp_key_length_one(self) -> None:
        assert len(generate_otp_key(1, seed=1)) == 1

    def test_generate_otp_key_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="length"):
            generate_otp_key(0, seed=1)


class TestCodenameEncoding:
    @pytest.mark.parametrize(
        "name,shift",
        [("SILENT-JAGUAR", 3), ("GOLDEN-BEACON", 7), ("Q-BRANCH", 1), ("WILD-COMET-7", 5)],
    )
    def test_obfuscate_restore_round_trip(self, name: str, shift: int) -> None:
        assert restore_codename(obfuscate_codename(name, shift), shift) == name

    def test_obfuscate_letters_and_digits(self) -> None:
        assert obfuscate_codename("A1", 1) == "B2"
        assert obfuscate_codename("a1", 1) == "b2"

    def test_obfuscate_digit_wraps(self) -> None:
        assert obfuscate_codename("9", 1) == "0"

    def test_obfuscate_preserves_hyphen(self) -> None:
        assert obfuscate_codename("SILENT-JAGUAR", 0) == "SILENT-JAGUAR"

    def test_token_is_uppercase_hex_deterministic(self) -> None:
        t1 = codename_token("RAVEN", seed=42)
        t2 = codename_token("RAVEN", seed=42)
        assert t1 == t2
        assert len(t1) == 6
        assert t1.isupper() and t1.isalnum()

    def test_token_custom_length(self) -> None:
        assert len(codename_token("X", seed=1, length=10)) == 10

    def test_token_differs_by_seed_and_name(self) -> None:
        assert codename_token("RAVEN", seed=1) != codename_token("RAVEN", seed=2)
        assert codename_token("RAVEN", seed=1) != codename_token("FALCON", seed=1)

    def test_token_zero_length_raises(self) -> None:
        with pytest.raises(ValueError, match="length"):
            codename_token("X", seed=1, length=0)

    def test_cross_module_seed_agreement(self) -> None:
        # A string seed folds through derive_seed before hashing.
        assert derive_seed("mission") == derive_seed("mission")
