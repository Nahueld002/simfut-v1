-- =============================================
-- Drop table
-- =============================================
DROP TABLE IF EXISTS logelo CASCADE;
DROP TABLE IF EXISTS tablaposiciones CASCADE;
DROP TABLE IF EXISTS partido CASCADE;
DROP TABLE IF EXISTS palmares CASCADE;
DROP TABLE IF EXISTS torneoascenso CASCADE;
DROP TABLE IF EXISTS torneodescensos CASCADE;
DROP TABLE IF EXISTS torneoresultados CASCADE;
DROP TABLE IF EXISTS torneoequipo CASCADE;
DROP TABLE IF EXISTS equipo CASCADE;
DROP TABLE IF EXISTS torneopais CASCADE;
DROP TABLE IF EXISTS torneo CASCADE;
DROP TABLE IF EXISTS ciudad CASCADE;
DROP TABLE IF EXISTS region CASCADE;
DROP TABLE IF EXISTS pais CASCADE;
DROP TABLE IF EXISTS confederacion CASCADE;

-- =============================================
-- Create table
-- =============================================

-- Tabla Confederacion
CREATE TABLE confederacion (
    confederacionid SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- Tabla Pais
CREATE TABLE pais (
    paisid SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigofifa VARCHAR(10) NOT NULL UNIQUE,
    confederacionid INT NOT NULL,
    pertenecefifa BOOLEAN DEFAULT TRUE, 
    FOREIGN KEY (confederacionid) REFERENCES confederacion(confederacionid)
);

-- Tabla Region
CREATE TABLE region (
    regionid SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tiporegion VARCHAR(50) NOT NULL,
    paisid INT NOT NULL,
    FOREIGN KEY (paisid) REFERENCES pais(paisid)
);

-- Tabla Ciudad
CREATE TABLE ciudad (
    ciudadid SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    regionid INT NOT NULL,
    escapital BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (regionid) REFERENCES region(regionid)
);

-- Tabla Torneo
CREATE TABLE torneo (
    torneoid SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipotorneo VARCHAR(50) NOT NULL,
    categoria VARCHAR(50) NULL,
    confederacionid INT NULL,
    paisid INT NULL,
    regionid INT NULL,
    ciudadid INT NULL,
    estado VARCHAR(20) DEFAULT 'Activo',
    FOREIGN KEY (confederacionid) REFERENCES confederacion(confederacionid),
    FOREIGN KEY (paisid) REFERENCES pais(paisid),
    FOREIGN KEY (regionid) REFERENCES region(regionid),
    FOREIGN KEY (ciudadid) REFERENCES ciudad(ciudadid),
    CONSTRAINT chk_estado_torneo CHECK (estado IN ('Activo', 'Suspendido', 'Extinto'))
);

-- Tabla TorneoPais (Multinacionales)
CREATE TABLE torneopais (
    torneopaisid SERIAL PRIMARY KEY,
    torneoid INT NOT NULL,
    paisid INT NOT NULL,
    FOREIGN KEY (torneoid) REFERENCES torneo(torneoid),
    FOREIGN KEY (paisid) REFERENCES pais(paisid)
);

-- Tabla Equipo
CREATE TABLE equipo (
    equipoid SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigoequipo VARCHAR(20) NOT NULL,
    regionid INT NULL,
    ciudadid INT NULL,
    aniofundacion SMALLINT NULL, 
    elo FLOAT DEFAULT 1000.00,
    tipoequipo VARCHAR(100),
    estado VARCHAR(20) DEFAULT 'Activo',
    FOREIGN KEY (regionid) REFERENCES region(regionid),
    FOREIGN KEY (ciudadid) REFERENCES ciudad(ciudadid),
    CONSTRAINT uq_codigoequipo_ciudad UNIQUE (codigoequipo, ciudadid),
    CONSTRAINT uq_codigoequipo_region UNIQUE (codigoequipo, regionid),
    CONSTRAINT chk_club_elo CHECK (elo > 0),
    CONSTRAINT chk_estado_equipo CHECK (estado IN ('Activo', 'Desaparecido', 'Desafiliado', 'Inactivo', 'Suspendido', 'Fusionado'))
);

-- Tabla TorneoEquipo
CREATE TABLE torneoequipo (
    torneoequipoid SERIAL PRIMARY KEY,
    torneoid INT NOT NULL,
    equipoid INT NOT NULL,
    anioparticipacion SMALLINT NOT NULL,
    fase VARCHAR(50) NOT NULL,
    grupo VARCHAR(200) NULL,
    FOREIGN KEY (torneoid) REFERENCES torneo(torneoid),
    FOREIGN KEY (equipoid) REFERENCES equipo(equipoid)
);

-- Tabla Resultados
CREATE TABLE torneoresultados (
    torneoresultadosid SERIAL PRIMARY KEY,
    torneoid INT NOT NULL,
    aniotorneo SMALLINT NOT NULL,
    campeonequipoid INT NULL,
    subcampeonequipoid INT NULL,
    observaciones VARCHAR(250) NULL,
    era VARCHAR(25) NULL,
    FOREIGN KEY (torneoid) REFERENCES torneo(torneoid),
    FOREIGN KEY (campeonequipoid) REFERENCES equipo(equipoid),
    FOREIGN KEY (subcampeonequipoid) REFERENCES equipo(equipoid),
    CONSTRAINT uq_torneo_anio UNIQUE (torneoid, aniotorneo),
    CONSTRAINT chk_era_torneoresultados CHECK (era IN ('Era Amateur', 'Era Profesional'))
);

-- Tabla Descenso
CREATE TABLE torneodescensos (
    torneodescensosid SERIAL PRIMARY KEY,
    descensotorneoequipoid INT NOT NULL,
    torneoorigenid INT NOT NULL,
    torneodestinoid INT NOT NULL,
    aniodescenso SMALLINT NOT NULL,
    FOREIGN KEY (descensotorneoequipoid) REFERENCES torneoequipo(torneoequipoid),
    FOREIGN KEY (torneoorigenid) REFERENCES torneo(torneoid),
    FOREIGN KEY (torneodestinoid) REFERENCES torneo(torneoid),
    CONSTRAINT uq_descenso UNIQUE (descensotorneoequipoid, aniodescenso)
);

-- Tabla Ascenso
CREATE TABLE torneoascenso (
    torneoascensoid SERIAL PRIMARY KEY,
    ascensotorneoequipoid INT NOT NULL,
    torneoorigenid INT NOT NULL,
    torneodestinoid INT NOT NULL,
    anioascenso SMALLINT NOT NULL,
    FOREIGN KEY (ascensotorneoequipoid) REFERENCES torneoequipo(torneoequipoid),
    FOREIGN KEY (torneoorigenid) REFERENCES torneo(torneoid),
    FOREIGN KEY (torneodestinoid) REFERENCES torneo(torneoid),
    CONSTRAINT uq_ascenso UNIQUE (ascensotorneoequipoid, anioascenso)
);

-- Tabla Palmares
CREATE TABLE palmares (
    palmaresid SERIAL PRIMARY KEY,
    aniotitulo SMALLINT NOT NULL,
    equipoid INT NOT NULL,
    torneoid INT NOT NULL,
    FOREIGN KEY (equipoid) REFERENCES equipo(equipoid),
    FOREIGN KEY (torneoid) REFERENCES torneo(torneoid),
    CONSTRAINT uq_palmares UNIQUE (equipoid, torneoid, aniotitulo)
);

-- Tabla Partido
CREATE TABLE partido (
    partidoid SERIAL PRIMARY KEY,
    torneoid INT NOT NULL,
    equipolocaltorneoequipoid INT NOT NULL,
    equipovisitantetorneoequipoid INT NOT NULL,
    goleslocal INT NULL,
    golesvisitante INT NULL,
    nrofecha INT NOT NULL,
    anioparticipacion SMALLINT NOT NULL,
    fase VARCHAR(50) NULL,
    grupo VARCHAR(50) NULL,
    estado VARCHAR(20) DEFAULT 'Pendiente',
    FOREIGN KEY (torneoid) REFERENCES torneo(torneoid),
    FOREIGN KEY (equipolocaltorneoequipoid) REFERENCES torneoequipo(torneoequipoid),
    FOREIGN KEY (equipovisitantetorneoequipoid) REFERENCES torneoequipo(torneoequipoid)
);

-- Tabla Posiciones
CREATE TABLE tablaposiciones (
    tablaposicionesid SERIAL PRIMARY KEY,
    torneoid INT NOT NULL,
    anioparticipacion SMALLINT NOT NULL,
    equipoid INT NOT NULL,
    pj INT DEFAULT 0 NOT NULL,
    pg INT DEFAULT 0 NOT NULL,
    pe INT DEFAULT 0 NOT NULL,
    pp INT DEFAULT 0 NOT NULL,
    gf INT DEFAULT 0 NOT NULL,
    gc INT DEFAULT 0 NOT NULL,
    dg INT DEFAULT 0 NOT NULL,
    pts INT DEFAULT 0 NOT NULL,
    fase VARCHAR(50) NULL,
    grupo VARCHAR(50) NULL,
    FOREIGN KEY (torneoid) REFERENCES torneo(torneoid),
    FOREIGN KEY (equipoid) REFERENCES equipo(equipoid),
    CONSTRAINT uq_torneo_equipo_anio UNIQUE (torneoid, anioparticipacion, equipoid, fase, grupo)
);

-- Tabla LogELO
CREATE TABLE logelo (
    logid SERIAL PRIMARY KEY,
    partidoid INT,
    equipoid INT,
    eloanterior FLOAT,
    elonuevo FLOAT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);