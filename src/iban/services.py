from typing import Sequence, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.iban.models import IBANValidationHistory, StatusTypes


class IBANValidationHistoryService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_all(self) -> Sequence[IBANValidationHistory]:
        query = select(IBANValidationHistory)
        result = await self._db.execute(query)
        return result.scalars().all()

    async def save(
            self,
            iban_code: str,
            status: Union[StatusTypes.validated, StatusTypes.partially_validated, StatusTypes.failed],
            error_msg: Union[str, None] = None
    ) -> IBANValidationHistory:
        model = IBANValidationHistory(code=iban_code, status=status, error_message=error_msg)
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return model
