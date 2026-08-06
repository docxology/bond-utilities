"""Tests for src/bond_utilities/ciphers.py — real computations, no mocks."""

from __future__ import annotations

import pytest

from bond_utilities.ciphers import (
    CIPHER_DESCRIPTIONS,
    CIPHER_NAMES,
    CRYPTANALYSIS_HELPERS,
    ENGLISH_FREQUENCIES,
    atbash,
    beaufort_decrypt,
    beaufort_encrypt,
    caesar_break,
    caesar_decrypt,
    caesar_encrypt,
    caesar_shift_scores,
    codename_token,
    columnar_decrypt,
    columnar_encrypt,
    english_chi_squared,
    frequency_normalized,
    generate_otp_key,
    index_of_coincidence,
    kasiski_key_lengths,
    letter_frequency,
    obfuscate_codename,
    one_time_pad,
    playfair_decrypt,
    playfair_encrypt,
    rail_fence_decrypt,
    rail_fence_encrypt,
    restore_codename,
    vigenere_break,
    vigenere_decrypt,
    vigenere_encrypt,
    xor_bytes,
)
from bond_utilities.randomness import derive_seed, seeded_bytes

# Long, letter-rich English pangram paragraph for frequency-based cryptanalysis.
_LONG = (
    "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGANDTHENGATHERSGRACEFULACORNS"
    "FROMEVERYMAPLETREEBYTHERIVERBANKWHILETHEHUNTERSLEEPSSILENTLYIN"
    "THESHADOWOFTHECASTLECLOCKTOWERCOUNTINGTHEMINUTESUNTILTHEDAWN"
    "BREAKSOVERHORIZON"
)

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
BEAUFORT_VECTORS = [("ATTACKATDAWN", "LEMON"), ("mission", "key"), ("hello world", "secret")]
RAIL_VECTORS = [("HELLOWORLD", 2), ("QBRANCH", 3), ("a c e", 4), ("MISSIONIMPOSED", 7)]
PLAYFAIR_VECTORS = [("ATTACKATDAWN", "MONARCHY"), ("HIDETHEGOLD", "LEMON"), ("QB7", "KEY"), ("REPEATEDLL", "SQUARE")]
COLUMNAR_VECTORS = [("HELLOWORLD", "3142"), ("QBRANCH", "21"), ("MISSION", "12"), ("", "42")]


def _prepare_bytes(text: str) -> bytes:
    return text.encode("utf-8")


class TestRegistry:
    def test_cipher_names(self) -> None:
        assert CIPHER_NAMES == (
            "caesar",
            "vigenere",
            "one_time_pad",
            "xor",
            "atbash",
            "beaufort",
            "rail_fence",
            "playfair",
            "columnar",
        )

    def test_descriptions_and_helpers(self) -> None:
        assert set(CIPHER_DESCRIPTIONS) == set(CIPHER_NAMES)
        assert "caesar_break" in CRYPTANALYSIS_HELPERS
        assert abs(sum(ENGLISH_FREQUENCIES.values()) - 1.0) < 1e-3
        assert set(ENGLISH_FREQUENCIES) == {chr(code) for code in range(ord("a"), ord("z") + 1)}


