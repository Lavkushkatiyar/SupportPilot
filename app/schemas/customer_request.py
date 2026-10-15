from pydantic import BaseModel, ConfigDict, Field, field_validator


class CustomerSupportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_message: str = Field(min_length=1, max_length=5000)

    @field_validator("customer_message")
    @classmethod
    def validate_customer_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Customer message cannot be empty.")
        return value
