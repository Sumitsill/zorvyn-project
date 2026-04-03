import enum
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, Enum, DateTime, ForeignKey, Numeric, Date
from database import Base

class RoleEnum(str, enum.Enum):
    VIEWER = 'VIEWER'
    ANALYST = 'ANALYST'
    ADMIN = 'ADMIN'

class TransactionTypeEnum(str, enum.Enum):
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_type = Column(Enum(TransactionTypeEnum), nullable=False)
    category = Column(String, nullable=False)
    date = Column(Date, default=date.today)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