#: Round-trip exercisers keyed by registered cipher name. The keys are compared
#: against ``CIPHER_NAMES`` below, so a cipher cannot enter the registry without
#: a real round-trip here, and cannot be removed from the registry while one
#: remains.
_ROUND_TRIPS: dict[str, object] = {
    "caesar": lambda: caesar_decrypt(caesar_encrypt("ATTACK AT DAWN", 5), 5) == "ATTACK AT DAWN",
    "vigenere": lambda: vigenere_decrypt(vigenere_encrypt("ATTACK AT DAWN", "LEMON"), "LEMON") == "ATTACK AT DAWN",
    "one_time_pad": lambda: one_time_pad(one_time_pad(b"secret", b"\x11" * 6), b"\x11" * 6) == b"secret",
    "xor": lambda: xor_bytes(xor_bytes(b"payload", b"\x01\x02"), b"\x01\x02") == b"payload",
    "atbash": lambda: atbash(atbash("HELLO")) == "HELLO",
    "beaufort": lambda: beaufort_decrypt(beaufort_encrypt("MISSION", "KEY"), "KEY") == "MISSION",
    "rail_fence": lambda: rail_fence_decrypt(rail_fence_encrypt("QBRANCH", 3), 3) == "QBRANCH",
    "playfair": lambda: playfair_decrypt(playfair_encrypt("HIDETHEGOLD", "LEMON"), "LEMON").startswith("HID"),
    "columnar": lambda: columnar_decrypt(columnar_encrypt("QBRANCH", "21"), "21") == "QBRANCH",
}

#: Public functions of ``ciphers`` that are neither a cipher entrypoint nor a
#: cryptanalysis helper. Together with the two registries this is an exhaustive
#: partition of the module's public function surface — see
#: :class:`TestRegistryBinding`.
_KEY_AND_CODENAME_UTILITIES = frozenset(
    {"generate_otp_key", "obfuscate_codename", "restore_codename", "codename_token"}
)


def _entrypoint_candidates(name: str) -> set[str]:
    """Names a registered cipher ``name`` may be implemented under."""
    return {name, f"{name}_encrypt", f"{name}_decrypt", f"{name}_bytes"}


class TestRegistryBinding:
    """`CIPHER_NAMES` / `CRYPTANALYSIS_HELPERS` bound to the module, not to copies.

    The literal tuple assertion above pins the *order* the manuscript CSV token
    renders. These tests pin the *content* against what the module actually
    defines and what the suite actually exercises, in both directions.
    """

    def test_every_registered_cipher_has_a_real_entrypoint(self) -> None:
        import bond_utilities.ciphers as module

        for name in CIPHER_NAMES:
            resolved = [
                candidate
                for candidate in _entrypoint_candidates(name)
                if callable(getattr(module, candidate, None)) and candidate in module.__all__
            ]
            assert resolved, f"CIPHER_NAMES entry {name!r} resolves to no exported callable"

    def test_every_registered_cipher_has_a_verified_round_trip(self) -> None:
        assert set(_ROUND_TRIPS) == set(CIPHER_NAMES)
        for name, check in _ROUND_TRIPS.items():
            assert check(), f"round trip failed for registered cipher {name!r}"  # type: ignore[operator]

    def test_every_encrypt_function_is_registered(self) -> None:
        """Reverse direction: a new ``*_encrypt`` must join `CIPHER_NAMES`."""
        import inspect

        import bond_utilities.ciphers as module

        discovered = {
            name[: -len("_encrypt")]
            for name, obj in vars(module).items()
            if name.endswith("_encrypt")
            and inspect.isfunction(obj)
            and getattr(obj, "__module__", "") == module.__name__
        }
        unregistered = discovered - set(CIPHER_NAMES)
        assert not unregistered, f"cipher entrypoints missing from CIPHER_NAMES: {sorted(unregistered)}"

    def test_every_registered_helper_is_a_real_exported_function(self) -> None:
        import inspect

        import bond_utilities.ciphers as module

        for name in CRYPTANALYSIS_HELPERS:
            attribute = getattr(module, name, None)
            assert inspect.isfunction(attribute), f"CRYPTANALYSIS_HELPERS names a non-function: {name}"
            assert name in module.__all__, f"CRYPTANALYSIS_HELPERS names an unexported helper: {name}"

    def test_public_function_surface_is_exhaustively_partitioned(self) -> None:
        """Reverse direction for both registries.

        Every public function of the module belongs to exactly one of: a
        registered cipher entrypoint, `CRYPTANALYSIS_HELPERS`, or the small
        explicit key/codename utility set. Adding a public function without
        classifying it fails here, so neither registry can silently fall behind
        the code the manuscript counts.
        """
        import inspect

        import bond_utilities.ciphers as module

        cipher_entrypoints = {candidate for name in CIPHER_NAMES for candidate in _entrypoint_candidates(name)}
        classified = cipher_entrypoints | set(CRYPTANALYSIS_HELPERS) | _KEY_AND_CODENAME_UTILITIES
        public_functions = {
            name
            for name in module.__all__
            if inspect.isfunction(getattr(module, name, None))
            and getattr(getattr(module, name), "__module__", "") == module.__name__
        }
        unclassified = public_functions - classified
        assert not unclassified, f"public ciphers functions in no registry and no utility set: {sorted(unclassified)}"
        stale = _KEY_AND_CODENAME_UTILITIES - public_functions
        assert not stale, f"utility set names functions that no longer exist: {sorted(stale)}"


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

    def test_full_cycle(self) -> None:
        assert caesar_encrypt("HELLO", 26) == "HELLO"


