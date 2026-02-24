import random
import math
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
BACKEND_DIR = os.path.join(PROJECT_ROOT, 'backend')

sys.path.append(BACKEND_DIR)

from db import get_db_connection

class SimuladorFutbol:
    def __init__(self):
        self.K = 30  
        self.conn = None

    def get_connection(self):
        """
        Reutiliza la lógica de conexión de tu archivo db.py
        """
        return get_db_connection()

    def simular_torneo(self, nombre_torneo, anio):
        print(f"⚽ Iniciando simulación para: {nombre_torneo} ({anio})")
        
        try:
            self.conn = self.get_connection()
            if self.conn is None:
                raise Exception("No se pudo establecer conexión con la base de datos.")

            cur = self.conn.cursor()

            cur.execute("SELECT torneoid FROM torneo WHERE nombre = %s", (nombre_torneo,))
            res = cur.fetchone()
            if not res:
                raise Exception("El torneo especificado no existe.")
            torneo_id = res[0]

            sql_pendientes = """
                SELECT 
                    p.partidoid, 
                    p.equipolocaltorneoequipoid, 
                    p.equipovisitantetorneoequipoid,
                    tel.equipoid AS local_id, 
                    tev.equipoid AS visita_id,
                    COALESCE(el.elo, 1000) as elo_local,
                    COALESCE(ev.elo, 1000) as elo_visita
                FROM partido p
                JOIN torneoequipo tel ON p.equipolocaltorneoequipoid = tel.torneoequipoid
                JOIN torneoequipo tev ON p.equipovisitantetorneoequipoid = tev.torneoequipoid
                JOIN equipo el ON tel.equipoid = el.equipoid
                JOIN equipo ev ON tev.equipoid = ev.equipoid
                WHERE p.torneoid = %s AND p.anioparticipacion = %s AND p.estado = 'Pendiente'
                ORDER BY p.nrofecha ASC
            """
            cur.execute(sql_pendientes, (torneo_id, anio))
            partidos = cur.fetchall()

            if not partidos:
                print("No hay partidos pendientes para simular.")
                return

            for p in partidos:
                partido_id, id_te_local, id_te_visita, id_eq_local, id_eq_visita, elo_local, elo_visita = p
                
                e_local = 1.0 / (1.0 + math.pow(10.0, (elo_visita - elo_local) / 400.0))
                
                draw_chance = 0.20
                p_win_local = (1.0 - draw_chance) * e_local

                r = random.random()
                
                resultado = ""
                if r < p_win_local:
                    resultado = "local"
                elif r < (p_win_local + draw_chance):
                    resultado = "draw"
                else:
                    resultado = "visitante"

                goles_local, goles_visita = self._calcular_goles(resultado, elo_local, elo_visita)

                cur.execute("""
                    UPDATE partido 
                    SET goleslocal = %s, golesvisitante = %s, estado = 'Finalizado'
                    WHERE partidoid = %s
                """, (goles_local, goles_visita, partido_id))

                e_visita = 1.0 - e_local
                s_local = 1.0 if resultado == "local" else (0.5 if resultado == "draw" else 0.0)
                s_visita = 1.0 if resultado == "visitante" else (0.5 if resultado == "draw" else 0.0)

                new_elo_local = elo_local + self.K * (s_local - e_local)
                new_elo_visita = elo_visita + self.K * (s_visita - e_visita)

                cur.execute("UPDATE equipo SET elo = %s WHERE equipoid = %s", (new_elo_local, id_eq_local))
                cur.execute("UPDATE equipo SET elo = %s WHERE equipoid = %s", (new_elo_visita, id_eq_visita))
                
                try:
                    cur.execute("""
                        INSERT INTO logelo (partidoid, equipoid, eloanterior, elonuevo) 
                        VALUES (%s, %s, %s, %s), (%s, %s, %s, %s)
                    """, (partido_id, id_eq_local, elo_local, new_elo_local, 
                          partido_id, id_eq_visita, elo_visita, new_elo_visita))
                except Exception:
                    pass

            self._actualizar_tabla_posiciones(cur, torneo_id, anio)

            cur.execute("""
                SELECT COUNT(*) FROM partido 
                WHERE torneoid = %s AND anioparticipacion = %s AND estado = 'Pendiente'
            """, (torneo_id, anio))
            pendientes = cur.fetchone()[0]

            if pendientes == 0:
                print("🏆 Torneo finalizado. Calculando campeón...")
                self._declarar_campeon(cur, torneo_id, anio)

            self.conn.commit()
            print("Simulación completada con éxito.")

        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Error en la simulación: {e}")
            raise e
        finally:
            if self.conn:
                self.conn.close()

    def _calcular_goles(self, resultado, elo_local, elo_visita):
        """ Lógica interna de goles (Idéntica a la anterior) """
        diferencia_elo = abs(elo_local - elo_visita)
        g_local = 0
        g_visita = 0

        candidate_chance = 0.05 if diferencia_elo >= 400 else 0.0
        es_goleada = False

        if random.random() < candidate_chance:
            goles_winner = random.randint(5, 8) if random.random() < 0.8 else random.randint(9, 15)
            goles_loser = 0 if random.random() < 0.9 else 1
            
            diff = goles_winner - goles_loser
            accept_prob = 0.005
            if diff > 5: accept_prob = accept_prob / (diff - 5 + 1)
            
            if random.random() < accept_prob:
                es_goleada = True
                if resultado == "local": g_local, g_visita = goles_winner, goles_loser
                elif resultado == "visitante": g_local, g_visita = goles_loser, goles_winner

        if not es_goleada:
            rand_val = random.random()
            goles_winner = 0
            if diferencia_elo < 50:
                if rand_val < 0.30: goles_winner = 1
                elif rand_val < 0.80: goles_winner = 2
                elif rand_val < 0.95: goles_winner = 3
                else: goles_winner = 4
            else:
                if rand_val < 0.20: goles_winner = 1
                elif rand_val < 0.50: goles_winner = 2
                elif rand_val < 0.85: goles_winner = 3
                elif rand_val < 0.97: goles_winner = 4
                else: goles_winner = 5
            
            rand_val2 = random.random()
            goles_loser = 0 if rand_val2 < 0.70 else (1 if rand_val2 < 0.90 else 2)

            if resultado == "local": g_local, g_visita = goles_winner, goles_loser
            elif resultado == "visitante": g_local, g_visita = goles_loser, goles_winner
            else:
                if random.random() < 0.95:
                    val = 0 if random.random() < 0.5 else 1
                    g_local = g_visita = val
                else:
                    g_local = g_visita = random.randint(2, 4)

        return g_local, g_visita

    def _actualizar_tabla_posiciones(self, cur, torneo_id, anio):
        print("Recalculando Tabla de Posiciones por Grupo...")
        
        cur.execute("DELETE FROM tablaposiciones WHERE torneoid = %s AND anioparticipacion = %s", (torneo_id, anio))

        sql_insert = """
        INSERT INTO tablaposiciones (torneoid, anioparticipacion, equipoid, pj, pg, pe, pp, gf, gc, dg, pts, fase, grupo)
        SELECT 
            t.torneoid,
            p.anioparticipacion,
            e.equipoid,
            COUNT(p.partidoid),
            COUNT(CASE 
                WHEN (p.goleslocal > p.golesvisitante AND p.equipolocaltorneoequipoid = te.torneoequipoid) 
                  OR (p.golesvisitante > p.goleslocal AND p.equipovisitantetorneoequipoid = te.torneoequipoid) THEN 1 
            END),
            COUNT(CASE WHEN p.goleslocal = p.golesvisitante THEN 1 END),
            COUNT(CASE 
                WHEN (p.goleslocal < p.golesvisitante AND p.equipolocaltorneoequipoid = te.torneoequipoid) 
                  OR (p.golesvisitante < p.goleslocal AND p.equipovisitantetorneoequipoid = te.torneoequipoid) THEN 1 
            END),
            SUM(CASE WHEN p.equipolocaltorneoequipoid = te.torneoequipoid THEN p.goleslocal ELSE p.golesvisitante END),
            SUM(CASE WHEN p.equipolocaltorneoequipoid = te.torneoequipoid THEN p.golesvisitante ELSE p.goleslocal END),
            SUM(CASE WHEN p.equipolocaltorneoequipoid = te.torneoequipoid THEN p.goleslocal - p.golesvisitante ELSE p.golesvisitante - p.goleslocal END),
            (3 * COUNT(CASE 
                WHEN (p.goleslocal > p.golesvisitante AND p.equipolocaltorneoequipoid = te.torneoequipoid) 
                  OR (p.golesvisitante > p.goleslocal AND p.equipovisitantetorneoequipoid = te.torneoequipoid) THEN 1 
            END) + 
            COUNT(CASE WHEN p.goleslocal = p.golesvisitante THEN 1 END)),
            p.fase,
            p.grupo
        FROM partido p
        INNER JOIN torneoequipo te ON (p.equipolocaltorneoequipoid = te.torneoequipoid OR p.equipovisitantetorneoequipoid = te.torneoequipoid) 
        INNER JOIN equipo e ON te.equipoid = e.equipoid  
        INNER JOIN torneo t ON te.torneoid = t.torneoid  
        WHERE p.estado = 'Finalizado' AND t.torneoid = %s AND p.anioparticipacion = %s
        GROUP BY t.torneoid, p.anioparticipacion, e.equipoid, p.fase, p.grupo
        """
        cur.execute(sql_insert, (torneo_id, anio))

    def _declarar_campeon(self, cur, torneo_id, anio):
        sql_top = """
            SELECT equipoid FROM tablaposiciones 
            WHERE torneoid = %s AND anioparticipacion = %s
            ORDER BY pts DESC, dg DESC, gf DESC LIMIT 2
        """
        cur.execute(sql_top, (torneo_id, anio))
        top_teams = cur.fetchall()
        
        if len(top_teams) >= 1:
            campeon_id = top_teams[0][0]
            try:
                cur.execute("INSERT INTO palmares (aniotitulo, equipoid, torneoid) VALUES (%s, %s, %s)", 
                            (anio, campeon_id, torneo_id))
            except Exception:
                pass 
    def simular_uno(self, partido_id):
        print(f"⚽ Iniciando simulación individual para Partido ID: {partido_id}")
        
        try:
            self.conn = self.get_connection()
            if self.conn is None: 
                raise Exception("Sin conexión BD")
            
            cur = self.conn.cursor()

            sql_partido = """
                SELECT 
                    p.partidoid, 
                    p.equipolocaltorneoequipoid, 
                    p.equipovisitantetorneoequipoid,
                    tel.equipoid AS local_id, 
                    tev.equipoid AS visita_id,
                    COALESCE(el.elo, 1000) as elo_local,
                    COALESCE(ev.elo, 1000) as elo_visita,
                    p.torneoid,
                    p.anioparticipacion
                FROM partido p
                JOIN torneoequipo tel ON p.equipolocaltorneoequipoid = tel.torneoequipoid
                JOIN torneoequipo tev ON p.equipovisitantetorneoequipoid = tev.torneoequipoid
                JOIN equipo el ON tel.equipoid = el.equipoid
                JOIN equipo ev ON tev.equipoid = ev.equipoid
                WHERE p.partidoid = %s AND p.estado = 'Pendiente'
            """
            cur.execute(sql_partido, (partido_id,))
            match = cur.fetchone()

            if not match:
                return False 

            pid, id_te_local, id_te_visita, id_eq_local, id_eq_visita, elo_local, elo_visita, torneoid, anio = match

            e_local = 1.0 / (1.0 + math.pow(10.0, (elo_visita - elo_local) / 400.0))
            draw_chance = 0.20
            p_win_local = (1.0 - draw_chance) * e_local

            r = random.random()
            resultado = ""
            if r < p_win_local:
                resultado = "local"
            elif r < (p_win_local + draw_chance):
                resultado = "draw"
            else:
                resultado = "visitante"

            g_local, g_visita = self._calcular_goles(resultado, elo_local, elo_visita)

            cur.execute("""
                UPDATE partido 
                SET goleslocal=%s, golesvisitante=%s, estado='Finalizado' 
                WHERE partidoid=%s
            """, (g_local, g_visita, pid))

            e_visita = 1.0 - e_local
            s_local = 1.0 if resultado == "local" else (0.5 if resultado == "draw" else 0.0)
            s_visita = 1.0 if resultado == "visitante" else (0.5 if resultado == "draw" else 0.0)

            new_elo_local = elo_local + self.K * (s_local - e_local)
            new_elo_visita = elo_visita + self.K * (s_visita - e_visita)

            cur.execute("UPDATE equipo SET elo = %s WHERE equipoid = %s", (new_elo_local, id_eq_local))
            cur.execute("UPDATE equipo SET elo = %s WHERE equipoid = %s", (new_elo_visita, id_eq_visita))

            try:
                cur.execute("""
                    INSERT INTO logelo (partidoid, equipoid, eloanterior, elonuevo) 
                    VALUES (%s, %s, %s, %s), (%s, %s, %s, %s)
                """, (pid, id_eq_local, elo_local, new_elo_local, 
                      pid, id_eq_visita, elo_visita, new_elo_visita))
            except Exception:
                pass

            self._actualizar_tabla_posiciones(cur, torneoid, anio)

            cur.execute("""
                SELECT COUNT(*) FROM partido 
                WHERE torneoid = %s AND anioparticipacion = %s AND estado = 'Pendiente'
            """, (torneoid, anio))
            pendientes = cur.fetchone()[0]

            if pendientes == 0:
                print("🏆 Torneo finalizado tras este partido. Calculando campeón...")
                self._declarar_campeon(cur, torneoid, anio)

            self.conn.commit()
            print(f"Partido {pid} simulado exitosamente: {g_local}-{g_visita}")
            return True

        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Error simulando partido {partido_id}: {e}")
            raise e
        finally:
            if self.conn:
                self.conn.close()
    
    def registrar_manual(self, partido_id, goles_local, goles_visita):
        print(f"\n⚡ INTENTO MANUAL: Partido {partido_id} | {goles_local}-{goles_visita}")
        
        try:
            self.conn = self.get_connection()
            if self.conn is None: raise Exception("Sin conexión BD")
            cur = self.conn.cursor()

            sql_partido = """
                SELECT 
                    p.partidoid, 
                    tel.equipoid AS local_id, 
                    tev.equipoid AS visita_id,
                    COALESCE(el.elo, 1000) as elo_local, 
                    COALESCE(ev.elo, 1000) as elo_visita,
                    p.torneoid, 
                    p.anioparticipacion
                FROM partido p
                JOIN torneoequipo tel ON p.equipolocaltorneoequipoid = tel.torneoequipoid
                JOIN torneoequipo tev ON p.equipovisitantetorneoequipoid = tev.torneoequipoid
                JOIN equipo el ON tel.equipoid = el.equipoid
                JOIN equipo ev ON tev.equipoid = ev.equipoid
                WHERE p.partidoid = %s
            """
            cur.execute(sql_partido, (partido_id,))
            match = cur.fetchone()

            if not match: 
                raise Exception(f"No se encontró el partido ID {partido_id}")

            pid, id_eq_local, id_eq_visita, elo_local, elo_visita, torneoid, anio = match
            
            print(f"   -> Datos: LocalID={id_eq_local}, VisitaID={id_eq_visita}, EloL={elo_local}, EloV={elo_visita}")

            cur.execute("""
                UPDATE partido 
                SET goleslocal=%s, golesvisitante=%s, estado='Finalizado' 
                WHERE partidoid=%s
            """, (goles_local, goles_visita, pid))

            if goles_local > goles_visita:
                resultado = "local"
                s_local, s_visita = 1.0, 0.0
            elif goles_visita > goles_local:
                resultado = "visitante"
                s_local, s_visita = 0.0, 1.0
            else:
                resultado = "draw"
                s_local, s_visita = 0.5, 0.5

            elo_local_flt = float(elo_local)
            elo_visita_flt = float(elo_visita)

            e_local = 1.0 / (1.0 + math.pow(10.0, (elo_visita_flt - elo_local_flt) / 400.0))
            e_visita = 1.0 - e_local
            
            new_elo_local = elo_local_flt + self.K * (s_local - e_local)
            new_elo_visita = elo_visita_flt + self.K * (s_visita - e_visita)

            print(f"   -> ELO Calculado: {new_elo_local:.2f} (L) - {new_elo_visita:.2f} (V)")

            cur.execute("UPDATE equipo SET elo = %s WHERE equipoid = %s", (new_elo_local, id_eq_local))
            cur.execute("UPDATE equipo SET elo = %s WHERE equipoid = %s", (new_elo_visita, id_eq_visita))

            print("   -> Intentando insertar en LogELO...")
            cur.execute("""
                INSERT INTO logelo (partidoid, equipoid, eloanterior, elonuevo) 
                VALUES (%s, %s, %s, %s), (%s, %s, %s, %s)
            """, (pid, id_eq_local, elo_local_flt, new_elo_local, 
                  pid, id_eq_visita, elo_visita_flt, new_elo_visita))
            print("   -> Insertado en LogELO OK")

            self._actualizar_tabla_posiciones(cur, torneoid, anio)

            cur.execute("SELECT COUNT(*) FROM partido WHERE torneoid = %s AND anioparticipacion = %s AND estado = 'Pendiente'", (torneoid, anio))
            if cur.fetchone()[0] == 0:
                self._declarar_campeon(cur, torneoid, anio)

            self.conn.commit()
            print("Transacción completada con éxito.")
            return True

        except Exception as e:
            if self.conn: self.conn.rollback()
            print(f"ERROR FATAL EN MANUAL: {e}")
            raise e 
        finally:
            if self.conn: self.conn.close()