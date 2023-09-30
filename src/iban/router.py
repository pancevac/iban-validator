from fastapi import APIRouter

from src.iban.schemas import IBAN, IBANResponse, IBANDetails

router = APIRouter(prefix='/iban')


@router.post('/validate', response_model=IBANResponse)
async def validate(iban: IBAN):
    return IBANResponse(
        code=iban.code,
        fully_validated=iban.validator_instance.completed_iban,
        details=IBANDetails(
            bank_code=iban.validator_instance.bank_code,
            account_code=iban.validator_instance.account_code,
            bban=iban.validator_instance.bban,
            checksum_digits=iban.validator_instance.checksum_digits,
            country_code=iban.validator_instance.country_code
        ))