class TestVigenere:
    @pytest.mark.parametrize("text,key", VIGENERE_VECTORS)
    def test_round_trip(self, text: str, key: str) -> None:
        assert vigenere_decrypt(vigenere_encrypt(text, key), key) == text

    def test_known_vector(self) -> None:
        assert vigenere_encrypt("ATTACKATDAWN", "LEMON") == "LXFOPVEFRNHR"
        assert vigenere_decrypt("LXFOPVEFRNHR", "LEMON") == "ATTACKATDAWN"

    def test_non_letters_do_not_advance_key(self) -> None:
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
        assert xor_bytes(b"\x00\x00\x00\x00", b"\x01") == b"\x01\x01\x01\x01"

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
        assert one_time_pad(b"\x01\x02", b"\xf0\xf0\xf0") == b"\xf1\xf2"

    def test_generate_otp_key_deterministic_and_matches_seeded_bytes(self) -> None:
        assert generate_otp_key(32, seed="mission-7") == generate_otp_key(32, seed="mission-7")
        assert generate_otp_key(32, seed="mission-7") == seeded_bytes("mission-7", 32)
        assert generate_otp_key(32, seed="mission-7") != generate_otp_key(32, seed="mission-8")
        assert len(generate_otp_key(1, seed=1)) == 1
        with pytest.raises(ValueError, match="length"):
            generate_otp_key(0, seed=1)


class TestCodenameEncoding:
    @pytest.mark.parametrize(
        "name,shift",
        [("SILENT-JAGUAR", 3), ("GOLDEN-BEACON", 7), ("Q-BRANCH", 1), ("WILD-COMET-7", 5)],
    )
    def test_obfuscate_restore_round_trip(self, name: str, shift: int) -> None:
        assert restore_codename(obfuscate_codename(name, shift), shift) == name

    def test_obfuscate_letters_digits_case(self) -> None:
        assert obfuscate_codename("A1", 1) == "B2"
        assert obfuscate_codename("a1", 1) == "b2"
        assert obfuscate_codename("9", 1) == "0"
        assert obfuscate_codename("SILENT-JAGUAR", 0) == "SILENT-JAGUAR"

    def test_token(self) -> None:
        assert codename_token("RAVEN", seed=42) == codename_token("RAVEN", seed=42)
        assert len(codename_token("X", seed=1, length=10)) == 10
        assert codename_token("RAVEN", seed=1) != codename_token("FALCON", seed=1)
        with pytest.raises(ValueError, match="length"):
            codename_token("X", seed=1, length=0)


class TestAtbash:
    def test_known_vector(self) -> None:
        assert atbash("HELLO") == "SVOOL"

    def test_self_inverse(self) -> None:
        assert atbash(atbash("HELLO WORLD")) == "HELLO WORLD"

    def test_case_and_non_letters(self) -> None:
        assert atbash("AbC-7") == "ZyX-7"


