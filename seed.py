import uuid
import random
from datetime import date, timedelta
from database import SessionLocal
import models
from core.security import get_password_hash

def seed_db():
    db = SessionLocal()
    
    # Check if empty
    if db.query(models.User).count() > 0:
        print("Database already contains data")
        return

    # Create users
    admin = models.User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=models.RoleEnum.ADMIN
    )
    analyst = models.User(
        email="analyst@example.com",
        password_hash=get_password_hash("analyst123"),
        role=models.RoleEnum.ANALYST
    )
    viewer = models.User(
        email="viewer@example.com",
        password_hash=get_password_hash("viewer123"),
        role=models.RoleEnum.VIEWER
    )
    
    db.add_all([admin, analyst, viewer])
    db.commit()
    db.refresh(admin)

    # Create financial records
    categories = ['Salary', 'Marketing', 'Server Costs', 'Software', 'Rent']
    records = []
    
    for i in range(50):
        t_type = random.choice(list(models.TransactionTypeEnum))
        cat = random.choice(categories)
        amount = round(random.uniform(50.0, 5000.0), 2)
        days_ago = random.randint(0, 90)
        r_date = date.today() - timedelta(days=days_ago)
        
        record = models.FinancialRecord(
            user_id=admin.id,
            amount=amount,
            transaction_type=t_type,
            category=cat,
            date=r_date,
            description=f"Dummy {cat} transaction"
        )
        records.append(record)
        
    db.add_all(records)
    db.commit()
    print("Database seeded with admin, analyst, viewer and 50 records")
    db.close()

if __name__ == "__main__":
    from database import engine
    models.Base.metadata.create_all(bind=engine)
    seed_db()
