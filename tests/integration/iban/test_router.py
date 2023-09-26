import random
import string

from fastapi.testclient import TestClient
from starlette import status

from src.iban.validator.iban import MONTENEGRO_BBAN_SPEC
from src.main import app
from tests.utils import generate_iban

client = TestClient(app)

IBAN_BASE_ENDPOINT = '/api/v1/iban'


def test_health():
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'health': 'ok'}


def test_validate_success():
    iban = generate_iban()
    bban = iban[4:]
    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': iban}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'validated': True,
        'code': iban,
        'details': {
            'bban': int(bban),
            'bank_code': int(bban[0:3]),
            'account_code': int(bban[3:]),
            'checksum_digits': int(iban[2:4]),
            'country_code': iban[0:2]
        }
    }


def test_validate_success_even_when_lowercase_code():
    iban = generate_iban().lower()
    bban = iban[4:]
    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': iban}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'validated': True,
        'code': iban.upper(),
        'details': {
            'bban': int(bban),
            'bank_code': int(bban[0:3]),
            'account_code': int(bban[3:]),
            'checksum_digits': int(iban[2:4]),
            'country_code': iban[0:2].upper()
        }
    }


def test_validate_fail_when_length_more_than_fixed():
    iban = generate_iban() + str(random.randint(1, 9))
    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': iban}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['msg'] == 'Value error, Invalid IBAN length'


def test_validate_fail_when_country_code_is_different():
    iban = generate_iban(county_code='RS')

    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': iban}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['msg'] == 'Value error, Invalid country code'


def test_validate_fail_when_calc_checksum_not_matching():
    iban = generate_iban()

    # replace last digit with randomly generated except the original
    skip_digit = int(iban[-1])
    rand_digit = random.choice([i for i in range(0, 9) if i != skip_digit])
    iban = iban[:-1] + str(rand_digit)

    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': iban}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['msg'] == 'Value error, Invalid checksum digits'


def test_validate_fail_when_format_is_invalid():
    iban = generate_iban()

    iban = iban[:-1] + random.choice(string.ascii_uppercase)
    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': iban}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['msg'] == "Value error, " \
        "Invalid IBAN structure: '{}' " \
        "doesn't match '{}''".format(iban[4:], MONTENEGRO_BBAN_SPEC)
