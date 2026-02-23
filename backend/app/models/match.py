from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Float, CheckConstraint, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base

class Partido(Base):
    __tablename__ = "partido"
    __table_args__ = (
        CheckConstraint('local_equipo_id <> visita_equipo_id'),
        {"schema": "futsim"}
    )

    partido_id = Column(BigInteger, primary_key=True)
    edicion_id = Column(Integer, ForeignKey("futsim.competencia_edicion.edicion_id", ondelete="CASCADE"), nullable=False)
    etapa_id = Column(Integer, ForeignKey("futsim.etapa.etapa_id", ondelete="CASCADE"), nullable=False)
    ronda_id = Column(Integer, ForeignKey("futsim.ronda.ronda_id", ondelete="SET NULL"))
    grupo_id = Column(Integer, ForeignKey("futsim.grupo.grupo_id", ondelete="SET NULL"))

    local_equipo_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id"), nullable=False)
    visita_equipo_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id"), nullable=False)

    estadio_real_id = Column(Integer, ForeignKey("futsim.estadio.estadio_id"))
    es_neutral = Column(Boolean, nullable=False, default=False)
    ciudad_id = Column(Integer, ForeignKey("futsim.ciudad.ciudad_id"))

    fecha_hora = Column(DateTime)
    jornada = Column(Integer)
    fase_label = Column(String(50))

    asistencia = Column(Integer)

    goles_local = Column(Integer)
    goles_visita = Column(Integer)
    penales_local = Column(Integer)
    penales_visita = Column(Integer)

    estado_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"), nullable=False, server_default='25')
    reporte_motor = Column(JSONB, nullable=False, server_default='{}')

    # Relationships
    estado = relationship("CatParametro", foreign_keys=[estado_id])
    clima = relationship("PartidoClima", back_populates="partido", uselist=False, cascade="all, delete-orphan")
    contexto = relationship("PartidoContexto", back_populates="partido", uselist=False, cascade="all, delete-orphan")
    stats = relationship("PartidoStatsEquipo", back_populates="partido", cascade="all, delete-orphan")

class PartidoClima(Base):
    __tablename__ = "partido_clima"
    __table_args__ = {"schema": "futsim"}

    partido_id = Column(BigInteger, ForeignKey("futsim.partido.partido_id", ondelete="CASCADE"), primary_key=True)
    temperatura_c = Column(Float)
    humedad = Column(Float)
    viento_kmh = Column(Float)
    lluvia_mm = Column(Float)
    
    # [REFACTOR] Apunta a cat_parametro (Dominio: CLIMA_CONDICION)
    condicion_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"))
    
    tags = Column(JSONB, nullable=False, server_default='[]')
    meta = Column(JSONB, nullable=False, server_default='{}')

    partido = relationship("Partido", back_populates="clima")
    
    # Relationships
    condicion = relationship("CatParametro", foreign_keys=[condicion_id])

class PartidoContexto(Base):
    __tablename__ = "partido_contexto"
    __table_args__ = (
        CheckConstraint('intensidad_hinchada BETWEEN 0 AND 100'),
        CheckConstraint('presion BETWEEN 0 AND 100'),
        {"schema": "futsim"}
    )

    partido_id = Column(BigInteger, ForeignKey("futsim.partido.partido_id", ondelete="CASCADE"), primary_key=True)
    intensidad_hinchada = Column(Integer, nullable=False, default=50)
    viaje_km_visita = Column(Integer)
    altitud_m = Column(Integer)
    rivalidad_intensidad = Column(Integer)
    presion = Column(Integer, nullable=False, default=50)
    external = Column(JSONB, nullable=False, server_default='{}')

    partido = relationship("Partido", back_populates="contexto")

class PartidoStatsEquipo(Base):
    __tablename__ = "partido_stats_equipo"
    __table_args__ = {"schema": "futsim"}

    partido_id = Column(BigInteger, ForeignKey("futsim.partido.partido_id", ondelete="CASCADE"), primary_key=True)
    equipo_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"), primary_key=True)
    es_local = Column(Boolean, nullable=False)

    xg = Column(Float)
    tiros = Column(Integer)
    tiros_arco = Column(Integer)
    posesion = Column(Float)
    corners = Column(Integer)
    faltas = Column(Integer)
    amarillas = Column(Integer)
    rojas = Column(Integer)

    delta_elo = Column(Float)
    payload = Column(JSONB, nullable=False, server_default='{}')

    partido = relationship("Partido", back_populates="stats")
