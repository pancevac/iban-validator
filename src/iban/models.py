from enum import IntEnum

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy_utils.types.choice import ChoiceType

from src.db import Base


class StatusTypes(IntEnum):
    validated = 1
    partially_validated = 2
    failed = 3


class IBANValidationHistory(Base):
    __tablename__ = 'iban_validations'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(length=34), nullable=False)
    status = Column(ChoiceType(StatusTypes, impl=Integer()), nullable=False)
    error_message = Column(String(), nullable=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
