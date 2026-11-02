"""
Base62 Encoder / Decoder
Chapter 7 & 8: ID Encoding & URL Shortening

Base62 uses [0-9, a-z, A-Z] (62 distinct characters).
A 64-bit integer encoded in Base62 produces a compact string of at most 11 characters.
For example:
- ID: 1000000 -> Base62: "4c92"
- ID: 2009215674938 -> Base62: "1Nz82p"
"""

BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(BASE62_ALPHABET)  # 62
DECODE_MAP = {char: idx for idx, char in enumerate(BASE62_ALPHABET)}


class Base62:
    @staticmethod
    def encode(num: int) -> str:
        """Encode a positive integer into a Base62 string."""
        if num < 0:
            raise ValueError("Only non-negative integers can be Base62 encoded.")
        if num == 0:
            return BASE62_ALPHABET[0]

        chars = []
        while num > 0:
            num, rem = divmod(num, BASE)
            chars.append(BASE62_ALPHABET[rem])

        return "".join(reversed(chars))

    @staticmethod
    def decode(s: str) -> int:
        """Decode a Base62 string back to an integer."""
        if not s:
            raise ValueError("Cannot decode an empty string.")

        num = 0
        for char in s:
            if char not in DECODE_MAP:
                raise ValueError(f"Invalid Base62 character: '{char}'")
            num = num * BASE + DECODE_MAP[char]

        return num

