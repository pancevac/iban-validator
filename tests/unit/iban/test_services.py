import random
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.iban.models import StatusTypes, IBANValidationHistory
from src.iban.services import IBANValidationHistoryService
from tests.utils import generate_iban


@pytest.mark.asyncio
class TestIBANValidationHistoryService:
    async def test_save(self):
        db_session_mock = AsyncMock(spec_set=AsyncSession)
        service = IBANValidationHistoryService(db=db_session_mock)
        iban = generate_iban()

        iban_validation_history = await service.save(iban_code=iban, status=StatusTypes.validated, error_msg=None)

        assert isinstance(iban_validation_history, IBANValidationHistory)
        db_session_mock.add.assert_called_once_with(iban_validation_history)
        db_session_mock.commit.assert_called_once()
        db_session_mock.refresh.assert_called_once_with(iban_validation_history)

    async def test_get_all(self):
        iban_validation_history_list = [
            IBANValidationHistory(
                id=random.randint(1, 10),
                status=StatusTypes.validated,
                code=generate_iban()
            )
        ]

        db_session_mock = AsyncMock(spec_set=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = iban_validation_history_list
        db_session_mock.execute = AsyncMock(return_value=mock_result)

        service = IBANValidationHistoryService(db=db_session_mock)

        iban_validation_history = await service.get_all(limit=100, offset=0)

        assert isinstance(iban_validation_history, list)
        assert len(iban_validation_history) >= 0

        db_session_mock.execute.assert_called_once()
