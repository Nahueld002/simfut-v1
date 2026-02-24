from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, ForeignKey, func, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import Base

class CatDominio(Base):
    __tablename__ = "cat_dominio"
    __table_args__ = {"schema": "futsim"}

    dominio_id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True)

    parametros = relationship("CatParametro", back_populates="dominio", cascade="all, delete-orphan")

class CatParametro(Base):
    __tablename__ = "cat_parametro"
    __table_args__ = {"schema": "futsim"}

    parametro_id = Column(Integer, primary_key=True)
    dominio_id = Column(Integer, ForeignKey("futsim.cat_dominio.dominio_id"), nullable=False)
    codigo = Column(String(50), nullable=False)
    descripcion = Column(String(255))
    orden = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    metadatos = Column(JSONB, server_default='{}')

    dominio = relationship("CatDominio", back_populates="parametros")

class MediaAsset(Base):
    __tablename__ = "media_asset"
    __table_args__ = {"schema": "futsim"}

    media_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, nullable=False)
    mime_type = Column(Text)
    ancho = Column(Integer)
    alto = Column(Integer)
    bytes = Column(BigInteger)
    checksum = Column(Text)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    meta = Column(JSONB, nullable=False, server_default='{}')
