USE FutbolDB2;
GO

/*ACTUALMENTE PARA LA SIMULACIÓN DE TORNEOS (LIGA) NO SE NECESITA EL PARÁMETRO DE @FASE
POR LO QUE SE DESCARTA ESTA FORMA DE EJECUCIÓN DEL STORED PROCEDURE POR EL MOMENTO
EN EL FUTURO SE CREARÁN OTROS SCRIPTS PARA LA SIMULACIÓN DE OTRO TIPO DE TORNEOS
--** Para ejecutar el Stored Procedure
--!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
EXEC spSimularTorneoElo
    @TorneoNombre = 'Torneo Clausura',
    @AñoParticipacion = 2025,
	@Fase = 'Primera Ronda';
--!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
--** Para ejecutar el Stored Procedure
--!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
EXEC spSimularTorneoEloB_Nacional
    @TorneoNombre = 'Primera B Nacional',
    @AñoParticipacion = 2025,
	@Fase = 'Fase 1';

--!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!*/

--** Para ejecutar el Stored Procedure (Tipo de Torneo = Liga)
EXEC spSimularTorneoElo
    @TorneoNombre = 'Torneo Clausura',
    @AñoParticipacion = 2025;

/*##################################################################################################################
###################################################################################################################*/
--***************VER TODOS LOS PARTIDOS DE UN TORNEO DE UN AÑO EN ESPECÍFICO*******************
SELECT p.NroFecha, el.Nombre AS ClubLocal, CONCAT_WS(' - ', p.GolesLocal, p.GolesVisitante) AS Resultado, ev.Nombre AS ClubVisitante, t.Nombre AS Torneo, p.AñoParticipacion AS Año, p.Fase, p.Grupo,p.Estado FROM Partido p
INNER JOIN TorneoEquipo tel ON p.EquipoLocalTorneoEquipoID = tel.TorneoEquipoID
INNER JOIN Equipo el ON tel.EquipoID = el.EquipoID
INNER JOIN TorneoEquipo tev ON p.EquipoVisitanteTorneoEquipoID = tev.TorneoEquipoID
INNER JOIN Equipo ev ON tev.EquipoID = ev.EquipoID
INNER JOIN Torneo t ON p.TorneoID = t.TorneoID
WHERE t.Nombre = 'Torneo Clausura' AND p.AñoParticipacion = 2025
ORDER BY p.NroFecha ASC



/*##################################################################################################################
###################################################################################################################*/
--***************CLUBES QUE PERTENECEN A UN TORNEO EN ESPECÍFICO CON NIVEL DE CADA UNO*******************
SELECT e.Nombre, ROUND(e.ELO,2) AS ELO FROM TorneoEquipo te
INNER JOIN Torneo t ON te.TorneoID = t.TorneoID
INNER JOIN Equipo e ON te.EquipoID = e.EquipoID
WHERE t.Nombre = 'Primera B Nacional' AND te.AñoParticipacion = 2025
ORDER BY e.ELO DESC


/*##################################################################################################################
###################################################################################################################*/
--***************CONSULTA DE TITULOS*******************
--Consultar detalle de cada torneo y sus resultados
SELECT e1.Nombre AS Campeón, e2.Nombre AS Subcampeón, t.Nombre AS Torneo, tr.AñoTorneo FROM TorneoResultados tr
LEFT JOIN Torneo t ON tr.TorneoID = t.TorneoID
LEFT JOIN Equipo e1 ON tr.CampeonEquipoID = e1.EquipoID
LEFT JOIN Equipo e2 ON tr.SubcampeonEquipoID = e2.EquipoID
ORDER BY tr.AñoTorneo
use FutbolDB2
go
--TOTAL DE TÍTULOS
SELECT e.Nombre AS Equipo, COUNT(p.PalmaresID) AS 'Total de Títulos' FROM Palmares p
INNER JOIN Equipo e ON p.EquipoID = e.EquipoID
GROUP BY e.Nombre
ORDER BY 'Total de Títulos' DESC;


--DESGLOSE DE CANTIDAD DE TITULOS POR TITULO
SELECT e.Nombre AS Equipo, t.Nombre AS Torneo, COUNT(p.PalmaresID) AS CantidadTitulos FROM Palmares p
INNER JOIN Equipo e ON p.EquipoID = e.EquipoID
INNER JOIN Torneo t ON p.TorneoID = t.TorneoID
GROUP BY e.Nombre, t.Nombre
ORDER BY CantidadTitulos DESC;