class TestBeaufort:
    @pytest.mark.parametrize("text,key", BEAUFORT_VECTORS)
    def test_round_trip(self, text: str, key: str) -> None:
        ciphertext = beaufort_encrypt(text, key)
        assert beaufort_decrypt(ciphertext, key) == text

    def test_self_inverse(self) -> None:
        assert beaufort_encrypt("HELLO", "LEMON") == beaufort_decrypt("HELLO", "LEMON")

    def test_known_vector(self) -> None:
        # key 'A' -> c = (0 - p) mod 26, the reverse shift cipher.
        assert beaufort_encrypt("HELLO", "A") == "TWPPM"

    def test_errors(self) -> None:
        with pytest.raises(ValueError, match="key must not be empty"):
            beaufort_encrypt("HELLO", "")
        with pytest.raises(ValueError, match="letters"):
            beaufort_encrypt("HELLO", "a1")

    def test_non_letters_pass(self) -> None:
        assert beaufort_encrypt("a!a", "B") == "b!b"


class TestRailFence:
    @pytest.mark.parametrize("text,rails", RAIL_VECTORS)
    def test_round_trip(self, text: str, rails: int) -> None:
        assert rail_fence_decrypt(rail_fence_encrypt(text, rails), rails) == text

    def test_known_vector(self) -> None:
        # 3-rail, text "HELLOWORLD":
        assert rail_fence_encrypt("HELLOWORLD", 3) == "HOLELWRDLO"

    def test_two_rails(self) -> None:
        assert rail_fence_encrypt("HELLO", 2) == "HLOEL"

    def test_rails_too_small_raises(self) -> None:
        with pytest.raises(ValueError, match="rails"):
            rail_fence_encrypt("HELLO", 1)

    def test_encrypt_is_permutation(self) -> None:
        text = "QBRANCH MISSION"
        cipher = rail_fence_encrypt(text, 4)
        assert sorted(cipher) == sorted(text)


class TestPlayfair:
    @pytest.mark.parametrize("text,key", PLAYFAIR_VECTORS)
    def test_round_trip_vs_prepared(self, text: str, key: str) -> None:
        from bond_utilities.ciphers import _playfair_prepare

        prepared = _playfair_prepare(text)
        assert playfair_decrypt(playfair_encrypt(text, key), key) == prepared

    def test_clean_input_round_trip_exact(self) -> None:
        # No doubles, no J, even length -> exact round trip against input.
        text = "ATTACKATDAWN"
        assert playfair_decrypt(playfair_encrypt(text, "MONARCHY"), "MONARCHY") == text

    def test_identity_square_vector(self) -> None:
        # Identity keyed square orders A..Z (I/J merged):
        #   A B C D E / F G H I K / L M N O P / Q R S T U / V W X Y Z
        key = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
        # Same row -> shift right.
        assert playfair_encrypt("HI", key) == "IK"
        assert playfair_decrypt("IK", key) == "HI"
        # Same column -> shift down.
        assert playfair_encrypt("AF", key) == "FL"
        assert playfair_decrypt("FL", key) == "AF"
        # Rectangle -> swap corners.
        assert playfair_encrypt("HE", key) == "KC"
        assert playfair_decrypt("KC", key) == "HE"

    def test_odd_ciphertext_raises(self) -> None:
        with pytest.raises(ValueError, match="even"):
            playfair_decrypt("ABC", "KEY")

    def test_empty_key_raises(self) -> None:
        with pytest.raises(ValueError, match="key must not be empty"):
            playfair_encrypt("HELLO", "")

    def test_j_merged(self) -> None:
        from bond_utilities.ciphers import _playfair_prepare

        assert "J" not in playfair_encrypt("JACK", "KEY")
        assert _playfair_prepare("JACK") == "IACK"
        # A repeated pair triggers double-splitting.
        assert _playfair_prepare("HELLO") == "HELXLO"
        # An odd final letter is padded with X.
        assert _playfair_prepare("OFF") == "OFFX"

    def test_key_containing_j(self) -> None:
        from bond_utilities.ciphers import _playfair_prepare

        # A 'J' in the key folds to 'I' when building the square.
        key = "JACKSQUARE"
        text = "HELLO"
        assert playfair_decrypt(playfair_encrypt(text, key), key) == _playfair_prepare(text)

    def test_clean_input_round_trip_different_keys(self) -> None:
        for key in ("MONARCHY", "PLAYFAIREXAMPLE", "SECRETKEY"):
            text = "ATTACKATDAWN"
            assert playfair_decrypt(playfair_encrypt(text, key), key) == text


