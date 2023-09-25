import re
import string
from typing import Dict

_spec_to_re: Dict[str, str] = {"n": r"\d", "a": r"[A-Z]", "c": r"[A-Za-z0-9]", "e": r" "}
_alphabet: str = string.digits + string.ascii_uppercase


def build_bban_regex(bban_spec: str) -> re.Pattern:
    """
    Transform BBAN registry specification into regex pattern.
    Example: Montenegro BBAN spec 3!n13!n2!n will build regex r'\d{3}\d{13}\d{2}'
    See: https://ibanapi.com/iban-registry/ME
    """
    spec_re = r"(\d+)(!)?([{}])".format("".join(_spec_to_re.keys()))

    def convert(match: re.Match) -> str:
        quantifier = ("{%s}" if match.group(2) else "{1,%s}") % match.group(1)
        return _spec_to_re[match.group(3)] + quantifier

    return re.compile("^{}$".format(re.sub(spec_re, convert, bban_spec)))


def numerify(chars: str) -> int:
    """
    Return int representation of string
    """
    return int("".join(str(_alphabet.index(c)) for c in chars))


def clear(code: str) -> str:
    """
    Strip any whitespaces from code.
    """
    return code.strip().replace(' ', '').upper()

