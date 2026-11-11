from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.modules.loans.domain.entities.loan import LoanStatus


class CreateLoanRequest(BaseModel):
    book_id: UUID
    reader_id: UUID
    borrowed_at: date
    due_date: date


class ReturnLoanRequest(BaseModel):
    returned_at: date
    policy_type: Literal["STANDARD", "ACADEMIC"] = "STANDARD"


class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    book_id: UUID
    reader_id: UUID
    borrowed_at: date
    due_date: date
    returned_at: date | None
    fine_amount: Decimal
    status: LoanStatus