class TestColumnar:
    @pytest.mark.parametrize("text,key", COLUMNAR_VECTORS)
    def test_round_trip(self, text: str, key: str) -> None:
        if not text:
            assert columnar_encrypt(text, key) == ""
            assert columnar_decrypt(text, key) == ""
            return
        assert columnar_decrypt(columnar_encrypt(text, key), key) == text

    def test_known_vector(self) -> None:
        # key "3142" -> read columns 3,1,4,2 (0-indexed 2,0,3,1).
        assert columnar_encrypt("HELLOWORLD", "3142") == "EWDLRHOLLO"

    def test_errors(self) -> None:
        with pytest.raises(ValueError, match="key must not be empty"):
            columnar_encrypt("HELLO", "")
        with pytest.raises(ValueError, match="digits"):
            columnar_encrypt("HELLO", "ABC")


class TestFrequencyAnalysis:
    def test_letter_frequency(self) -> None:
        counts = letter_frequency("AabB cC")
        assert counts["a"] == 2
        assert counts["c"] == 2
        # Non-letters (space) are ignored: only 6 letters counted.
        assert sum(counts.values()) == 6
        assert len(counts) == 26

    def test_frequency_normalized(self) -> None:
        norm = frequency_normalized("AAA")
        assert norm["a"] == 1.0
        assert norm["b"] == 0.0
        assert sum(norm.values()) == 1.0

    def test_frequency_normalized_empty(self) -> None:
        assert frequency_normalized("123") == {letter: 0.0 for letter in "abcdefghijklmnopqrstuvwxyz"}

    def test_index_of_coincidence(self) -> None:
        # English-ish text: IC well above uniform (0.038).
        ic_en = index_of_coincidence("ELEPHANTELEPHANTELEPHANTELEPHANT")
        ic_rand = index_of_coincidence("QWERTYUIOPASDFGHJKLZXCVBNMQWERTY")
        assert ic_en > ic_rand
        assert 0.0 < ic_en < 0.2
        assert 0.0 <= ic_rand < 0.06

    def test_index_of_coincidence_too_short(self) -> None:
        assert index_of_coincidence("A") == 0.0
        assert index_of_coincidence("") == 0.0

    def test_english_chi_squared_lower_for_english(self) -> None:
        english = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
        shift3 = caesar_encrypt(english, 3)
        assert english_chi_squared(english) < english_chi_squared(shift3)

    def test_english_chi_squared_empty(self) -> None:
        assert english_chi_squared("123") == 0.0


class TestCaesarBreak:
    def test_recovers_shift_on_long_text(self) -> None:
        for original_shift in (3, 7, 12, 25):
            ciphertext = caesar_encrypt(_LONG, original_shift)
            shift, plaintext = caesar_break(ciphertext)
            assert shift == original_shift
            assert plaintext == _LONG

    def test_no_letters_raises(self) -> None:
        with pytest.raises(ValueError, match="letter"):
            caesar_break("12345")

    def test_shift_scores_sorted(self) -> None:
        scores = caesar_shift_scores(caesar_encrypt(_LONG, 5))
        assert len(scores) == 26
        assert scores[0][0] == 5
        shifts = [entry[0] for entry in scores]
        assert sorted(shifts) == list(range(26))


