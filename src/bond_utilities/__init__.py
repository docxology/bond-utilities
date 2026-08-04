"""bond-utilities — the shared foundation package of the BOND suite.

Layer 0 (Q-BRANCH primitives): classic ciphers, deterministic codenames,
mission clock math, seeded randomness, mission-record persistence with
provenance, plain-text reporting, and shared test fixtures. Every other
bond package imports from this package; it depends only on the standard
library plus numpy/matplotlib/pyyaml (pytest is required only for
``bond_utilities.testing``, which other packages opt into via conftest).
"""

from .ciphers import (
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
from .clock import (
    elapsed_time,
    format_elapsed,
    parse_schedule,
    parse_timestamp,
    t_minus,
    to_utc,
    window_elapsed,
    window_open,
    window_remaining,
)
from .codenames import (
    ADJECTIVES,
    NOUNS,
    codename_for,
    generate_codenames,
    random_codename,
)
from .mission_io import (
    MISSION_SCHEMA,
    MISSION_SCHEMA_VERSION,
    MissionValidationError,
    hash_payload,
    load_record,
    record_provenance_outcome,
    save_record,
    validate_record,
)
from .randomness import derive_seed, make_rng, seeded
from .reporting import banner, format_kv, format_table, print_kv, print_table

__version__ = "0.1.0"

__all__ = [
    # ciphers
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
    # codenames
    "ADJECTIVES",
    "NOUNS",
    "random_codename",
    "generate_codenames",
    "codename_for",
    # clock
    "to_utc",
    "parse_timestamp",
    "elapsed_time",
    "format_elapsed",
    "window_open",
    "window_elapsed",
    "window_remaining",
    "t_minus",
    "parse_schedule",
    # mission_io
    "MISSION_SCHEMA",
    "MISSION_SCHEMA_VERSION",
    "MissionValidationError",
    "hash_payload",
    "validate_record",
    "save_record",
    "load_record",
    "record_provenance_outcome",
    # randomness
    "derive_seed",
    "make_rng",
    "seeded",
    # reporting
    "banner",
    "format_table",
    "format_kv",
    "print_table",
    "print_kv",
    "__version__",
]
