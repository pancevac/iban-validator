"""
This file is highly inspired by package "Schwifty",
GitHub Link: https://github.com/mdomke/schwifty

It contains only essentially functionalities from schwifty,
but it also implements additional functionalities by task requirements.
"""
import re
from typing import Optional

from src.iban.validator import exceptions
from src.iban.validator.helpers import build_bban_regex, numerify, clear

# Regex for Montenegro according to IBAN registry specifications.
# See: https://ibanapi.com/iban-registry/ME
MONTENEGRO_BBAN_SPEC = '3!n13!n2!n'
MONTENEGRO_BBAN_REGEX = build_bban_regex(MONTENEGRO_BBAN_SPEC)

MONTENEGRO_IBAN_LENGTH = 22
MONTENEGRO_COUNTRY_CODE = 'ME'

MONTENEGRO_IBAN_POSITIONS = {
    'bank_code': (0, 3),
    'account_code': (3, 18)
}


class IBAN:
    def __init__(self, code: str):
        self._code = clear(code)
        self._validated = False

    @property
    def code(self) -> str:
        return self._code

    @property
    def length(self) -> int:
        return len(self._code)

    @property
    def validated(self) -> bool:
        return self._validated

    @property
    def bban(self) -> str:
        """
        Extract BBAN code from IBAN.
        """
        return self._get_component(start=4)

    @property
    def completed_iban(self) -> bool:
        """
        Is IBAN code is fully written or only part of it?
        """
        return self.length == MONTENEGRO_IBAN_LENGTH

    @property
    def country_code(self) -> str:
        return self._get_component(start=0, end=2)

    @property
    def numeric(self) -> int:
        """
        A numeric representation of the IBAN.
        """
        return numerify(self.bban + self._code[:4])

    @property
    def checksum_digits(self) -> str:
        """
        Extract checksum digits from IBAN, also known as control digits.
        """
        return self._get_component(start=2, end=4)

    @property
    def bank_code(self) -> str:
        return self._get_code('bank_code')

    @property
    def account_code(self) -> str:
        return self._get_code('account_code')

    def _get_code(self, code_type: str) -> str:
        start, end = MONTENEGRO_IBAN_POSITIONS[code_type]
        code = self.bban[start:end]
        if len(code) == end - start:
            return code
        return ''

    def _get_component(self, start: int, end: Optional[int] = None) -> str:
        """
        Get specific part of code.
        """
        if start < self.length and (end is None or end <= self.length):
            return self._code[start:end] if end else self._code[start:]
        return ''

    def _calc_checksum_digits(self) -> str:
        return "{:02d}".format(98 - (numerify(self.bban + self.country_code) * 100) % 97)

    def _validate_characters(self) -> None:
        if not re.match(r"[A-Z]{2}\d{2}[A-Z]*", self._code):  # TODO review this regex!
            raise exceptions.InvalidStructure(f"Invalid characters in IBAN {self._code}")

    def _validate_characters_partially(self) -> None:
        if self.length <= 2:
            if not re.match(r"[A-Z]{2}$", self._code):
                raise exceptions.InvalidStructure(f"Invalid characters in IBAN {self._code}")

        else:
            if not re.match(r"[A-Z]{2}\d+$", self._code):
                raise exceptions.InvalidStructure(f"Invalid characters in IBAN {self._code}")

    def _validate_format(self) -> None:
        if not re.match(MONTENEGRO_BBAN_REGEX, self.bban):
            raise exceptions.InvalidStructure(
                "Invalid IBAN structure: '{}' doesn't match '{}''".format(
                    self.bban, MONTENEGRO_BBAN_SPEC
                )
            )

    def _validate_iban_checksum(self) -> None:
        if self.numeric % 97 != 1 or self._calc_checksum_digits() != self.checksum_digits:
            raise exceptions.InvalidChecksumDigits("Invalid checksum digits")

    def _validate_country_code(self) -> None:
        if self.country_code != MONTENEGRO_COUNTRY_CODE:
            raise exceptions.InvalidCountryCode("Invalid country code")

    def _validate_length(self) -> None:
        if MONTENEGRO_IBAN_LENGTH != self.length:
            raise exceptions.InvalidLength("Invalid IBAN length")

    def _validate_length_partially(self) -> None:
        if MONTENEGRO_IBAN_LENGTH < self.length:
            raise exceptions.InvalidLength("Invalid IBAN length")

    def _validate_format_partially(self) -> None:
        raise NotImplemented

    def validate(self):
        if self.completed_iban:
            self._validate_characters()
            self._validate_length()
            self._validate_country_code()
            self._validate_format()
            self._validate_iban_checksum()
        else:
            self._validate_characters_partially()
            self._validate_length_partially()
            self._validate_country_code()
            # self._validate_format_partially()

        self._validated = True
