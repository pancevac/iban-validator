from pydantic import BaseModel, Field, field_validator

from src.iban.validator.iban import IBAN as IBANValidator


class IBAN(BaseModel):
    code: str = Field(
        title='International Bank Account Number',
        examples=['ME21143598727954283123']
    )

    @field_validator('code')
    @classmethod
    def validate_code(cls, value: str) -> str:
        iban = IBANValidator(code=value)
        iban.validate()
        return iban.code


class IBANResponse(BaseModel):
    validated: bool = True
    code: str
