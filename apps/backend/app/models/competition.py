from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Float, CheckConstraint, UniqueConstraint, Date, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

class PerfilSorteo(Base):
    __tablename__ = "perfil_sorteo"
    __table_args__ = {"schema": "futsim"}

    perfil_sorteo_id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    config = Column(JSONB, nullable=False)

class Competencia(Base):
    __tablename__ = "competencia"
    __table_args__ = (
        UniqueConstraint('mundo_id', 'nombre'),
        {"schema": "futsim"}
    )

    competencia_id = Column(Integer, primary_key=True)
    mundo_id = Column(Integer, ForeignKey("futsim.mundo.mundo_id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(150), nullable=False)
    tipo_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"), nullable=False)
    
    confederacion_id = Column(Integer, ForeignKey("futsim.confederacion.confederacion_id"))
    pais_id = Column(Integer, ForeignKey("futsim.pais.pais_id"))
    region_id = Column(Integer, ForeignKey("futsim.region.region_id"))
    asociacion_id = Column(Integer, ForeignKey("futsim.asociacion.asociacion_id"))
    ciudad_id = Column(Integer, ForeignKey("futsim.ciudad.ciudad_id"))
    
    logo_media_id = Column(UUID(as_uuid=True), ForeignKey("futsim.media_asset.media_id"))
    
    reputacion_base = Column(Integer, nullable=False, default=5000)
    configuracion_base = Column(JSONB, nullable=False, server_default='{}')
    meta = Column(JSONB, nullable=False, server_default='{}')

    # Relationships
    tipo = relationship("CatParametro", foreign_keys=[tipo_id])
    ediciones = relationship("CompetenciaEdicion", back_populates="competencia", cascade="all, delete-orphan")

class CompetenciaReputacion(Base):
    __tablename__ = "competencia_reputacion"
    __table_args__ = (
        CheckConstraint("alcance IN ('WORLD','CONFED','PAIS')"),
        {"schema": "futsim"}
    )

    competencia_id = Column(Integer, ForeignKey("futsim.competencia.competencia_id", ondelete="CASCADE"), primary_key=True)
    alcance = Column(String(20), nullable=False, primary_key=True)
    temporada_id = Column(Integer, ForeignKey("futsim.temporada.temporada_id", ondelete="CASCADE"), primary_key=True)
    valor = Column(Integer, nullable=False, default=5000)
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class ReglaElegibilidad(Base):
    __tablename__ = "regla_elegibilidad"
    __table_args__ = {"schema": "futsim"}

    elegibilidad_id = Column(Integer, primary_key=True)
    competencia_id = Column(Integer, ForeignKey("futsim.competencia.competencia_id", ondelete="CASCADE"), nullable=False)
    regla = Column(JSONB, nullable=False)
    nota = Column(Text)

class CompetenciaEdicion(Base):
    __tablename__ = "competencia_edicion"
    __table_args__ = (
        UniqueConstraint('competencia_id', 'temporada_id'),
        {"schema": "futsim"}
    )

    edicion_id = Column(Integer, primary_key=True)
    competencia_id = Column(Integer, ForeignKey("futsim.competencia.competencia_id", ondelete="CASCADE"), nullable=False)
    temporada_id = Column(Integer, ForeignKey("futsim.temporada.temporada_id", ondelete="CASCADE"), nullable=False)
    nombre_display = Column(String(100))
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    
    # [REFACTOR] Ahora apunta a cat_parametro (Dominio: ESTADO_GENERICO)
    estado_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"), nullable=False)
    
    reglas_edicion = Column(JSONB, nullable=False, server_default='{}')
    meta = Column(JSONB, nullable=False, server_default='{}')

    # Relationships
    estado = relationship("CatParametro", foreign_keys=[estado_id])
    competencia = relationship("Competencia", back_populates="ediciones")
    etapas = relationship("Etapa", back_populates="edicion", cascade="all, delete-orphan")

class Etapa(Base):
    __tablename__ = "etapa"
    __table_args__ = (
        UniqueConstraint('edicion_id', 'orden'),
        {"schema": "futsim"}
    )

    etapa_id = Column(Integer, primary_key=True)
    edicion_id = Column(Integer, ForeignKey("futsim.competencia_edicion.edicion_id", ondelete="CASCADE"), nullable=False)
    orden = Column(Integer, nullable=False)
    tipo_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"), nullable=False)
    nombre = Column(String(150), nullable=False)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    config_etapa = Column(JSONB, nullable=False, server_default='{}')
    perfil_sorteo_id = Column(Integer, ForeignKey("futsim.perfil_sorteo.perfil_sorteo_id"))

    # Relationships
    tipo = relationship("CatParametro", foreign_keys=[tipo_id])
    edicion = relationship("CompetenciaEdicion", back_populates="etapas")
    grupos = relationship("Grupo", back_populates="etapa", cascade="all, delete-orphan")
    rondas = relationship("Ronda", back_populates="etapa", cascade="all, delete-orphan")

class Grupo(Base):
    __tablename__ = "grupo"
    __table_args__ = (
        UniqueConstraint('etapa_id', 'codigo'),
        {"schema": "futsim"}
    )

    grupo_id = Column(Integer, primary_key=True)
    etapa_id = Column(Integer, ForeignKey("futsim.etapa.etapa_id", ondelete="CASCADE"), nullable=False)
    codigo = Column(String(10), nullable=False)
    nombre = Column(String(50))
    meta = Column(JSONB, nullable=False, server_default='{}')

    etapa = relationship("Etapa", back_populates="grupos")

class Ronda(Base):
    __tablename__ = "ronda"
    __table_args__ = (
        UniqueConstraint('etapa_id', 'grupo_id', 'numero', 'pierna'),
        {"schema": "futsim"}
    )

    ronda_id = Column(Integer, primary_key=True)
    etapa_id = Column(Integer, ForeignKey("futsim.etapa.etapa_id", ondelete="CASCADE"), nullable=False)
    grupo_id = Column(Integer, ForeignKey("futsim.grupo.grupo_id", ondelete="CASCADE"))
    numero = Column(Integer, nullable=False)
    pierna = Column(Integer, nullable=False, default=1)
    fecha_programada = Column(Date)
    nombre = Column(String(100))
    meta = Column(JSONB, nullable=False, server_default='{}')

    etapa = relationship("Etapa", back_populates="rondas")

class Participante(Base):
    __tablename__ = "participante"
    __table_args__ = (
        UniqueConstraint('edicion_id', 'equipo_id'),
        {"schema": "futsim"}
    )

    participante_id = Column(Integer, primary_key=True)
    edicion_id = Column(Integer, ForeignKey("futsim.competencia_edicion.edicion_id", ondelete="CASCADE"), nullable=False)
    equipo_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"), nullable=False)
    
    metodo_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"))
    
    # Relationships
    metodo = relationship("CatParametro", foreign_keys=[metodo_id])
    seed = Column(Integer)
    bombo_sorteo = Column(Integer)
    grupo_id_inicial = Column(Integer, ForeignKey("futsim.grupo.grupo_id"))
    grupo_inicial_texto = Column(String(50))
    
    posicion_final = Column(Integer)
    ronda_eliminacion = Column(String(50))
    puntos_ranking_ganados = Column(Float, nullable=False, default=0)
    
    meta = Column(JSONB, nullable=False, server_default='{}')

class TablaPosiciones(Base):
    __tablename__ = "tabla_posiciones"
    __table_args__ = {"schema": "futsim"}

    edicion_id = Column(Integer, ForeignKey("futsim.competencia_edicion.edicion_id", ondelete="CASCADE"), primary_key=True)
    etapa_id = Column(Integer, ForeignKey("futsim.etapa.etapa_id", ondelete="CASCADE"), primary_key=True)
    grupo_id = Column(Integer, ForeignKey("futsim.grupo.grupo_id", ondelete="CASCADE"), primary_key=True)
    equipo_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"), primary_key=True)

    pj = Column(Integer, nullable=False, default=0)
    pg = Column(Integer, nullable=False, default=0)
    pe = Column(Integer, nullable=False, default=0)
    pp = Column(Integer, nullable=False, default=0)
    gf = Column(Integer, nullable=False, default=0)
    gc = Column(Integer, nullable=False, default=0)
    dg = Column(Integer, nullable=False, default=0)
    pts = Column(Integer, nullable=False, default=0)
    forma = Column(String(10))
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    meta = Column(JSONB, nullable=False, server_default='{}')
