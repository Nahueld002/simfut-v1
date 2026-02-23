USE FutbolDB2
GO
--==========================================================
--STORED PROCEDURE PARA ACTUALIZAR LA TABLA DE POSICIONES
--==========================================================
CREATE OR ALTER PROCEDURE ActualizarTablaPosiciones
AS
BEGIN
    SET NOCOUNT ON;

    -- Eliminar registros previos para recalcular la tabla de posiciones
    DELETE FROM TablaPosiciones WHERE TorneoID IN (SELECT DISTINCT TorneoID FROM Partido WHERE Estado = 'Finalizado');

    -- Insertar registros con los resultados actualizados
    INSERT INTO TablaPosiciones (TorneoID, AñoParticipacion, EquipoID, PJ, PG, PE, PP, GF, GC, DG, PTS, Fase, Grupo)
    SELECT 
        t.TorneoID,
        p.AñoParticipacion,
        e.EquipoID,
        COUNT(p.PartidoID) AS PJ,
        COUNT(CASE 
            WHEN p.GolesLocal > p.GolesVisitante AND p.EquipoLocalTorneoEquipoID = te.TorneoEquipoID THEN 1 
            WHEN p.GolesVisitante > p.GolesLocal AND p.EquipoVisitanteTorneoEquipoID = te.TorneoEquipoID THEN 1 
        END) AS PG,
        COUNT(CASE 
            WHEN p.GolesLocal = p.GolesVisitante THEN 1 
        END) AS PE,
        COUNT(CASE 
            WHEN p.GolesLocal < p.GolesVisitante AND p.EquipoLocalTorneoEquipoID = te.TorneoEquipoID THEN 1 
            WHEN p.GolesVisitante < p.GolesLocal AND p.EquipoVisitanteTorneoEquipoID = te.TorneoEquipoID THEN 1 
        END) AS PP,
        SUM(CASE 
            WHEN p.EquipoLocalTorneoEquipoID = te.TorneoEquipoID THEN COALESCE(p.GolesLocal, 0) 
            WHEN p.EquipoVisitanteTorneoEquipoID = te.TorneoEquipoID THEN COALESCE(p.GolesVisitante, 0) 
        END) AS GF,
        SUM(CASE 
            WHEN p.EquipoLocalTorneoEquipoID = te.TorneoEquipoID THEN COALESCE(p.GolesVisitante, 0) 
            WHEN p.EquipoVisitanteTorneoEquipoID = te.TorneoEquipoID THEN COALESCE(p.GolesLocal, 0) 
        END) AS GC,
        SUM(CASE 
            WHEN p.EquipoLocalTorneoEquipoID = te.TorneoEquipoID THEN COALESCE(p.GolesLocal, 0) - COALESCE(p.GolesVisitante, 0) 
            WHEN p.EquipoVisitanteTorneoEquipoID = te.TorneoEquipoID THEN COALESCE(p.GolesVisitante, 0) - COALESCE(p.GolesLocal, 0) 
        END) AS DG,
        (3 * COUNT(CASE 
            WHEN p.GolesLocal > p.GolesVisitante AND p.EquipoLocalTorneoEquipoID = te.TorneoEquipoID THEN 1 
            WHEN p.GolesVisitante > p.GolesLocal AND p.EquipoVisitanteTorneoEquipoID = te.TorneoEquipoID THEN 1 
        END) + 
        COUNT(CASE 
            WHEN p.GolesLocal = p.GolesVisitante THEN 1 
        END)) AS PTS,
        p.Fase,
        p.Grupo
    FROM Partido p
    INNER JOIN TorneoEquipo te ON (p.EquipoLocalTorneoEquipoID = te.TorneoEquipoID OR p.EquipoVisitanteTorneoEquipoID = te.TorneoEquipoID) 
    INNER JOIN Equipo e ON te.EquipoID = e.EquipoID  
    INNER JOIN Torneo t ON te.TorneoID = t.TorneoID  
    WHERE p.Estado = 'Finalizado'
    GROUP BY t.TorneoID, p.AñoParticipacion, e.EquipoID, p.Fase, p.Grupo;
