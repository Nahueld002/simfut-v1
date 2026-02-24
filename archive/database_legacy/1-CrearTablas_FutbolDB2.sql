/*CREATE DATABASE FutbolDB2
GO*/

USE FutbolDB2
GO

-- Crear tabla Confederaci�n
CREATE TABLE Confederacion (
	ConfederacionID INT IDENTITY (1,1) PRIMARY KEY, -- Indica que es la clave primaria y tiene un autoincremento de 1 en 1
	Nombre VARCHAR(20) NOT NULL, -- Nombre de la confederaci�n (m�ximo 20 caracteres)
);

-- Crear tabla Pa�s
CREATE TABLE Pais (
	PaisID INT IDENTITY(1,1) PRIMARY KEY, -- Clave primaria con autoincremento
	Nombre NVARCHAR(50) NOT NULL, -- Nombre del pa�s (m�ximo 50 caracteres)
	CodigoFIFA VARCHAR(3) NOT NULL UNIQUE, -- C�digo FIFA �nico del pa�s
	ConfederacionID INT NOT NULL, -- Relaci�n con la tabla Confederaci�n
	PerteneceFIFA BIT DEFAULT 1, --0 para 'No pertenece' y 1 para 'S� pertenece'
	FOREIGN KEY (ConfederacionID) REFERENCES Confederacion(ConfederacionID) -- Llave for�nea a Confederaci�n
);


-- Crea tabla para Regiones o Divisiones Pol�ticas PRIMARIAS como Departamentos, Condados, Provincias, Estados, Federaciones, etc. 
CREATE TABLE Region (
	RegionID INT IDENTITY (1,1) PRIMARY KEY,
	Nombre VARCHAR(50) NOT NULL,
	TipoRegion VARCHAR(50) NOT NULL,
	PaisID INT NOT NULL,
	FOREIGN KEY (PaisID) REFERENCES Pais(PaisID)
);


-- Crear tabla Ciudad
CREATE TABLE Ciudad (
    	CiudadID INT IDENTITY(1,1) PRIMARY KEY, -- Clave primaria con autoincremento
    	Nombre NVARCHAR(100) NOT NULL, -- Nombre de la ciudad
    	RegionID INT NOT NULL, -- Relaci�n con el departamento al que pertenece
    	EsCapital BIT NOT NULL DEFAULT 0, -- Indicador de capital: 0 = No, 1 = S�
    	FOREIGN KEY (RegionID) REFERENCES Region(RegionID) -- Llave for�nea a Departamento
);


-- Crea tabla para Torneos nacionales e internacionales
CREATE TABLE Torneo (
    TorneoID INT IDENTITY(1,1) PRIMARY KEY,
    Nombre NVARCHAR(100) NOT NULL, -- Nombre del torneo
    TipoTorneo NVARCHAR(50) NOT NULL, -- Liga, Copa, Clasificatoria, Play-Offs, Regional
    Categoria NVARCHAR(50) NULL, -- Ejemplo: Primera Divisi�n, Segunda Divisi�n, etc.
    ConfederacionID INT NULL, --
	PaisID INT NULL,
	RegionID INT NULL,
	CiudadID INT NULL,
	Estado NVARCHAR(20) NOT NULL DEFAULT 'Activo', 
    FOREIGN KEY (ConfederacionID) REFERENCES Confederacion(ConfederacionID),
	FOREIGN KEY (PaisID) REFERENCES Pais(PaisID),
	FOREIGN KEY (RegionID) REFERENCES Region(RegionID),
	FOREIGN KEY (CiudadID) REFERENCES Ciudad(CiudadID),
    CONSTRAINT CHK_Estado_Torneo CHECK (Estado IN ('Activo', 'Suspendido', 'Extinto'))
);

-- Crea tabla para Torneos multinacionales
CREATE TABLE TorneoPais (
    TorneoPaisID INT IDENTITY(1,1) PRIMARY KEY,
    TorneoID INT NOT NULL, -- Relaci�n con el torneo
    PaisID INT NOT NULL, -- Relaci�n con el pa�s
    FOREIGN KEY (TorneoID) REFERENCES Torneo(TorneoID),
    FOREIGN KEY (PaisID) REFERENCES Pais(PaisID)
);

