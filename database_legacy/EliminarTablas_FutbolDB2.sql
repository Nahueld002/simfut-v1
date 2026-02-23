USE FutbolDB2
GO



-- 1. Eliminar datos en orden correcto

DELETE FROM LogELO;
DBCC CHECKIDENT ('LogELO', RESEED, 0);

DELETE FROM TablaPosiciones;
DBCC CHECKIDENT ('TablaPosiciones', RESEED, 0);

DELETE FROM Partido;
DBCC CHECKIDENT ('Partido', RESEED, 0);

DELETE FROM Palmares;
DBCC CHECKIDENT ('Palmares', RESEED, 0);

DELETE FROM TorneoAscenso;
DBCC CHECKIDENT ('TorneoAscenso', RESEED, 0);

DELETE FROM TorneoDescensos;
DBCC CHECKIDENT ('TorneoDescensos', RESEED, 0);

DELETE FROM TorneoResultados;
DBCC CHECKIDENT ('TorneoResultados', RESEED, 0);

DELETE FROM TorneoEquipo;
DBCC CHECKIDENT ('TorneoEquipo', RESEED, 0);

DELETE FROM Equipo;
DBCC CHECKIDENT ('Equipo', RESEED, 0);

DELETE FROM TorneoPais;
DBCC CHECKIDENT ('TorneoPais', RESEED, 0);

DELETE FROM Torneo;
DBCC CHECKIDENT ('Torneo', RESEED, 0);

DELETE FROM Ciudad;
DBCC CHECKIDENT ('Ciudad', RESEED, 0);

DELETE FROM Region;
DBCC CHECKIDENT ('Region', RESEED, 0);

DELETE FROM Pais;
DBCC CHECKIDENT ('Pais', RESEED, 0);

DELETE FROM Confederacion;
DBCC CHECKIDENT ('Confederacion', RESEED, 0);

-- 2. Eliminar las tablas
DROP TABLE LogELO;
DROP TABLE TablaPosiciones;
DROP TABLE Partido;
DROP TABLE Palmares;
DROP TABLE TorneoAscenso;
DROP TABLE TorneoDescensos;
DROP TABLE TorneoResultados;
DROP TABLE TorneoEquipo;
DROP TABLE Equipo;
DROP TABLE TorneoPais;
DROP TABLE Torneo;
DROP TABLE Ciudad;
DROP TABLE Region;
DROP TABLE Pais;
DROP TABLE Confederacion;