END;
GO


------------------------
--STORED PROCEDURE PARA SIMULAR PARTIDOS EN LA WEB APP 
------------------------
USE FutbolDB2
GO
CREATE OR ALTER PROCEDURE spSimularTorneoElo
    @TorneoNombre       NVARCHAR(100),
    @AñoParticipacion SMALLINT
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        ---------------------------------------------------------
        -- DECLARACIÓN DE VARIABLES
        ---------------------------------------------------------
        
        DECLARE 
            @TorneoID INT,
            @PartidoID INT,
            @localTorneoEquipoID INT,
            @visitanteTorneoEquipoID INT,
            @localEquipoID INT,
            @visitanteEquipoID INT,
            @localELO FLOAT,
            @visitanteELO FLOAT,
            @diferenciaELO FLOAT,
            @E_local FLOAT,
            @E_visitante FLOAT,
            @drawChance FLOAT = 0.2,    -- 20% de probabilidad de empate
            @P_win_local FLOAT,
            @P_win_visitante FLOAT,
            @r FLOAT,
            @resultado VARCHAR(10),
            @golesLocal INT,
            @golesVisitante INT,
            @S_local FLOAT,
            @S_visitante FLOAT,
            @newELO_local FLOAT,
            @newELO_visitante FLOAT,
            @K INT = 30,
            @randVal FLOAT,            -- Variable para números aleatorios
            @randVal2 FLOAT,
            @randCandidate FLOAT,    -- Para decidir si se intenta una goleada
            @rGoleada FLOAT,         -- Para evaluar la aceptación de la candidata goleada
            @golesLocalCandidate INT,
            @golesVisitanteCandidate INT,
            @candidateDiff INT,      -- Diferencia de goles en el candidato
            @acceptProb FLOAT,       -- Probabilidad de aceptar la candidata goleada
            @candidateChance FLOAT;  -- Probabilidad de intentar una goleada
                
        --Esto es para obtener el ID del Torneo y poder manejarlo con la TablaPosiciones
        -- Obtener el ID del Torneo
        SELECT @TorneoID = TorneoID FROM Torneo WHERE Nombre = @TorneoNombre;

        IF @TorneoID IS NULL
        BEGIN
            RAISERROR('El torneo especificado no existe.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        PRINT 'Simulación iniciada para el torneo: ' + @TorneoNombre + ', Año: ' + CAST(@AñoParticipacion AS NVARCHAR);

        -- SIMULACIÓN DE PARTIDOS
        DECLARE partido_cursor CURSOR LOCAL FAST_FORWARD FOR
        SELECT 
            p.PartidoID, 
            p.EquipoLocalTorneoEquipoID, 
            p.EquipoVisitanteTorneoEquipoID,
            tel.EquipoID, 
            tev.EquipoID
        FROM Partido p
        INNER JOIN TorneoEquipo tel ON p.EquipoLocalTorneoEquipoID = tel.TorneoEquipoID
        INNER JOIN TorneoEquipo tev ON p.EquipoVisitanteTorneoEquipoID = tev.TorneoEquipoID
        WHERE 
            p.TorneoID = @TorneoID
            AND p.AñoParticipacion = @AñoParticipacion
            AND p.Estado = 'Pendiente'
        ORDER BY p.NroFecha;

        OPEN partido_cursor;
        FETCH NEXT FROM partido_cursor 
        INTO @PartidoID, @localTorneoEquipoID, @visitanteTorneoEquipoID, @localEquipoID, @visitanteEquipoID;        
        WHILE @@FETCH_STATUS = 0
        BEGIN
            -- Obtener los ELO actuales de cada equipo
            -- Si el equipo no tiene ELO asignado, se le da un valor por defecto
            SELECT @localELO = COALESCE(ELO, 1000) FROM Equipo WHERE EquipoID = @localEquipoID;
            SELECT @visitanteELO = COALESCE(ELO, 1000) FROM Equipo WHERE EquipoID = @visitanteEquipoID;

            
            -- Cálculo de la diferencia de ELO y probabilidades esperadas
            SET @diferenciaELO = ABS(@localELO - @visitanteELO);
            SET @E_local = 1.0 / (1.0 + POWER(10.0, ((@visitanteELO - @localELO) / 400.0)));
            SET @E_visitante = 1.0 - @E_local;
            
            -- Ajuste de probabilidades considerando empate
            SET @P_win_local       = (1.0 - @drawChance) * @E_local;
            SET @P_win_visitante = (1.0 - @drawChance) * @E_visitante;
            
            -- Determinar el resultado: 'local', 'draw' o 'visitante'
            SET @r = CAST(ABS(CHECKSUM(NEWID())) % 10000 AS FLOAT) / 10000.0;
            IF @r < @P_win_local
                SET @resultado = 'local';
            ELSE IF @r < (@P_win_local + @drawChance)
                SET @resultado = 'draw';
            ELSE
                SET @resultado = 'visitante';
            
            -- Simulación de goles según el resultado obtenido
            IF @resultado = 'local'
            BEGIN
                IF @diferenciaELO >= 400 
                    SET @candidateChance = 0.05;    -- 5% de probabilidad de intentar una goleada
                ELSE
                    SET @candidateChance = 0.0;
                
                SET @randCandidate = CAST(ABS(CHECKSUM(NEWID())) % 10000 AS FLOAT) / 10000.0;
                IF @randCandidate < @candidateChance
                BEGIN
                    -- Intentar candidata goleada
                    SET @randCandidate = CAST(ABS(CHECKSUM(NEWID())) % 100 AS FLOAT) / 100.0;
                    IF @randCandidate < 0.8
                        SET @golesLocalCandidate = 5 + CAST(ABS(CHECKSUM(NEWID())) % 4 AS INT);    -- 5 a 8 goles
                    ELSE
                        SET @golesLocalCandidate = 9 + CAST(ABS(CHECKSUM(NEWID())) % 7 AS INT);    -- 9 a 15 goles
                    
                    SET @randVal2 = CAST(ABS(CHECKSUM(NEWID())) % 100 AS FLOAT) / 100.0;
                    IF @randVal2 < 0.90 
                        SET @golesVisitanteCandidate = 0;
                    ELSE 
                        SET @golesVisitanteCandidate = 1;
                    
                    SET @candidateDiff = @golesLocalCandidate - @golesVisitanteCandidate;
                    SET @acceptProb = 0.005;    -- Probabilidad base para aceptar la candidata
                    IF @candidateDiff > 5
                        SET @acceptProb = @acceptProb / (@candidateDiff - 5 + 1);
                    
                    SET @rGoleada = CAST(ABS(CHECKSUM(NEWID())) % 10000 AS FLOAT) / 10000.0;
                    IF @rGoleada < @acceptProb
                    BEGIN
                        SET @golesLocal = @golesLocalCandidate;
                        SET @golesVisitante = @golesVisitanteCandidate;
                    END
                    ELSE
                    BEGIN
                        -- Simulación normal
                        SET @randVal = CAST(ABS(CHECKSUM(NEWID())) % 100 AS FLOAT) / 100.0;
                        IF @diferenciaELO < 50
                        BEGIN
                            IF @randVal < 0.30 SET @golesLocal = 1;
                            ELSE IF @randVal < 0.80 SET @golesLocal = 2;
                            ELSE IF @randVal < 0.95 SET @golesLocal = 3;
                            ELSE SET @golesLocal = 4;
                        END
                        ELSE
                        BEGIN
                            IF @randVal < 0.20 SET @golesLocal = 1;
                            ELSE IF @randVal < 0.50 SET @golesLocal = 2;
                            ELSE IF @randVal < 0.85 SET @golesLocal = 3;
                            ELSE IF @randVal < 0.97 SET @golesLocal = 4;
                            ELSE SET @golesLocal = 5;
                        END;
                        
                        SET @randVal2 = CAST(ABS(CHECKSUM(NEWID())) % 100 AS FLOAT) / 100.0;
                        IF @randVal2 < 0.70 SET @golesVisitante = 0;
                        ELSE IF @randVal2 < 0.90 SET @golesVisitante = 1;
                        ELSE SET @golesVisitante = 2;
                    END
                END
                ELSE
                BEGIN
                    -- Simulación normal para victoria local sin candidata goleada
                    SET @randVal = CAST(ABS(CHECKSUM(NEWID())) % 100 AS FLOAT) / 100.0;
                    IF @diferenciaELO < 50
                    BEGIN
                        IF @randVal < 0.30 SET @golesLocal = 1;
                        ELSE IF @randVal < 0.80 SET @golesLocal = 2;
                        ELSE IF @randVal < 0.95 SET @golesLocal = 3;
                        ELSE SET @golesLocal = 4;
                    END
                    ELSE
                    BEGIN
                        IF @randVal < 0.20 SET @golesLocal = 1;
                        ELSE IF @randVal < 0.50 SET @golesLocal = 2;
                        ELSE IF @randVal < 0.85 SET @golesLocal = 3;
                        ELSE IF @randVal < 0.97 SET @golesLocal = 4;
                        ELSE SET @golesLocal = 5;
                    END;
                    
                    SET @randVal2 = CAST(ABS(CHECKSUM(NEWID())) % 100 AS FLOAT) / 100.0;
                    IF @randVal2 < 0.70 SET @golesVisitante = 0;
                    ELSE IF @randVal2 < 0.90 SET @golesVisitante = 1;
                    ELSE SET @golesVisitante = 2;
                END
            END
            ELSE IF @resultado = 'visitante'
            BEGIN
                -- Rama para victoria visitante (lógica similar a la de local)
                IF @diferenciaELO >= 400 
                    SET @candidateChance = 0.05;
                ELSE
                    SET @candidateChance = 0.0;
                
                SET @randCandidate = CAST(ABS(CHECKSUM(NEWID())) % 10000 AS FLOAT) / 10000.0;
                IF @randCandidate < @candidateChance
                BEGIN
                    SET @randCandidate = CAST(ABS(CHECKSUM(NEWID())) % 100 AS FLOAT) / 100.0;
                    IF @randCandidate < 0.8
                        SET @golesVisitanteCandidate = 5 + CAST(ABS(CHECKSUM(NEWID())) % 4 AS INT);    -- 5 a 8 goles
                    ELSE
                        SET @golesVisitanteCandidate = 9 + CAST(ABS(CHECKSUM(NEWID())) % 7 AS INT);    -- 9 a 15 goles
                    
                    SET @randVal2 = CAST(ABS(CHECKSUM(NEWID())) % 100 AS FLOAT) / 100.0;
                    IF @randVal2 < 0.90 
                        SET @golesLocalCandidate = 0;
                    ELSE 
                        SET @golesLocalCandidate = 1;
                    
                    SET @candidateDiff = @golesVisitanteCandidate - @golesLocalCandidate;
                    SET @acceptProb = 0.005;
                    IF @candidateDiff > 5
                        SET @acceptProb = @acceptProb / (@candidateDiff - 5 + 1);
                    
                    SET @rGoleada = CAST(ABS(CHECKSUM(NEWID())) % 10000 AS FLOAT) / 10000.0;
                    IF @rGoleada < @acceptProb
                    BEGIN
                        SET @golesVisitante = @golesVisitanteCandidate;
                        SET @golesLocal = @golesLocalCandidate;
                    END
                    ELSE
                    BEGIN
                        -- Simulación normal para victoria visitante
                        SET @randVal = CAST(ABS(CHECKSUM(NEWID())) % 100 AS FLOAT) / 100.0;
                        IF @diferenciaELO < 50
                        BEGIN
                            IF @randVal < 0.30 SET @golesVisitante = 1;
                            ELSE IF @randVal < 0.80 SET @golesVisitante = 2;
                            ELSE IF @randVal < 0.95 SET @golesVisitante = 3;
                            ELSE SET @golesVisitante = 4;
                        END
                        ELSE
                        BEGIN
                            IF @randVal < 0.20 SET @golesVisitante = 1;
                            ELSE IF @randVal < 0.50 SET @golesVisitante = 2;
                            ELSE IF @randVal < 0.85 SET @golesVisitante = 3;
                            ELSE IF @randVal < 0.97 SET @golesVisitante = 4;
                            ELSE SET @golesVisitante = 5;
                        END;
                        
                        SET @randVal2 = CAST(ABS(CHECKSUM(NEWID())) % 100 AS FLOAT) / 100.0;
                        IF @randVal2 < 0.70 SET @golesLocal = 0;
                        ELSE IF @randVal2 < 0.90 SET @golesLocal = 1;
                        ELSE SET @golesLocal = 2;
                    END
                END
                ELSE
                BEGIN
                    -- Simulación normal para victoria visitante sin candidata goleada
                    SET @randVal = CAST(ABS(CHECKSUM(NEWID())) % 100 AS FLOAT) / 100.0;
                    IF @diferenciaELO < 50
                    BEGIN
                        IF @randVal < 0.30 SET @golesVisitante = 1;
                        ELSE IF @randVal < 0.80 SET @golesVisitante = 2;
                        ELSE IF @randVal < 0.95 SET @golesVisitante = 3;
                        ELSE SET @golesVisitante = 4;
                    END
                    ELSE
                    BEGIN
                        IF @randVal < 0.20 SET @golesVisitante = 1;
                        ELSE IF @randVal < 0.50 SET @golesVisitante = 2;
                        ELSE IF @randVal < 0.85 SET @golesVisitante = 3;
                        ELSE IF @randVal < 0.97 SET @golesVisitante = 4;
                        ELSE SET @golesVisitante = 5;
                    END;
                    
                    SET @randVal2 = CAST(ABS(CHECKSUM(NEWID())) % 100 AS FLOAT) / 100.0;
                    IF @randVal2 < 0.70 SET @golesLocal = 0;
                    ELSE IF @randVal2 < 0.90 SET @golesLocal = 1;
                    ELSE SET @golesLocal = 2;
                END
            END
            ELSE
            BEGIN
                -- Rama de empate: se simula un marcador bajo, con posibilidad de empate goleado
                SET @randVal = CAST(ABS(CHECKSUM(NEWID())) % 100 AS FLOAT) / 100.0;
                IF @randVal < 0.95
                BEGIN
                    IF @randVal < 0.50 SET @golesLocal = 0;
                    ELSE IF @randVal < 0.85 SET @golesLocal = 1;
                    ELSE SET @golesLocal = 2;
                END
                ELSE
                BEGIN
                    SET @golesLocal = 3 + CAST(ABS(CHECKSUM(NEWID())) % 3 AS INT);    -- 3, 4 o 5 goles
                END;
                SET @golesVisitante = @golesLocal;
            END
            
            -- Actualizar el partido
            UPDATE Partido
            SET 
                GolesLocal = COALESCE(@golesLocal, 0),
                GolesVisitante = COALESCE(@golesVisitante, 0),
                Estado = 'Finalizado'
            WHERE PartidoID = @PartidoID;

            
            -- Definir el resultado para el cálculo ELO
            IF @resultado IS NULL 
            BEGIN
                SET @resultado = 'draw';    -- En caso de error, lo tratamos como empate
            END

            IF @resultado = 'local'
            BEGIN
                SET @S_local = 1.0;
                SET @S_visitante = 0.0;
            END
            ELSE IF @resultado = 'visitante'
            BEGIN
                SET @S_local = 0.0;
                SET @S_visitante = 1.0;
            END
            ELSE
            BEGIN
                SET @S_local = 0.5;
                SET @S_visitante = 0.5;
            END

            
            -- Calcular y actualizar el nuevo ELO de cada equipo
            SET @newELO_local       = @localELO + @K * (@S_local - @E_local);
            SET @newELO_visitante = @visitanteELO + @K * (@S_visitante - @E_visitante);
            
            UPDATE Equipo SET ELO = @newELO_local WHERE EquipoID = @localEquipoID;
            UPDATE Equipo SET ELO = @newELO_visitante WHERE EquipoID = @visitanteEquipoID;
            
            -- Guardar logs de cambios de ELO
            INSERT INTO LogELO (PartidoID, EquipoID, ELOAnterior, ELONuevo)
            VALUES (@PartidoID, @localEquipoID, @localELO, @newELO_local);
            
            INSERT INTO LogELO (PartidoID, EquipoID, ELOAnterior, ELONuevo)
            VALUES (@PartidoID, @visitanteEquipoID, @visitanteELO, @newELO_visitante);
            
            FETCH NEXT FROM partido_cursor 
                INTO @PartidoID, @localTorneoEquipoID, @visitanteTorneoEquipoID, @localEquipoID, @visitanteEquipoID;
        END
        
        CLOSE partido_cursor;
        DEALLOCATE partido_cursor;

        PRINT 'Simulación completada. Actualizando la Tabla de Posiciones...';

        -- ACTUALIZAR TABLA DE POSICIONES
        EXEC ActualizarTablaPosiciones;

        ---------------------------------------------------------
        -- VERIFICAR SI TODOS LOS PARTIDOS HAN FINALIZADO PARA EL TORNEO Y AÑO
        ---------------------------------------------------------
        IF NOT EXISTS (
            SELECT 1 FROM Partido 
            WHERE TorneoID = @TorneoID AND AñoParticipacion = @AñoParticipacion
            AND Estado = 'Pendiente'
        )
        BEGIN
            PRINT 'Todos los partidos del torneo han finalizado. Calculando clasificaciones...';

            DECLARE @Campeon INT, @Subcampeon INT;
            
            WITH RankedTeams AS (
                SELECT 
                    EquipoID,
                    ROW_NUMBER() OVER (ORDER BY COALESCE(PTS, 0) DESC, COALESCE(DG, 0) DESC, COALESCE(GF, 0) DESC) AS Posicion
                FROM TablaPosiciones
                WHERE TorneoID = @TorneoID AND AñoParticipacion = @AñoParticipacion
            )
            SELECT 
                @Campeon = MAX(CASE WHEN Posicion = 1 THEN EquipoID END),
                @Subcampeon = MAX(CASE WHEN Posicion = 2 THEN EquipoID END)
            FROM RankedTeams;

            -- Insertar resultados
            INSERT INTO TorneoResultados (TorneoID, AñoTorneo, CampeonEquipoID, SubcampeonEquipoID, Observaciones, Era)
            VALUES (@TorneoID, @AñoParticipacion, @Campeon, @Subcampeon, 'Resultados generados por simulación Elo', 'Era Profesional');

            -- Insertar el título en Palmares
            INSERT INTO Palmares (AñoTitulo, EquipoID, TorneoID)
            VALUES (@AñoParticipacion, @Campeon, @TorneoID);

            PRINT 'Campeón y subcampeón guardados exitosamente';
        END
        ELSE
        BEGIN
            PRINT 'Faltan partidos por jugar en el torneo, no se calcularán clasificaciones aún.';
        END

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR(@ErrorMessage, 16, 1);
    END CATCH
END;
GO