-- Crear tabla Equipo con m�s estados
CREATE TABLE Equipo (
    EquipoID INT IDENTITY(1,1) PRIMARY KEY,
    Nombre NVARCHAR(100) NOT NULL,
    CodigoEquipo VARCHAR(10) NOT NULL,
    RegionID INT NULL,
    CiudadID INT NULL,
    AñoFundacion SMALLINT NULL,
    ELO FLOAT DEFAULT 1000.00 NULL,
    TipoEquipo NVARCHAR(100),
    Estado NVARCHAR(20) NOT NULL DEFAULT 'Activo',
    FOREIGN KEY (RegionID) REFERENCES Region(RegionID),
    FOREIGN KEY (CiudadID) REFERENCES Ciudad(CiudadID),
    CONSTRAINT UQ_CodigoEquipo_Ciudad UNIQUE (CodigoEquipo, CiudadID),
    CONSTRAINT UQ_CodigoEquipo_Region UNIQUE (CodigoEquipo, RegionID),
    CONSTRAINT CHK_Club_ELO CHECK (ELO > 0),
    CONSTRAINT CHK_Estado_Equipo CHECK (Estado IN ('Activo', 'Desaparecido', 'Desafiliado', 'Inactivo', 'Suspendido', 'Fusionado'))
);

--Crear tabla TorneoEquipo
CREATE TABLE TorneoEquipo (
    TorneoEquipoID INT IDENTITY(1,1) PRIMARY KEY, -- Clave primaria con autoincremento
    TorneoID INT NOT NULL, -- Relaci�n con el torneo
    EquipoID INT NOT NULL, -- Relaci�n con el club participante
    AñoParticipacion SMALLINT NOT NULL, -- A�o de participaci�n en el torneo
	Fase NVARCHAR(50) NOT NULL, --Fase de Grupos, Liga, etc
    Grupo NVARCHAR(200) NULL, -- (Opcional) Grupo en el torneo
    FOREIGN KEY (TorneoID) REFERENCES Torneo(TorneoID),
    FOREIGN KEY (EquipoID) REFERENCES Equipo(EquipoID)
);

--Crear tabla de Resultados de un Torneo
CREATE TABLE TorneoResultados (
    TorneoResultadosID INT IDENTITY(1,1) PRIMARY KEY, 
    TorneoID INT NOT NULL, -- Relaci�n con el torneo
    AñoTorneo SMALLINT NOT NULL, -- A�o del torneo
    CampeonEquipoID INT NULL, -- Equipo que gan� el torneo
    SubcampeonEquipoID INT NULL, -- Equipo subcampe�n
	Observaciones NVARCHAR(250) NULL, --Anotar observaciones
	Era NVARCHAR(25) NULL, --Era Profesional, Era Amateur
    FOREIGN KEY (TorneoID) REFERENCES Torneo(TorneoID),
    FOREIGN KEY (CampeonEquipoID) REFERENCES Equipo(EquipoID),
    FOREIGN KEY (SubcampeonEquipoID) REFERENCES Equipo(EquipoID),
    CONSTRAINT UQ_Torneo_Año UNIQUE (TorneoID, AñoTorneo), -- Un torneo solo puede tener un resultado por a�o
	CONSTRAINT CHK_Era_TorneoResultados CHECK (Era IN ('Era Amateur', 'Era Profesional'))
);

CREATE TABLE TorneoDescensos (
    TorneoDescensosID INT IDENTITY(1,1) PRIMARY KEY,
    DescensoTorneoEquipoID INT NOT NULL, -- Equipo que descendi�
    TorneoOrigenID INT NOT NULL, -- Torneo donde jugaba
    TorneoDestinoID INT NOT NULL, -- Torneo al que desciende
    AñoDescenso SMALLINT NOT NULL, -- A�o del descenso
    FOREIGN KEY (DescensoTorneoEquipoID) REFERENCES TorneoEquipo(TorneoEquipoID),
    FOREIGN KEY (TorneoOrigenID) REFERENCES Torneo(TorneoID),
    FOREIGN KEY (TorneoDestinoID) REFERENCES Torneo(TorneoID),
    CONSTRAINT UQ_Descenso UNIQUE (DescensoTorneoEquipoID, AñoDescenso) -- Un equipo no puede descender dos veces el mismo a�o
);

CREATE TABLE TorneoAscenso (
    TorneoAscensoID INT IDENTITY(1,1) PRIMARY KEY,
    AscensoTorneoEquipoID INT NOT NULL, -- Equipo que ascendi�
    TorneoOrigenID INT NOT NULL, -- Torneo de donde ascendi�
    TorneoDestinoID INT NOT NULL, -- Torneo al que ascendi�
    AñoAscenso SMALLINT NOT NULL, -- A�o del ascenso
    FOREIGN KEY (AscensoTorneoEquipoID) REFERENCES TorneoEquipo(TorneoEquipoID),
    FOREIGN KEY (TorneoOrigenID) REFERENCES Torneo(TorneoID),
    FOREIGN KEY (TorneoDestinoID) REFERENCES Torneo(TorneoID),
    CONSTRAINT UQ_Ascenso UNIQUE (AscensoTorneoEquipoID, AñoAscenso) -- Un equipo no puede ascender dos veces el mismo a�o
);


