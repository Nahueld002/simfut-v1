from sqlalchemy import Column, Integer, String, Date, BigInteger, DateTime, ForeignKey, Boolean, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base

class Mundo(Base):
    __tablename__ = "mundo"
    __table_args__ = {"schema": "futsim"}

    mundo_id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    fecha_actual = Column(Date, nullable=False, server_default=func.current_date())
    semilla_rng = Column(BigInteger)
    configuracion_global = Column(JSONB, nullable=False, server_default='{}')

    temporadas = relationship("Temporada", back_populates="mundo", cascade="all, delete-orphan")

class Temporada(Base):
    __tablename__ = "temporada"
    __table_args__ = (
        UniqueConstraint('mundo_id', 'nombre'),
        {"schema": "futsim"}
    )

    temporada_id = Column(Integer, primary_key=True)
    mundo_id = Column(Integer, ForeignKey("futsim.mundo.mundo_id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(50), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    es_actual = Column(Boolean, nullable=False, default=False)
    meta = Column(JSONB, nullable=False, server_default='{}')

    mundo = relationship("Mundo", back_populates="temporadas")

class MundoSnapshot(Base):
    __tablename__ = "mundo_snapshot"
    __table_args__ = (
        UniqueConstraint('mundo_id', 'fecha', 'tick'),
        {"schema": "futsim"}
    )

    snapshot_id = Column(BigInteger, primary_key=True)
    mundo_id = Column(Integer, ForeignKey("futsim.mundo.mundo_id", ondelete="CASCADE"), nullable=False)
    fecha = Column(Date, nullable=False)
    tick = Column(BigInteger, nullable=False, default=0)
    payload = Column(JSONB, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class SimLog(Base):
    __tablename__ = "sim_log"
    __table_args__ = {"schema": "futsim"}

    log_id = Column(BigInteger, primary_key=True)
    mundo_id = Column(Integer, ForeignKey("futsim.mundo.mundo_id", ondelete="CASCADE"), nullable=False)
    tick = Column(BigInteger, nullable=False, default=0)
    fecha = Column(Date, nullable=False)
    accion = Column(String(100), nullable=False)
    payload = Column(JSONB, nullable=False, server_default='{}')
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
