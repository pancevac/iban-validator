from datetime import datetime
from typing import Union, Generic, TypeVar, List

from pydantic import BaseModel, Field, field_validator

from src.iban.models import StatusTypes
from src.iban.validator.iban import IBAN as IBANValidator

M = TypeVar('M')


class IBAN(BaseModel):
    code: str = Field(title='International Bank Account Number', examples=['ME21143598727954283123'])
    _iban: IBANValidator

    @field_validator('code')
    @classmethod
    def validate_code(cls, value: str) -> str:
        iban = IBANValidator(code=value)
        iban.validate()
        cls._iban = iban
        return iban.code

    @property
    def validator_instance(self) -> IBANValidator:
        return self._iban


class IBANDetails(BaseModel):
    bban: str = Field(title='Basic Bank Account Number', examples=['143598727954283120'])
    bank_code: str = Field(title='Bank Code', examples=['143'])
    account_code: str = Field(title='Account Code', examples=['598727954283123'])
    checksum_digits: str = Field(title='Checksum digits', examples=['21'])
    country_code: str = Field(title='Country Code', examples=['ME'])


class IBANResponse(BaseModel):
    fully_validated: bool
    code: str = Field(title='International Bank Account Number', examples=['ME21143598727954283123'])
    details: IBANDetails


class IBANValidationHistoryResponse(BaseModel):
    id: int
    code: str = Field(
        title='International Bank Account Number',
        examples=['ME21143598727954283123'])
    status: StatusTypes = Field(
        title='Status of the validation',
        examples=['failed', 'partially_validated', 'validated'])
    error_message: Union[str, None] = Field(
        title='Error message if validation failed',
        examples=['Value error, Invalid country code']
    )
    timestamp: datetime

    class Config:
        # Remap enum int values as string names, see: https://stackoverflow.com/a/75586485
        json_encoders = {StatusTypes: lambda s: s.name}
        from_attributes = True


class PaginatedResponse(BaseModel, Generic[M]):
    count: int = Field(description='Number of items returned in the response')
    items: List[M] = Field(description='List of items returned in the response following given criteria')
