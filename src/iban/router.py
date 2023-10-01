from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.iban.schemas import IBAN, IBANResponse, IBANDetails, IBANValidationsResponse
from src.iban.services import IBANValidationHistoryService

router = APIRouter(
    prefix='/iban'
)


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
        )
    )


@router.get('/history', response_model=list[IBANValidationsResponse])
async def history(db: AsyncSession = Depends(get_db)):
    service = IBANValidationHistoryService(db)
    result = await service.get_all()
    return result
