from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Float, CheckConstraint, UniqueConstraint, Date, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from app.models.base import Base

class SistemaRanking(Base):
    __tablename__ = "sistema_ranking"
    __table_args__ = (
        CheckConstraint("alcance IN ('WORLD','CONFED','PAIS','COMPETENCIA')"),
        CheckConstraint('ventana_anios BETWEEN 1 AND 20'),
        UniqueConstraint('mundo_id', 'nombre'),
        {"schema": "futsim"}
    )

    sistema_id = Column(Integer, primary_key=True)
    mundo_id = Column(Integer, ForeignKey("futsim.mundo.mundo_id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(100), nullable=False)
    alcance = Column(String(30), nullable=False)
    ventana_anios = Column(Integer, nullable=False, default=5)
    reglas_calculo = Column(JSONB, nullable=False)
    
    confederacion_id = Column(Integer, ForeignKey("futsim.confederacion.confederacion_id"))
    pais_id = Column(Integer, ForeignKey("futsim.pais.pais_id"))
    competencia_id = Column(Integer, ForeignKey("futsim.competencia.competencia_id"))
    meta = Column(JSONB, nullable=False, server_default='{}')

class RankingEntrada(Base):
    __tablename__ = "ranking_entrada"
    __table_args__ = (
        CheckConstraint("""
            (CASE WHEN equipo_id IS NULL THEN 0 ELSE 1 END) +
            (CASE WHEN pais_id IS NULL THEN 0 ELSE 1 END) +
            (CASE WHEN confederacion_id IS NULL THEN 0 ELSE 1 END) +
            (CASE WHEN competencia_id IS NULL THEN 0 ELSE 1 END) = 1
        """, name='ck_ranking_polymorphic'),
        {"schema": "futsim"}
    )

    entrada_id = Column(BigInteger, primary_key=True)
    sistema_id = Column(Integer, ForeignKey("futsim.sistema_ranking.sistema_id", ondelete="CASCADE"), nullable=False)
    temporada_id = Column(Integer, ForeignKey("futsim.temporada.temporada_id", ondelete="CASCADE"))
    at_date = Column(Date, nullable=False, server_default=func.current_date())

    equipo_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"))
    pais_id = Column(Integer, ForeignKey("futsim.pais.pais_id", ondelete="CASCADE"))
    confederacion_id = Column(Integer, ForeignKey("futsim.confederacion.confederacion_id", ondelete="CASCADE"))
    competencia_id = Column(Integer, ForeignKey("futsim.competencia.competencia_id", ondelete="CASCADE"))

    puntos_totales = Column(Float, nullable=False, default=0)
    ranking_posicion = Column(Integer)
    historial_puntos = Column(JSONB, nullable=False, server_default='{}')

class ReglaAsignacionCupos(Base):
    __tablename__ = "regla_asignacion_cupos"
    __table_args__ = {"schema": "futsim"}

    asignacion_id = Column(Integer, primary_key=True)
    mundo_id = Column(Integer, ForeignKey("futsim.mundo.mundo_id", ondelete="CASCADE"), nullable=False)
    competencia_objetivo_id = Column(Integer, ForeignKey("futsim.competencia.competencia_id", ondelete="CASCADE"), nullable=False)
    sistema_id = Column(Integer, ForeignKey("futsim.sistema_ranking.sistema_id"), nullable=False)
    temporada_id = Column(Integer, ForeignKey("futsim.temporada.temporada_id", ondelete="CASCADE"))
    regla = Column(JSONB, nullable=False)
    nota = Column(Text)

class ReglaClasificacion(Base):
    __tablename__ = "regla_clasificacion"
    __table_args__ = {"schema": "futsim"}

    clasificacion_id = Column(Integer, primary_key=True)
    mundo_id = Column(Integer, ForeignKey("futsim.mundo.mundo_id", ondelete="CASCADE"), nullable=False)
    temporada_id = Column(Integer, ForeignKey("futsim.temporada.temporada_id", ondelete="CASCADE"))

    competencia_fuente_id = Column(Integer, ForeignKey("futsim.competencia.competencia_id", ondelete="CASCADE"), nullable=False)
    etapa_fuente_tipo = Column(String(30))
    grupo_fuente_codigo = Column(String(10))
    posicion_desde = Column(Integer)
    posicion_hasta = Column(Integer)
    condicion_fuente = Column(JSONB, nullable=False, server_default='{}')

    competencia_destino_id = Column(Integer, ForeignKey("futsim.competencia.competencia_id", ondelete="CASCADE"), nullable=False)
    etapa_destino_tipo = Column(String(30))
    hint_ronda_destino = Column(String(30))
    metodo_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"))
    
    # Relationships
    metodo = relationship("CatParametro", foreign_keys=[metodo_id])
    prioridad = Column(Integer, nullable=False, default=0)

    nota = Column(Text)

class SnapshotEquipo(Base):
    __tablename__ = "snapshot_equipo"
    __table_args__ = (
        UniqueConstraint('equipo_id', 'fecha'),
        {"schema": "futsim"}
    )

    snapshot_id = Column(BigInteger, primary_key=True)
    equipo_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"), nullable=False)
    fecha = Column(Date, nullable=False)

    elo = Column(Float)
    reputacion = Column(Integer)
    presupuesto_fichajes = Column(Float) # DECIMAL in SQL, Float usually fine for this unless precise billing
    presupuesto_salarial = Column(Float)
    posicion_estimada = Column(Integer)

    meta = Column(JSONB, nullable=False, server_default='{}')

class HistoriaNarrativa(Base):
    __tablename__ = "historia_narrativa"
    __table_args__ = (
        CheckConstraint('importancia BETWEEN 1 AND 10'),
        {"schema": "futsim"}
    )

    historia_id = Column(Integer, primary_key=True)
    mundo_id = Column(Integer, ForeignKey("futsim.mundo.mundo_id", ondelete="CASCADE"), nullable=False)
    fecha_generacion = Column(Date, nullable=False, server_default=func.current_date())
    titulo = Column(String(150), nullable=False)
    tipo_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"))
    
    # Relationships
    tipo = relationship("CatParametro", foreign_keys=[tipo_id])
    importancia = Column(Integer, nullable=False, default=1)

    equipo_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="SET NULL"))
    competencia_id = Column(Integer, ForeignKey("futsim.competencia.competencia_id", ondelete="SET NULL"))
    pais_id = Column(Integer, ForeignKey("futsim.pais.pais_id", ondelete="SET NULL"))

    resumen_texto = Column(Text)
    datos_clave = Column(JSONB, nullable=False, server_default='{}')

