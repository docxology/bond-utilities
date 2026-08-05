"""Every worked example printed in the docs, executed against the real code.

Three documented examples used to assert outputs the library does not produce.
The fix is not a softer comment: each documented output is now *computed here*
and then required to appear verbatim in the file that quotes it. A doc example
that drifts from the code fails this module, in either direction:

* change the code and the computed value stops matching the quoted string;
* change the quoted string and the file-content assertion fails.

No mocks: every value below comes from calling the shipped functions.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bond_utilities.ciphers import (
    caesar_break,
    caesar_encrypt,
    index_of_coincidence,
    kasiski_key_lengths,
    vigenere_break,
    vigenere_encrypt,
)
from bond_utilities.codenames import nato_codename, numeric_codename

PROJECT_ROOT = Path(__file__).resolve().parents[1]

#: The letter-rich sample the README and AGENTS.md both quote.
LETTER_RICH_SAMPLE = (
    "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGANDTHENGATHERSGRACEFULACORNS"
    "FROMEVERYMAPLETREEBYTHERIVERBANKWHILETHEHUNTERSLEEPSSILENTLYIN"
    "THESHADOWOFTHECASTLECLOCKTOWERCOUNTINGTHEMINUTESUNTILTHEDAWN"
    "BREAKSOVERHORIZON"
)

#: The short sample the docs use as the documented failure case.
SHORT_SAMPLE = "THEQUICKBROWNFOXJUMPS"

#: The 35-letter pangram used in the quickstart success case.
PANGRAM = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"


def _read(relative: str) -> str:
    path = PROJECT_ROOT / relative
    assert path.exists(), f"documented file missing: {relative}"
    return path.read_text(encoding="utf-8")


class TestQuickstartExamples:
    """`docs/quickstart.md` — "Try the library" block."""

    def test_caesar_encrypt_output(self) -> None:
        assert caesar_encrypt("Q-BRANCH", 3) == "T-EUDQFK"
        assert "'T-EUDQFK'" in _read("docs/quickstart.md")

    def test_long_sample_recovers_exactly(self) -> None:
        assert caesar_break(caesar_encrypt(PANGRAM, 7)) == (7, PANGRAM)
        assert f"(7, '{PANGRAM}')" in _read("docs/quickstart.md")

    def test_short_sample_returns_the_documented_wrong_answer(self) -> None:
        result = caesar_break(caesar_encrypt("THEQUICKBROWNFOX", 7))
        assert result == (23, "DROAESMULBYGXPYH")
        text = _read("docs/quickstart.md")
        assert "(23, 'DROAESMULBYGXPYH')" in text, "quickstart no longer quotes the real short-text result"

    def test_nato_example(self) -> None:
        assert nato_codename("QB7") == "QUEBEC-BRAVO-7"
        assert "'QUEBEC-BRAVO-7'" in _read("docs/quickstart.md")


class TestReadmeExamples:
    """`README.md` — "Ciphers + cryptanalysis" and codename blocks."""

    def test_caesar_break_short_english_phrase(self) -> None:
        assert caesar_break(caesar_encrypt("ATTACK AT DAWN", 5)) == (5, "ATTACK AT DAWN")
        assert "(5, 'ATTACK AT DAWN')" in _read("README.md")

    def test_vigenere_recovers_key_on_the_documented_sample(self) -> None:
        cipher = vigenere_encrypt(LETTER_RICH_SAMPLE, "LEMON")
        key, decoded = vigenere_break(cipher, 5)
        assert key == "LEMON"
        assert decoded == LETTER_RICH_SAMPLE
        assert "key == 'LEMON', decoded == sample" in _read("README.md")

    def test_documented_sample_length(self) -> None:
        assert len(LETTER_RICH_SAMPLE) == 202
        assert "202 letters" in _read("README.md")

    def test_numeric_codename_value(self) -> None:
        assert numeric_codename("M-001", seed=7) == "QB-B6050C24"
        assert "'QB-B6050C24'" in _read("README.md")


class TestAgentsExamples:
    """`AGENTS.md` — "Cryptanalysis" block and its short-sample caveat."""

    def test_caesar_and_vigenere_succeed_on_the_letter_rich_sample(self) -> None:
        shift, plaintext = caesar_break(caesar_encrypt(LETTER_RICH_SAMPLE, 7))
        assert (shift, plaintext) == (7, LETTER_RICH_SAMPLE)
        key, decoded = vigenere_break(vigenere_encrypt(LETTER_RICH_SAMPLE, "LEMON"), 5)
        assert (key, decoded) == ("LEMON", LETTER_RICH_SAMPLE)
        text = _read("AGENTS.md")
        assert "shift == 7, plaintext == sample" in text
        assert "key == 'LEMON', decoded == sample" in text

    def test_kasiski_top_candidate_is_the_true_key_length(self) -> None:
        cipher = vigenere_encrypt(LETTER_RICH_SAMPLE, "LEMON")
        assert kasiski_key_lengths(cipher)[0] == 5

    def test_index_of_coincidence_separates_the_two_texts(self) -> None:
        cipher = vigenere_encrypt(LETTER_RICH_SAMPLE, "LEMON")
        assert index_of_coincidence(LETTER_RICH_SAMPLE) > index_of_coincidence(cipher)

    def test_documented_short_sample_failures(self) -> None:
        assert caesar_break(caesar_encrypt(SHORT_SAMPLE, 7)) == (8, "SGDPTHBJAQNVMENWITLOR")
        key, _ = vigenere_break(vigenere_encrypt(SHORT_SAMPLE, "LEMON"), 5)
        assert key == "MTSMQ"
        text = _read("AGENTS.md")
        assert "(8, 'SGDPTHBJAQNVMENWITLOR')" in text
        assert "'MTSMQ'" in text


class TestRecoveryIsLengthDependent:
    """The manuscript's qualified claim, bound to a measurement.

    `caesar_break` recovers the exact shift on letter-rich English and does not
    on short samples. Both directions are asserted so neither half of the
    documented statement can rot.
    """

    @pytest.mark.parametrize("text", [PANGRAM, LETTER_RICH_SAMPLE])
    def test_recovers_on_letter_rich_english(self, text: str) -> None:
        for shift in (1, 7, 13, 25):
            assert caesar_break(caesar_encrypt(text, shift)) == (shift, text)

    @pytest.mark.parametrize(
        "text,shift",
        [("THEQUICKBROWNFOX", 7), ("THEQUICKBROWNFOXJUMPS", 7)],
    )
    def test_fails_on_short_english(self, text: str, shift: int) -> None:
        recovered, _ = caesar_break(caesar_encrypt(text, shift))
        assert recovered != shift, "short-text failure disappeared — the docs' limitation statement is now wrong"


class TestBibliographyClaimsMatchTheCode:
    """`manuscript/99_references.md` annotates each source with a code claim.

    Two of those annotations were false: friedman_1922 claimed the index of
    coincidence scores candidate key lengths inside `vigenere_break`, and
    iso8601 claimed `append_outcome` writes a timestamp. These tests pin the
    corrected statements against the actual source.
    """

    def test_vigenere_break_does_not_use_the_index_of_coincidence(self) -> None:
        import inspect

        source = inspect.getsource(vigenere_break)
        assert "index_of_coincidence" not in source
        assert "caesar_break" in source

    def test_vigenere_break_requires_an_explicit_key_length(self) -> None:
        import inspect

        signature = inspect.signature(vigenere_break)
        assert list(signature.parameters) == ["text", "key_length"]
        assert signature.parameters["key_length"].default is inspect.Parameter.empty
        with pytest.raises(TypeError):
            vigenere_break(vigenere_encrypt(LETTER_RICH_SAMPLE, "LEMON"))  # type: ignore[call-arg]

    def test_index_of_coincidence_is_surfaced_by_the_cli(self) -> None:
        assert "index_of_coincidence" in _read("scripts/cryptanalyze.py")

    def test_append_outcome_writes_no_timestamp(self) -> None:
        import inspect

        from bond_utilities.mission_io import append_outcome, record_provenance_outcome

        append_source = inspect.getsource(append_outcome)
        assert "isoformat" not in append_source
        assert "datetime" not in append_source
        assert "isoformat" in inspect.getsource(record_provenance_outcome)

    def test_append_outcome_preserves_started_at_and_provenance(self, tmp_path: Path) -> None:
        from bond_utilities.mission_io import append_outcome, record_provenance_outcome

        target = tmp_path / "M-001.json"
        record = record_provenance_outcome(
            mission_id="M-001",
            seed="ops",
            version="0.3.0",
            input_payload={"target": "grid"},
            outcome={"status": "ok"},
            path=target,
        )
        updated = append_outcome(target, {"consumed": True})
        assert updated["started_at"] == record["started_at"]
        assert updated["provenance"] == record["provenance"]
        assert updated["outcomes"]["consumed"] is True

    def test_references_state_the_corrected_claims(self) -> None:
        text = _read("manuscript/99_references.md")
        assert "does **not** consult the IC" in text
        assert "writes no timestamp of its own" in text
