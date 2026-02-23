from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Float, CheckConstraint, UniqueConstraint, Date, DECIMAL, Text, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

class Equipo(Base):
    __tablename__ = "equipo"
    __table_args__ = (
        UniqueConstraint('mundo_id', 'nombre'),
        {"schema": "futsim"}
    )

    equipo_id = Column(Integer, primary_key=True)
    mundo_id = Column(Integer, ForeignKey("futsim.mundo.mundo_id", ondelete="CASCADE"), nullable=False)
    
    nombre = Column(String(150), nullable=False)
    codigo_tla = Column(String(10))
    anio_fundacion = Column(Integer)
    
    ciudad_sede_id = Column(Integer, ForeignKey("futsim.ciudad.ciudad_id"))
    pais_origen_id = Column(Integer, ForeignKey("futsim.pais.pais_id"))
    asociacion_liga_id = Column(Integer, ForeignKey("futsim.asociacion.asociacion_id"))
    estadio_principal_id = Column(Integer, ForeignKey("futsim.estadio.estadio_id"))
    
    escudo_media_id = Column(UUID(as_uuid=True), ForeignKey("futsim.media_asset.media_id"))
    colores = Column(JSONB, nullable=False, server_default='{}')
    
    estado_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"))
    meta = Column(JSONB, nullable=False, server_default='{}')

    # Relationships
    estado = relationship("CatParametro", foreign_keys=[estado_id])

    # One-to-one relationships
    rating = relationship("EquipoRatingActual", back_populates="equipo", uselist=False, cascade="all, delete-orphan")
    institucion = relationship("EquipoInstitucion", back_populates="equipo", uselist=False, cascade="all, delete-orphan")
    finanzas = relationship("EquipoFinanzas", back_populates="equipo", uselist=False, cascade="all, delete-orphan")
    
    # Locations
    pais = relationship("Pais", foreign_keys=[pais_origen_id])
    ciudad_sede = relationship("Ciudad", foreign_keys=[ciudad_sede_id])
    
    # Media
    escudo_media = relationship("MediaAsset", foreign_keys=[escudo_media_id])

    # One-to-Many relationships
    estadio_hist = relationship("EquipoEstadioHist", backref="equipo", cascade="all, delete-orphan")

class EquipoEstadioHist(Base):
    __tablename__ = "equipo_estadio_hist"
    __table_args__ = {"schema": "futsim"}

    equipo_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"), primary_key=True)
    estadio_id = Column(Integer, ForeignKey("futsim.estadio.estadio_id"), primary_key=True)
    fecha_inicio = Column(Date, nullable=False, primary_key=True)
    fecha_fin = Column(Date)
    motivo = Column(String(100))
    es_principal = Column(Boolean, nullable=False, default=True)

class EquipoRatingActual(Base):
    __tablename__ = "equipo_rating_actual"
    __table_args__ = (
        CheckConstraint('ataque BETWEEN 1 AND 100'),
        CheckConstraint('defensa BETWEEN 1 AND 100'),
        CheckConstraint('mediocampo BETWEEN 1 AND 100'),
        CheckConstraint('moral BETWEEN 0 AND 100'),
        CheckConstraint('fatiga BETWEEN 0 AND 100'),
        CheckConstraint('cohesion BETWEEN 0 AND 100'),
        CheckConstraint('disciplina BETWEEN 0 AND 100'),
        {"schema": "futsim"}
    )

    equipo_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"), primary_key=True)
    elo_actual = Column(Float, nullable=True, default=1200)
    ataque = Column(Integer, nullable=False, default=50)
    defensa = Column(Integer, nullable=False, default=50)
    mediocampo = Column(Integer, nullable=False, default=50)
    
    moral = Column(Integer, nullable=False, default=50)
    fatiga = Column(Integer, nullable=False, default=0)
    cohesion = Column(Integer, nullable=False, default=50)
    disciplina = Column(Integer, nullable=False, default=50)
    
    # [REFACTOR] Columnas tácticas FK
    estilo_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"))
    salida_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"))
    transicion_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"))
    
    tactica_detalle = Column(JSONB, nullable=False, server_default='{}')

    # Relationships
    estilo = relationship("CatParametro", foreign_keys=[estilo_id])
    salida = relationship("CatParametro", foreign_keys=[salida_id])
    transicion = relationship("CatParametro", foreign_keys=[transicion_id])
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    equipo = relationship("Equipo", back_populates="rating")

