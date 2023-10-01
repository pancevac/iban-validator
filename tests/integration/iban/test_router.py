import random
import string

from starlette import status

from src.iban.validator.iban import MONTENEGRO_BBAN_SPEC
from tests.utils import generate_iban

IBAN_BASE_ENDPOINT = '/api/v1/iban'


def test_health(client):
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'health': 'ok'}


def test_validate_success(client):
    iban = generate_iban()
    bban = iban[4:]
    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': iban}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'fully_validated': True,
        'code': iban,
        'details': {
            'bban': bban,
            'bank_code': bban[0:3],
            'account_code': bban[3:],
            'checksum_digits': iban[2:4],
            'country_code': iban[0:2]
        }
    }


def test_validate_success_even_when_lowercase_code(client):
    iban = generate_iban().lower()
    bban = iban[4:]
    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': iban}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'fully_validated': True,
        'code': iban.upper(),
        'details': {
            'bban': bban,
            'bank_code': bban[0:3],
            'account_code': bban[3:],
            'checksum_digits': iban[2:4],
            'country_code': iban[0:2].upper()
        }
    }


def test_partial_validate_success_case1(client):
    """
    In this case, cut IBAN code from randomly chosen index starting from 4.
    """
    iban = generate_iban()
    partial_iban = iban[:random.randint(4, 21)]
    bban = partial_iban[4:]

    bank_code, account_code, checksum_digits, country_code = '', '', iban[2:4], iban[0:2]

    if bban != '':
        bank_code = bban[0:3] if len(bban[0:3]) == 3 else ''
        account_code = bban[3:] if len(bban[3:]) == 15 else ''
        checksum_digits = partial_iban[2:4] if len(partial_iban[2:4]) == 2 else ''
        country_code = partial_iban[0:2] if len(partial_iban[0:2]) == 2 else ''

    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': partial_iban}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'fully_validated': False,
        'code': partial_iban,
        'details': {
            'bban': bban,
            'bank_code': bank_code,
            'account_code': account_code,
            'checksum_digits': checksum_digits,
            'country_code': country_code
        }
    }


def test_partial_validate_success_case2(client):
    """
    In this case, provide only fully country_code.
    """
    iban = generate_iban()
    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': iban[0:2]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'fully_validated': False,
        'code': 'ME',
        'details': {
            'bban': '',
            'bank_code': '',
            'account_code': '',
            'checksum_digits': '',
            'country_code': iban[0:2]
        }
    }


def test_partial_validate_success_case3(client):
    """
    In this case, provide fully country code and only one digit of checksum.
    """
    iban = generate_iban()
    partial_iban = iban[:3]

    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': partial_iban}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'fully_validated': False,
        'code': partial_iban,
        'details': {
            'bban': '',
            'bank_code': '',
            'account_code': '',
            'checksum_digits': '',
            'country_code': partial_iban[0:2]
        }
    }


def test_partial_validate_fail_when_provided_uncompleted_country_code(client):
    iban = generate_iban()
    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': iban[0:1]}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['msg'] == f'Value error, Invalid characters in IBAN {iban[0:1]}'


def test_partial_validate_fail_when_format_is_invalid(client):
    iban = generate_iban()
    partial_iban = iban[:random.randint(4, 21)]
    partial_iban = partial_iban[:-1] + random.choice(string.ascii_uppercase)
    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': partial_iban}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['msg'] == "Value error, " \
        "Invalid characters in IBAN {}".format(partial_iban)


def test_validate_fail_when_length_more_than_fixed(client):
    iban = generate_iban() + str(random.randint(1, 9))
    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': iban}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['msg'] == 'Value error, Invalid IBAN length'


def test_validate_fail_when_country_code_is_different(client):
    iban = generate_iban(county_code='RS')

    response = client.post(
        url=IBAN_BASE_ENDPOINT + '/validate',
        json={'code': iban}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['msg'] == 'Value error, Invalid country code'


def test_validate_fail_when_calc_checksum_not_matching(client):
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


def test_validate_fail_when_format_is_invalid(client):
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