CREATE TABLE Palmares (
    PalmaresID INT IDENTITY(1,1) PRIMARY KEY,
    AñoTitulo SMALLINT NOT NULL, -- A�o del t�tulo
    EquipoID INT NOT NULL, -- Equipo que gan� el t�tulo
    TorneoID INT NOT NULL, -- Torneo donde lo gan�
    FOREIGN KEY (EquipoID) REFERENCES Equipo(EquipoID),
    FOREIGN KEY (TorneoID) REFERENCES Torneo(TorneoID),
    CONSTRAINT UQ_Palmares UNIQUE (EquipoID, TorneoID, AñoTitulo) -- Evita duplicados en t�tulos por torneo y a�o
);

--Crear tabla de partidos
CREATE TABLE Partido (
    PartidoID INT IDENTITY(1,1) PRIMARY KEY, -- Clave primaria autoincremental
    TorneoID INT NOT NULL, -- Relaci�n con el torneo
    EquipoLocalTorneoEquipoID INT NOT NULL, -- Relaci�n con equipo local en TorneoEquipo
    EquipoVisitanteTorneoEquipoID INT NOT NULL, -- Relaci�n con equipo visitante en TorneoEquipo
    GolesLocal INT NULL, -- Goles anotados por el equipo local
    GolesVisitante INT NULL, -- Goles anotados por el equipo visitante
    NroFecha INT NOT NULL, -- N�mero de la fecha en el torneo
    AñoParticipacion SMALLINT NOT NULL, -- A�o del torneo
    Fase NVARCHAR(50) NULL, -- Fase del torneo (e.g., Grupos, Semifinal, Final)
    Grupo NVARCHAR(10) NULL, -- Grupo del torneo (e.g., A, B, C)
    Estado NVARCHAR(20) NOT NULL DEFAULT 'Pendiente', -- Pendiente, Jugado, Suspendido
    FOREIGN KEY (TorneoID) REFERENCES Torneo(TorneoID), -- Relaci�n con torneo
    FOREIGN KEY (EquipoLocalTorneoEquipoID) REFERENCES TorneoEquipo(TorneoEquipoID), -- Relaci�n con equipo local
    FOREIGN KEY (EquipoVisitanteTorneoEquipoID) REFERENCES TorneoEquipo(TorneoEquipoID), -- Relaci�n con equipo visitante
);

CREATE TABLE TablaPosiciones (
    TablaPosicionesID INT IDENTITY(1,1) PRIMARY KEY,
    TorneoID INT NOT NULL, -- Relaci�n con el torneo
    AñoParticipacion SMALLINT NOT NULL, -- A�o del torneo
    EquipoID INT NOT NULL, -- Equipo al que pertenece el registro
    PJ INT DEFAULT 0 NOT NULL, -- Partidos Jugados
    PG INT DEFAULT 0 NOT NULL, -- Partidos Ganados
    PE INT DEFAULT 0 NOT NULL, -- Partidos Empatados
    PP INT DEFAULT 0 NOT NULL, -- Partidos Perdidos
    GF INT DEFAULT 0 NOT NULL, -- Goles a Favor
    GC INT DEFAULT 0 NOT NULL, -- Goles en Contra
    DG INT DEFAULT 0 NOT NULL, -- Diferencia de Goles (GF - GC)
    PTS INT DEFAULT 0 NOT NULL, -- Puntos Totales
    Fase NVARCHAR(50) NULL, -- Fase del torneo
    Grupo NVARCHAR(50) NULL, -- Grupo en caso de torneos por grupos
    FOREIGN KEY (TorneoID) REFERENCES Torneo(TorneoID),
    FOREIGN KEY (EquipoID) REFERENCES Equipo(EquipoID),
    CONSTRAINT UQ_Torneo_Equipo_Año UNIQUE (TorneoID, AñoParticipacion, EquipoID, Fase, Grupo) -- Evita duplicados por torneo, equipo y a�o
);


CREATE TABLE LogELO (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    PartidoID INT,
    EquipoID INT,
    ELOAnterior FLOAT,
    ELONuevo FLOAT,
    Fecha DATETIME DEFAULT GETDATE()
);