class TestKasiski:
    def test_finds_key_length_from_repeated_plaintext(self) -> None:
        plaintext = "A" * 60 + "B" * 60 + "C" * 60
        cipher = vigenere_encrypt(plaintext, "SILENT")
        lengths = kasiski_key_lengths(cipher)
        assert 6 in lengths
        assert lengths == sorted(set(lengths), key=lengths.index)

    def test_too_short_returns_empty(self) -> None:
        assert kasiski_key_lengths("AB") == []

    def test_max_length_too_small_raises(self) -> None:
        with pytest.raises(ValueError, match="max_length"):
            kasiski_key_lengths(_LONG, max_length=1)


class TestVigenereBreak:
    def test_recovers_key_on_long_text(self) -> None:
        ciphertext = vigenere_encrypt(_LONG, "LEMON")
        key, plaintext = vigenere_break(ciphertext, 5)
        assert key == "LEMON"
        assert plaintext == _LONG

    def test_deterministic(self) -> None:
        ciphertext = vigenere_encrypt(_LONG, "SILENT")
        assert vigenere_break(ciphertext, 6) == vigenere_break(ciphertext, 6)

    def test_key_length_too_small_raises(self) -> None:
        with pytest.raises(ValueError, match="key_length"):
            vigenere_break(_LONG, 0)


def test_cross_module_seed_agreement() -> None:
    assert derive_seed("mission") == derive_seed("mission")


class TestNonAsciiRobustness:
    """Non-ASCII alphabetic characters are *non-letters* in this module.

    Every cipher document conceals -- and every counting helper promises --
    "letters A-Z / non-letters pass through". Guard the class of bug where a
    non-ASCII letter (e.g. é, ñ) crashed the A-Z counters with a KeyError or
    was silently corrupted by the ciphers.
    """

    def test_letter_frequency_ignores_non_ascii_and_emits_only_a_to_z(self) -> None:
        counts = letter_frequency("caf\u00e9 x\u00f1")
        # Negative control: no non-ASCII key may appear, and it must not crash.
        assert all("a" <= key <= "z" for key in counts)
        assert "\u00e9" not in counts and "\u00f1" not in counts
        assert counts["c"] == 1 and counts["a"] == 1 and counts["f"] == 1
        assert counts["x"] == 1

    def test_frequency_normalized_and_ic_and_chi_match_ascii_projection(self) -> None:
        # Non-ASCII letters are ignored, so results equal the ASCII-only body.
        assert frequency_normalized("abcabc\u00e9") == frequency_normalized("abcabc")
        assert index_of_coincidence("abcabc\u00e9") == index_of_coincidence("abcabc")
        assert english_chi_squared("abc\u00ef\u00e9\u00f1") == english_chi_squared("abc")

    def test_ciphers_pass_non_ascii_letters_through_unchanged(self) -> None:
        # é is not a cipher letter: ASCII neighbours shift, é itself is untouched.
        assert caesar_encrypt("caf\u00e9", 3) == "fdi\u00e9"
        # Round-trip still holds over the whole (mixed) string.
        from bond_utilities.ciphers import caesar_decrypt

        assert caesar_decrypt(caesar_encrypt("caf\u00e9 rue", 7), 7) == "caf\u00e9 rue"

    def test_break_and_counts_treat_non_ascii_only_text_as_letterless(self) -> None:
        from bond_utilities.ciphers import caesar_break

        with pytest.raises(ValueError, match="at least one letter"):
            caesar_break("\u00e9\u00ef\u00f1")
        assert english_chi_squared("\u00e9\u00ef") == 0.0

    def test_vigenere_rejects_non_ascii_key(self) -> None:
        with pytest.raises(ValueError, match="only letters"):
            vigenere_encrypt("MISSION", "caf\u00e9")