--***************CONSULTA DE SUBTITULOS*******************
SELECT e.Nombre AS Club, COUNT(tr.SubcampeonEquipoID) AS CantidadSubcampeonatos 
FROM TorneoResultados tr
INNER JOIN Equipo e ON tr.SubcampeonEquipoID = e.EquipoID
GROUP BY e.Nombre
ORDER BY CantidadSubcampeonatos DESC;


/*##################################################################################################################
###################################################################################################################*/
--*********************CONSULTAR LOG DE ELO*************************

--CONSULTAR EL HISTORIAL DE LOG POR EQUIPO
SELECT elo.LogID, e.Nombre, elo.ELOAnterior, elo.ELONuevo FROM LogELO elo 
LEFT JOIN Equipo e ON elo.EquipoID = e.EquipoID
WHERE e.Nombre = 'Nacional'
ORDER BY elo.LogID;




--CONSULTAR LA VARIACIÓN DE ELO POR EQUIPO A LO LARGO DEL TIEMPO
WITH EloOriginal AS (
    SELECT elo.EquipoID, elo.ELOAnterior AS ELOOriginal FROM LogELO elo
    WHERE elo.LogID = (SELECT MIN(LogID) FROM LogELO WHERE EquipoID = elo.EquipoID)
),
EloFinal AS (
    SELECT elo.EquipoID, elo.ELONuevo AS ELOFinal FROM LogELO elo
    WHERE elo.LogID = (SELECT MAX(LogID) FROM LogELO WHERE EquipoID = elo.EquipoID)
)
SELECT 
    e.Nombre AS Equipo, ROUND(eo.ELOOriginal,2), ROUND(ef.ELOFinal,2), ROUND((ef.ELOFinal - eo.ELOOriginal),2) AS ELOVariacion
FROM EloOriginal eo
JOIN EloFinal ef ON eo.EquipoID = ef.EquipoID
JOIN Equipo e ON eo.EquipoID = e.EquipoID
WHERE e.Nombre = 'Libertad';


--CONSULTAR LA VARIACIÓN DE ELO POR TORNEO DE UN AÑO EN ESPECIFICO (PERO MUESTRA LA VARIACION A LO LARGO DEL TIEMPO, NO SOLAMENTE DEL TORNEO ESPECIFICADO)
WITH EloOriginal AS (
    SELECT elo.EquipoID, elo.ELOAnterior AS ELOOriginal
    FROM LogELO elo
    WHERE elo.LogID = (SELECT MIN(LogID) FROM LogELO WHERE EquipoID = elo.EquipoID)
),
EloFinal AS (
    SELECT elo.EquipoID, elo.ELONuevo AS ELOFinal
    FROM LogELO elo
    WHERE elo.LogID = (SELECT MAX(LogID) FROM LogELO WHERE EquipoID = elo.EquipoID)
)
SELECT 
    e.Nombre AS Equipo,
    t.Nombre AS Torneo,
    te.AñoParticipacion,
    ROUND(eo.ELOOriginal,2) AS ELOOriginal,
    ROUND(ef.ELOFinal,2) AS ELOFinal,
    ROUND((ef.ELOFinal - eo.ELOOriginal),2) AS ELOVariacion
FROM TorneoEquipo te
INNER JOIN Torneo t ON te.TorneoID = t.TorneoID
INNER JOIN Equipo e ON te.EquipoID = e.EquipoID
LEFT JOIN EloOriginal eo ON te.EquipoID = eo.EquipoID
LEFT JOIN EloFinal ef ON te.EquipoID = ef.EquipoID
WHERE t.Nombre = 'Torneo Apertura' 
AND te.AñoParticipacion = 2025
ORDER BY ELOVariacion DESC;

--==================================================
--VER TABLA DE POSICIONES DE UN TORNEO ESPECÍFICO
--=================================================
SELECT 
    t.Nombre AS Torneo,
    tp.AñoParticipacion,
    e.Nombre AS Equipo,
    SUM(tp.PJ) AS PJ, 
    SUM(tp.PG) AS PG, 
    SUM(tp.PE) AS PE, 
    SUM(tp.PP) AS PP, 
    SUM(tp.GF) AS GF, 
    SUM(tp.GC) AS GC, 
    SUM(tp.DG) AS DG, 
    SUM(tp.PTS) AS PTS
FROM TablaPosiciones tp
INNER JOIN Equipo e ON tp.EquipoID = e.EquipoID
INNER JOIN Torneo t ON tp.TorneoID = t.TorneoID
WHERE 
    t.Nombre = 'Primera B Nacional' 
    AND tp.AñoParticipacion = 2025
GROUP BY t.Nombre, tp.AñoParticipacion, e.Nombre
ORDER BY PTS DESC, DG DESC, GF DESC;
