# app/models/armario.py — Tabela de Armários e Agendamentos

from sqlalchemy import Column, Integer, String, Boolean, Date, Text
from app.database import Base

class Armario(Base):
    __tablename__ = "armarios"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    numero = Column(String(50), nullable=False, unique=True, index=True)
    localizacao = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="Livre")  # "Livre" ou "Ocupado"

    # Dados do Agendamento / Reserva (preenchidos quando status = "Ocupado")
    aluno_nome = Column(String(150), nullable=True)
    turma = Column(String(100), nullable=True)
    contato = Column(String(100), nullable=True)
    data_inicio = Column(Date, nullable=True)
    data_termino = Column(Date, nullable=True)
    observacoes = Column(Text, nullable=True)

    ativo = Column(Boolean, default=True)
