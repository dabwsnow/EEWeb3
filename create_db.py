from app.database import Base, engine
from app.models import QuestionE12, QuestionE13, QuestionINF02, QuestionINF03, QuestionINF04

print("Создание таблиц...")
Base.metadata.create_all(bind=engine)

from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()

print(f"\n✅ Создано таблиц: {len(tables)}")
for table in tables:
    print(f"   - {table}")