class EquipoInstitucion(Base):
    __tablename__ = "equipo_institucion"
    __table_args__ = (
        CheckConstraint('volatilidad BETWEEN 1 AND 100'),
        CheckConstraint('infraestructura BETWEEN 1 AND 20'),
        CheckConstraint('nivel_scouting BETWEEN 1 AND 20'),
        CheckConstraint('nivel_entrenamiento BETWEEN 1 AND 20'),
        CheckConstraint('nivel_juveniles BETWEEN 1 AND 20'),
        CheckConstraint('estabilidad_directiva BETWEEN 1 AND 20'),
        {"schema": "futsim"}
    )

    equipo_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"), primary_key=True)
    potencial_basal = Column(Integer, nullable=False, default=1200)
    volatilidad = Column(Integer, nullable=False, default=10)
    
    infraestructura = Column(Integer, nullable=False, default=10)
    nivel_scouting = Column(Integer, nullable=False, default=10)
    nivel_entrenamiento = Column(Integer, nullable=False, default=10)
    nivel_juveniles = Column(Integer, nullable=False, default=10)
    
    estabilidad_directiva = Column(Integer, nullable=False, default=10)
    hinchada = Column(Integer, nullable=False, default=1000)
    reputacion_historica = Column(Integer, nullable=False, default=5000)
    meta = Column(JSONB, nullable=False, server_default='{}')

    equipo = relationship("Equipo", back_populates="institucion")

class EquipoFinanzas(Base):
    __tablename__ = "equipo_finanzas"
    __table_args__ = (
        CheckConstraint('poder_economico_base BETWEEN 1 AND 20'),
        CheckConstraint('paciencia_directiva BETWEEN 1 AND 20'),
        {"schema": "futsim"}
    )

    equipo_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"), primary_key=True)
    moneda_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"), nullable=False)
    presupuesto_fichajes = Column(DECIMAL(18,2), nullable=False, default=0)
    presupuesto_salarial = Column(DECIMAL(18,2), nullable=False, default=0)
    deuda_total = Column(DECIMAL(18,2), nullable=False, default=0)
    
    poder_economico_base = Column(Integer, nullable=False, default=10)
    tipo_propiedad_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"))
    
    # Relationships
    moneda = relationship("CatParametro", foreign_keys=[moneda_id])
    tipo_propiedad = relationship("CatParametro", foreign_keys=[tipo_propiedad_id])
    paciencia_directiva = Column(Integer, nullable=False, default=10)
    
    actualizado_en = Column(Date, nullable=False, server_default=func.current_date())
    meta = Column(JSONB, nullable=False, server_default='{}')

    equipo = relationship("Equipo", back_populates="finanzas")

class Rivalidad(Base):
    __tablename__ = "rivalidad"
    __table_args__ = (
        CheckConstraint('equipo_a_id < equipo_b_id'),
        UniqueConstraint('equipo_a_id', 'equipo_b_id'),
        CheckConstraint('intensidad BETWEEN 0 AND 100'),
        {"schema": "futsim"}
    )

    rivalidad_id = Column(Integer, primary_key=True)
    equipo_a_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"), nullable=False)
    equipo_b_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(150))
    intensidad = Column(Integer, nullable=False, default=50)
    meta = Column(JSONB, nullable=False, server_default='{}')

class HistorialEnfrentamiento(Base):
    __tablename__ = "historial_enfrentamiento"
    __table_args__ = (
        CheckConstraint('equipo_a_id < equipo_b_id'),
        UniqueConstraint('equipo_a_id', 'equipo_b_id'),
        {"schema": "futsim"}
    )

    historial_id = Column(Integer, primary_key=True)
    equipo_a_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"), nullable=False)
    equipo_b_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"), nullable=False)
    
    partidos_jugados = Column(Integer, nullable=False, default=0)
    victorias_a = Column(Integer, nullable=False, default=0)
    victorias_b = Column(Integer, nullable=False, default=0)
    empates = Column(Integer, nullable=False, default=0)
    goles_a = Column(Integer, nullable=False, default=0)
    goles_b = Column(Integer, nullable=False, default=0)
    
    ultimo_partido_fecha = Column(Date)
    ultimo_ganador_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id"))
    
    meta = Column(JSONB, nullable=False, server_default='{}')

class EventoEquipo(Base):
    __tablename__ = "evento_equipo"
    __table_args__ = (
        CheckConstraint('severidad BETWEEN 1 AND 10'),
        {"schema": "futsim"}
    )

    evento_id = Column(Integer, primary_key=True)
    mundo_id = Column(Integer, ForeignKey("futsim.mundo.mundo_id", ondelete="CASCADE"), nullable=False)
    equipo_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)
    tipo_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"))
    
    # Relationships
    tipo = relationship("CatParametro", foreign_keys=[tipo_id])
    severidad = Column(Integer, nullable=False, default=1)
    modificadores = Column(JSONB, nullable=False, server_default='{}')
    descripcion = Column(Text)
from sqlalchemy import Boolean
from sqlalchemy import DateTime
import datetime
