import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app import models

print("🔨 Создание таблиц...")
Base.metadata.create_all(bind=engine)
print("✅ Таблицы созданы!")
