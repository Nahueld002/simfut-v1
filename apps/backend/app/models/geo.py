from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Float, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.models.base import Base
import app.models.common as common # Help SQLAlchemy find CatParametro

class Confederacion(Base):
    __tablename__ = "confederacion"
    __table_args__ = {"schema": "futsim"}

    confederacion_id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False, unique=True)
    acronimo = Column(String(10), unique=True)
    logo_media_id = Column(UUID(as_uuid=True), ForeignKey("futsim.media_asset.media_id"))
    reputacion_base = Column(Integer, nullable=False, default=5000)
    meta = Column(JSONB, nullable=False, server_default='{}')

class Pais(Base):
    __tablename__ = "pais"
    __table_args__ = (
        CheckConstraint('nivel_futbolistico BETWEEN 1 AND 100', name='ck_pais_nivel'),
        {"schema": "futsim"}
    )

    pais_id = Column(Integer, primary_key=True)
    confederacion_id = Column(Integer, ForeignKey("futsim.confederacion.confederacion_id"))
    nombre = Column(String(150), nullable=False, unique=True)
    iso_code = Column(String(3), nullable=False, unique=True)
    gentilicio = Column(String(50))
    bandera_media_id = Column(UUID(as_uuid=True), ForeignKey("futsim.media_asset.media_id"))
    nivel_futbolistico = Column(Integer, nullable=False, default=50)
    poblacion = Column(BigInteger)
    meta = Column(JSONB, nullable=False, server_default='{}')

class Region(Base):
    __tablename__ = "region"
    __table_args__ = (
        UniqueConstraint('pais_id', 'nombre'),
        {"schema": "futsim"}
    )

    region_id = Column(Integer, primary_key=True)
    pais_id = Column(Integer, ForeignKey("futsim.pais.pais_id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(100), nullable=False)
    tipo_region = Column(String(50), nullable=False)
    meta = Column(JSONB, nullable=False, server_default='{}')

class PerfilClimatico(Base):
    __tablename__ = "perfil_climatico"
    __table_args__ = {"schema": "futsim"}

    perfil_id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    codigo_koppen = Column(String(5))
    temp_promedio_verano = Column(Float)
    temp_promedio_invierno = Column(Float)
    altitud_media = Column(Integer, nullable=False, default=0)
    tags = Column(JSONB, nullable=False, server_default='[]')
    ventaja_local_climatica = Column(Float, nullable=False, default=1.0)
    meta = Column(JSONB, nullable=False, server_default='{}')

class Ciudad(Base):
    __tablename__ = "ciudad"
    __table_args__ = (
        UniqueConstraint('region_id', 'nombre'),
        {"schema": "futsim"}
    )

    ciudad_id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey("futsim.region.region_id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(100), nullable=False)
    perfil_climatico_id = Column(Integer, ForeignKey("futsim.perfil_climatico.perfil_id"))
    coordenadas = Column(String) # Storing as text (lat,lon) for now
    poblacion = Column(Integer)
    meta = Column(JSONB, nullable=False, server_default='{}')

    region = relationship("Region")

class Estadio(Base):
    __tablename__ = "estadio"
    __table_args__ = {"schema": "futsim"}

    estadio_id = Column(Integer, primary_key=True)
    ciudad_id = Column(Integer, ForeignKey("futsim.ciudad.ciudad_id"))
    nombre = Column(String(150), nullable=False)
    capacidad = Column(Integer, nullable=False, default=0)
    
    # [REFACTOR] Ahora apunta a cat_parametro (Dominio: TIPO_CESPED)
    tipo_cesped_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"))
    
    foto_media_id = Column(UUID(as_uuid=True), ForeignKey("futsim.media_asset.media_id"))
    estado_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"), nullable=False)
    meta = Column(JSONB, nullable=False, server_default='{}')

    # Relationships
    tipo_cesped = relationship("CatParametro", foreign_keys=[tipo_cesped_id])
    estado = relationship("CatParametro", foreign_keys=[estado_id])

class Asociacion(Base):
    __tablename__ = "asociacion"
    __table_args__ = (
        UniqueConstraint('confederacion_id', 'nombre'),
        {"schema": "futsim"}
    )

    asociacion_id = Column(Integer, primary_key=True)
    confederacion_id = Column(Integer, ForeignKey("futsim.confederacion.confederacion_id"))
    pais_id = Column(Integer, ForeignKey("futsim.pais.pais_id"))
    nombre = Column(String(100), nullable=False)
    acronimo = Column(String(20))
    logo_media_id = Column(UUID(as_uuid=True), ForeignKey("futsim.media_asset.media_id"))
    meta = Column(JSONB, nullable=False, server_default='{}')
