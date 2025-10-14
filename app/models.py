from sqlalchemy import Column, Integer, String, Text
from .database import Base

# E.12
class QuestionE12(Base):
    __tablename__ = "questions_e12"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    answer_a = Column(Text, nullable=False)
    answer_b = Column(Text, nullable=False)
    answer_c = Column(Text, nullable=False)
    answer_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)
    explanation = Column(Text, nullable=True)

# E.13
class QuestionE13(Base):
    __tablename__ = "questions_e13"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    answer_a = Column(Text, nullable=False)
    answer_b = Column(Text, nullable=False)
    answer_c = Column(Text, nullable=False)
    answer_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)
    explanation = Column(Text, nullable=True)

# INF.02
class QuestionINF02(Base):
    __tablename__ = "questions_inf02"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    answer_a = Column(Text, nullable=False)
    answer_b = Column(Text, nullable=False)
    answer_c = Column(Text, nullable=False)
    answer_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)
    explanation = Column(Text, nullable=True)

# INF.03
class QuestionINF03(Base):
    __tablename__ = "questions_inf03"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    answer_a = Column(Text, nullable=False)
    answer_b = Column(Text, nullable=False)
    answer_c = Column(Text, nullable=False)
    answer_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)
    explanation = Column(Text, nullable=True)

# INF.04
class QuestionINF04(Base):
    __tablename__ = "questions_inf04"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    answer_a = Column(Text, nullable=False)
    answer_b = Column(Text, nullable=False)
    answer_c = Column(Text, nullable=False)
    answer_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)
    explanation = Column(Text, nullable=True)

class PracticeINF02(Base):
    __tablename__ = "practice_inf02"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(String(50), nullable=False)  # "2025 - Styczeń"
    year = Column(Integer, nullable=False, index=True)
    type = Column(String(100), nullable=True)  # "PHP, Database"
    arkusz_url = Column(Text, nullable=True)  # URL к PDF аркушу
    pliki_url = Column(Text, nullable=True)  # URL к ZIP с файлами
    rozwiazanie_url = Column(Text, nullable=True)  # URL к ZIP с решением
    downloaded = Column(Integer, default=0)  # Счетчик скачиваний

# Практика INF.03 / EE.09 / E.14
class PracticeINF03(Base):
    __tablename__ = "practice_inf03"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    type = Column(String(100), nullable=True)
    arkusz_url = Column(Text, nullable=True)
    pliki_url = Column(Text, nullable=True)
    rozwiazanie_url = Column(Text, nullable=True)
    downloaded = Column(Integer, default=0)

# Практика INF.04
class PracticeINF04(Base):
    __tablename__ = "practice_inf04"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    type = Column(String(100), nullable=True)
    arkusz_url = Column(Text, nullable=True)
    pliki_url = Column(Text, nullable=True)
    rozwiazanie_url = Column(Text, nullable=True)
    downloaded = Column(Integer, default=0)
