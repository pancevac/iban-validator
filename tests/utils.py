import random
from schwifty.iban import IBAN


def generate_iban(
        county_code: str = 'ME',
        bank_code: int = random.randint(100, 999),
        account_code: int = random.randint(1000000000000, 9999999999999)
) -> str:
    iban = IBAN.generate(county_code, bank_code=str(bank_code), account_code=str(account_code))
    return iban.compact
