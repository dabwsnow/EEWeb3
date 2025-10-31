from sqlalchemy import Column, Integer, String, Text
from database import Base

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
    date = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    type = Column(String(100), nullable=True)
    arkusz_url = Column(Text, nullable=True)
    pliki_url = Column(Text, nullable=True)
    rozwiazanie_url = Column(Text, nullable=True)
    downloaded = Column(Integer, default=0)

class PracticeEE08(Base):
    __tablename__ = "practice_ee08"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    type = Column(String(100), nullable=True)
    arkusz_url = Column(Text, nullable=True)
    pliki_url = Column(Text, nullable=True)
    rozwiazanie_url = Column(Text, nullable=True)
    downloaded = Column(Integer, default=0)

class PracticeE13(Base):
    __tablename__ = "practice_e13"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    type = Column(String(100), nullable=True)
    arkusz_url = Column(Text, nullable=True)
    pliki_url = Column(Text, nullable=True)
    rozwiazanie_url = Column(Text, nullable=True)
    downloaded = Column(Integer, default=0)

class PracticeE12(Base):
    __tablename__ = "practice_e12"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    type = Column(String(100), nullable=True)
    arkusz_url = Column(Text, nullable=True)
    pliki_url = Column(Text, nullable=True)
    rozwiazanie_url = Column(Text, nullable=True)
    downloaded = Column(Integer, default=0)

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

class PracticeEE09(Base):
    __tablename__ = "practice_ee09"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    type = Column(String(100), nullable=True)
    arkusz_url = Column(Text, nullable=True)
    pliki_url = Column(Text, nullable=True)
    rozwiazanie_url = Column(Text, nullable=True)
    downloaded = Column(Integer, default=0)

class PracticeE14(Base):
    __tablename__ = "practice_e14"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    type = Column(String(100), nullable=True)
    arkusz_url = Column(Text, nullable=True)
    pliki_url = Column(Text, nullable=True)
    rozwiazanie_url = Column(Text, nullable=True)
    downloaded = Column(Integer, default=0)

class PracticeINF04(Base):
    __tablename__ = "practice_inf04"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    type = Column(String(100), nullable=True)
    arkusz_url = Column(Text, nullable=True)
    pliki_url = Column(Text, nullable=True)
    klucz_odpowiedzi_url = Column(Text, nullable=True)
    materialy_url = Column(Text, nullable=True)
    rozwiazanie_cs_url = Column(Text, nullable=True)
    rozwiazanie_cpp_url = Column(Text, nullable=True)
    rozwiazanie_java_url = Column(Text, nullable=True)
    rozwiazanie_python_url = Column(Text, nullable=True)
    downloaded = Column(Integer, default=0)