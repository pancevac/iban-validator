from fastapi import APIRouter

from src.iban.schemas import IBAN, IBANResponse

router = APIRouter(prefix='/iban')


@router.post('/validate', response_model=IBANResponse)
async def validate(iban: IBAN):
    return IBANResponse(code=iban.code)
