from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.iban.models import StatusTypes
from src.iban.schemas import IBAN, IBANResponse, IBANDetails, IBANValidationHistoryResponse, PaginatedResponse
from src.iban.services import IBANValidationHistoryService
from src.iban.utils import IBANValidationErrorLoggingRoute, Task
from src.queue import get_redis

router = APIRouter(
    prefix='/iban',
    route_class=IBANValidationErrorLoggingRoute
)


@router.post('/validate', response_model=IBANResponse)
async def validate(iban: IBAN):
    task = Task(
        iban=iban.code,
        status=StatusTypes.validated if iban.validator_instance.completed_iban else StatusTypes.partially_validated
    )

    async with get_redis() as redis:
        await redis.enqueue_job('process_iban_validation_result', task)

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


@router.get('/history', response_model=PaginatedResponse[IBANValidationHistoryResponse])
async def history(
        db: AsyncSession = Depends(get_db),
        limit: int = Query(100, ge=0, le=100),
        offset: int = Query(0, ge=0)
):
    service = IBANValidationHistoryService(db)
    items = await service.get_all(limit=limit, offset=offset)
    return PaginatedResponse(count=len(items), items=items)
