"""Pure sequential plan for the pinned long fixture. No files, API or retries.

The caller must verify the actual file hash/identity, transport limits and live
token ownership before execution. A matching argument is not file verification.
"""
from dataclasses import dataclass

SIZE = 117210794
SHA256 = '611e3644fb56fc1f12ddccd1d889258d249e36a4eca445451c16d13f5c5f5b07'
CHUNK = 1024 * 1024


@dataclass(frozen=True)
class Part:
    number: int
    offset: int
    length: int
    resume: bool
    final_chunk: bool
    resume_at: int


def plan(size, sha256):
    if type(size) is not int or size != SIZE or type(sha256) is not str or sha256 != SHA256:
        raise ValueError('FIXTURE_IDENTITY')
    return tuple(
        Part(i + 1, offset, min(CHUNK, size - offset), i != 0,
             offset + CHUNK >= size, offset if i else -1)
        for i, offset in enumerate(range(0, size, CHUNK))
    )


def require_next(parts, acknowledged, number):
    """Select the next request according to the supplied acknowledgement count.

    An ambiguous response must stop the caller. This pure function cannot
    establish remote acknowledgement or make uploads idempotent.
    """
    scalar_types = (int, int, int, bool, bool, int)
    fields = ('number', 'offset', 'length', 'resume', 'final_chunk', 'resume_at')
    if (type(parts) is not tuple
            or any(type(part) is not Part
                   or any(type(getattr(part, field)) is not expected
                          for field, expected in zip(fields, scalar_types))
                   for part in parts)
            or parts != plan(SIZE, SHA256)):
        raise ValueError('PLAN_IDENTITY')
    if type(acknowledged) is not int or not 0 <= acknowledged < len(parts):
        raise ValueError('ACKNOWLEDGEMENT')
    if type(number) is not int or number != acknowledged + 1:
        raise ValueError('ORDER_OR_REPLAY')
    return parts[acknowledged]
