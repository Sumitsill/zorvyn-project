from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from models import RoleEnum, TransactionTypeEnum

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Optional[RoleEnum] = RoleEnum.VIEWER

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: RoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None
    role: Optional[RoleEnum] = None

class FinancialRecordCreate(BaseModel):
    amount: float = Field(..., gt=0)
    transaction_type: TransactionTypeEnum
    category: str
    date: date
    description: Optional[str] = None

class FinancialRecordUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    transaction_type: Optional[TransactionTypeEnum] = None
    category: Optional[str] = None
    date: Optional[date] = None
    description: Optional[str] = None

class FinancialRecordResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    transaction_type: TransactionTypeEnum
    category: str
    date: date
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedRecords(BaseModel):
    total: int
    page: int
    limit: int
    data: List[FinancialRecordResponse]

class DashboardSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float

class CategoryTotal(BaseModel):
    category: str
    total: float

class TrendItem(BaseModel):
    period: str
    income: float
    expense: float