class Noticia(Base):
    __tablename__ = "noticia"
    __table_args__ = {"schema": "futsim"}

    noticia_id = Column(BigInteger, primary_key=True)
    mundo_id = Column(Integer, ForeignKey("futsim.mundo.mundo_id", ondelete="CASCADE"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False, server_default=func.now())
    tipo_id = Column(Integer, ForeignKey("futsim.cat_parametro.parametro_id"))
    
    # Relationships
    tipo = relationship("CatParametro", foreign_keys=[tipo_id])
    titular = Column(String(200), nullable=False)
    cuerpo = Column(Text)
    equipos_relacionados = Column(ARRAY(Integer), nullable=False, server_default='{}') # Postgres ARRAY
    competencia_id = Column(Integer, ForeignKey("futsim.competencia.competencia_id", ondelete="SET NULL"))
    meta = Column(JSONB, nullable=False, server_default='{}')

class EstadisticaGlobal(Base):
    __tablename__ = "estadistica_global"
    __table_args__ = (
        UniqueConstraint('mundo_id', 'fecha'),
        {"schema": "futsim"}
    )

    stat_id = Column(Integer, primary_key=True)
    mundo_id = Column(Integer, ForeignKey("futsim.mundo.mundo_id", ondelete="CASCADE"), nullable=False)
    fecha = Column(Date, nullable=False)

    total_goles = Column(Integer, nullable=False, default=0)
    promedio_goles_partido = Column(Float, nullable=False, default=0)
    partidos_jugados = Column(Integer, nullable=False, default=0)
    distribucion_elo = Column(JSONB, nullable=False, server_default='{}')

    meta = Column(JSONB, nullable=False, server_default='{}')

class EquipoEloHist(Base):
    __tablename__ = "equipo_elo_hist"
    __table_args__ = {"schema": "futsim"}

    equipo_id = Column(Integer, ForeignKey("futsim.equipo.equipo_id", ondelete="CASCADE"), primary_key=True)
    fecha = Column(Date, nullable=False, primary_key=True)
    elo = Column(Float, nullable=False)
    potencial_basal = Column(Integer, nullable=False)
    volatilidad = Column(Integer, nullable=False)
    snapshot = Column(JSONB, nullable=False, server_default='{}')
