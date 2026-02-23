import argparse
import random
import os
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
import psycopg2
from psycopg2.extras import execute_values


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

db_path = os.path.join(BACKEND_DIR, "db.py")
if not os.path.exists(db_path):
    raise FileNotFoundError(f"No se encontró db.py en: {db_path}")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from db import get_db_connection


TORNEO_FORMATOS = {
    # 2, 3: 12 equipos, 2 ruedas
    2: {"mode": "liga", "rounds": 2},
    3: {"mode": "liga", "rounds": 2},
    # 4: 16 equipos, 2 ruedas
    4: {"mode": "liga", "rounds": 2},
    # 5: 18 equipos, 2 ruedas
    5: {"mode": "liga", "rounds": 2},
    # 6: 2 grupos de 7, 2 ruedas + semis ida/vuelta + final única
    6: {"mode": "grupos_playoff", "group_rounds": 2, "groups": 2},
    # 7: 12 equipos, 3 ruedas
    7: {"mode": "liga", "rounds": 3},
}



@dataclass(frozen=True)
class Match:
    local_te_id: int
    visita_te_id: int
    nrofecha: int
    fase: Optional[str]
    grupo: Optional[str]


def round_robin_circle_one_round(team_ids: List[int], seed: Optional[int] = None) -> List[Tuple[int, int, int]]:
    if len(team_ids) < 2:
        raise ValueError("Se requieren al menos 2 participantes para generar liga.")

    ids = list(team_ids)
    if seed is not None:
        rng = random.Random(seed)
        rng.shuffle(ids)

    bye = None
    if len(ids) % 2 == 1:
        ids.append(bye)

    n = len(ids)
    rounds = n - 1
    half = n // 2

    current = ids[:]
    fixtures: List[Tuple[int, int, int]] = []

    for r in range(1, rounds + 1):
        left = current[:half]
        right = list(reversed(current[half:]))

        for i in range(half):
            a = left[i]
            b = right[i]
            if a is None or b is None:
                continue

            if (r + i) % 2 == 0:
                local, visita = a, b
            else:
                local, visita = b, a

            fixtures.append((local, visita, r))

        fixed = current[0]
        rest = current[1:]
        rest = [rest[-1]] + rest[:-1]
        current = [fixed] + rest

    return fixtures


def round_robin_multi_rounds(team_ids: List[int], rounds_count: int, seed: Optional[int] = None) -> List[Tuple[int, int, int]]:
    if rounds_count < 1:
        raise ValueError("rounds_count debe ser >= 1")

    base = round_robin_circle_one_round(team_ids, seed=seed)
    one_round_len = max(f[2] for f in base)

    all_fx: List[Tuple[int, int, int]] = []
    for r in range(1, rounds_count + 1):
        offset = (r - 1) * one_round_len
        invert = (r % 2 == 0)
        for (local, visita, nro) in base:
            if invert:
                all_fx.append((visita, local, nro + offset))
            else:
                all_fx.append((local, visita, nro + offset))

    return all_fx



def fetch_torneo(conn, torneoid: int) -> Dict:
    with conn.cursor() as cur:
        cur.execute("SELECT torneoid, nombre, tipotorneo, categoria, estado FROM torneo WHERE torneoid=%s", (torneoid,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"No existe torneo con torneoid={torneoid}.")
        cols = [d.name for d in cur.description]
        return dict(zip(cols, row))


def fetch_participantes_raw(conn, torneoid: int, anio: int) -> List[Dict]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT torneoequipoid, fase, grupo, equipoid "
            "FROM torneoequipo "
            "WHERE torneoid=%s AND anioparticipacion=%s "
            "ORDER BY fase NULLS FIRST, grupo NULLS FIRST, torneoequipoid",
            (torneoid, anio),
        )
        rows = cur.fetchall()
        cols = [d.name for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]


def reset_tournament_data(conn, torneoid: int, anio: int) -> int:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT DISTINCT ON (l.equipoid) l.equipoid, l.eloanterior
            FROM logelo l
            JOIN partido p ON l.partidoid = p.partidoid
            WHERE p.torneoid = %s AND p.anioparticipacion = %s
            ORDER BY l.equipoid, l.logid ASC
        """, (torneoid, anio))
        rollbacks = cur.fetchall()
        
        reverted_count = 0
        for r in rollbacks:
            cur.execute("UPDATE equipo SET elo = %s WHERE equipoid = %s", (r[1], r[0]))
            reverted_count += 1
        
        if reverted_count > 0:
            print(f"   -> ELO revertido para {reverted_count} equipos a su estado original.")

        cur.execute("""
            DELETE FROM logelo 
            WHERE partidoid IN (SELECT partidoid FROM partido WHERE torneoid=%s AND anioparticipacion=%s)
        """, (torneoid, anio))

        cur.execute("DELETE FROM tablaposiciones WHERE torneoid=%s AND anioparticipacion=%s", (torneoid, anio))

        cur.execute("DELETE FROM torneoresultados WHERE torneoid=%s AND aniotorneo=%s", (torneoid, anio))
        cur.execute("DELETE FROM palmares WHERE torneoid=%s AND aniotitulo=%s", (torneoid, anio))

        cur.execute("DELETE FROM partido WHERE torneoid=%s AND anioparticipacion=%s", (torneoid, anio))
        
        return cur.rowcount


def insert_partidos(conn, torneoid: int, anio: int, matches: List[Match]) -> int:
    if not matches:
        return 0

    values = [
        (
            torneoid,
            m.local_te_id,
            m.visita_te_id,
            None,  
            None,  
            m.nrofecha,
            anio,
            m.fase,
            m.grupo,
            "Pendiente",
        )
        for m in matches
    ]

    sql = """
    INSERT INTO partido (
        torneoid,
        equipolocaltorneoequipoid,
        equipovisitantetorneoequipoid,
        goleslocal,
        golesvisitante,
        nrofecha,
        anioparticipacion,
        fase,
        grupo,
        estado
    ) VALUES %s
    """

    with conn.cursor() as cur:
        execute_values(cur, sql, values, page_size=1000)

    return len(matches)


def standings_top2_by_group(conn, torneoid: int, anio: int) -> Dict[str, List[int]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                COALESCE(tp.grupo, te.grupo) AS grp,
                te.torneoequipoid,
                tp.pts, tp.dg, tp.gf
            FROM tablaposiciones tp
            JOIN torneoequipo te
              ON te.torneoid = tp.torneoid
             AND te.anioparticipacion = tp.anioparticipacion
             AND te.equipoid = tp.equipoid
            WHERE tp.torneoid=%s AND tp.anioparticipacion=%s
            ORDER BY grp, tp.pts DESC, tp.dg DESC, tp.gf DESC, te.torneoequipoid
            """,
            (torneoid, anio),
        )
        rows = cur.fetchall()

    out: Dict[str, List[int]] = {}
    for grp, teid, pts, dg, gf in rows:
        if grp is None:
            continue
        g = str(grp)
        out.setdefault(g, [])
        if len(out[g]) < 2:
            out[g].append(int(teid))
    out = {g: ids for g, ids in out.items() if len(ids) == 2}
    return out


def build_liga_matches(participantes: List[int], rounds_count: int, fase: Optional[str], grupo: Optional[str], seed: Optional[int]) -> List[Match]:
    rr = round_robin_multi_rounds(participantes, rounds_count=rounds_count, seed=seed)
    return [Match(local, visita, nrofecha, fase, grupo) for (local, visita, nrofecha) in rr]


def split_into_groups(team_ids: List[int], groups: int) -> Dict[str, List[int]]:
    if groups <= 1:
        return {"A": list(team_ids)}

    if len(team_ids) % groups != 0:
        raise ValueError(f"No se puede dividir {len(team_ids)} equipos en {groups} grupos iguales.")

    size = len(team_ids) // groups
    group_names = [chr(ord("A") + i) for i in range(groups)]
    out: Dict[str, List[int]] = {}
    for i, g in enumerate(group_names):
        out[g] = team_ids[i * size : (i + 1) * size]
    return out


def build_torneo6_matches(conn, torneoid: int, anio: int, participantes_rows: List[Dict], seed: Optional[int], generar_playoffs: bool, finalistas: Optional[List[int]]) -> List[Match]:
    fmt = TORNEO_FORMATOS[6]
    group_rounds = fmt["group_rounds"]
    groups_count = fmt["groups"]

    with_group = [r for r in participantes_rows if r.get("grupo") is not None]
    group_map: Dict[str, List[int]] = {}

    if with_group:
        for r in with_group:
            g = str(r["grupo"])
            group_map.setdefault(g, []).append(int(r["torneoequipoid"]))
    else:
        ids = [int(r["torneoequipoid"]) for r in participantes_rows]
        group_map = split_into_groups(ids, groups_count)

    all_matches: List[Match] = []
    max_group_fecha = 0
    for grp, ids in group_map.items():
        gm = build_liga_matches(ids, rounds_count=group_rounds, fase="Grupos", grupo=grp, seed=seed)
        all_matches.extend(gm)
        if gm:
            max_group_fecha = max(max_group_fecha, max(m.nrofecha for m in gm))

    if generar_playoffs:
        top2 = standings_top2_by_group(conn, torneoid, anio)
        if ("A" in top2) and ("B" in top2):
            a1, a2 = top2["A"][0], top2["A"][1]
            b1, b2 = top2["B"][0], top2["B"][1]

            semis = [
                Match(local_te_id=b2, visita_te_id=a1, nrofecha=max_group_fecha + 1, fase="Semifinal", grupo=None),
                Match(local_te_id=a1, visita_te_id=b2, nrofecha=max_group_fecha + 2, fase="Semifinal", grupo=None),
                Match(local_te_id=a2, visita_te_id=b1, nrofecha=max_group_fecha + 1, fase="Semifinal", grupo=None),
                Match(local_te_id=b1, visita_te_id=a2, nrofecha=max_group_fecha + 2, fase="Semifinal", grupo=None),
            ]
            all_matches.extend(semis)
            max_group_fecha = max_group_fecha + 2

    if finalistas and len(finalistas) == 2:
        all_matches.append(
            Match(local_te_id=int(finalistas[0]), visita_te_id=int(finalistas[1]), nrofecha=max_group_fecha + 1, fase="Final", grupo=None)
        )

    return all_matches


def main():
    parser = argparse.ArgumentParser(
        description="Generador de fixture (partido) basado en torneoequipo y formatos por torneoid.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--torneo", type=int, required=True, help="torneoid")
    parser.add_argument("--anio", type=int, required=True, help="anioparticipacion")
    parser.add_argument("--seed", type=int, default=None, help="Semilla para shuffle reproducible")
    parser.add_argument("--replace", action="store_true", help="Borra todos los partidos y reinicia ELO/Tablas antes de insertar")
    parser.add_argument("--dry-run", action="store_true", help="No inserta; solo muestra resumen")
    parser.add_argument("--playoffs", action="store_true", help="(Solo torneo 6) intenta generar semifinales")
    parser.add_argument("--finalistas", type=int, nargs=2, default=None, help="(Solo torneo 6) dos torneoequipoid para final única")
    args = parser.parse_args()

    conn = get_db_connection()
    try:
        conn.autocommit = False

        torneo = fetch_torneo(conn, args.torneo)

        if args.torneo not in TORNEO_FORMATOS:
            raise ValueError(
                f"Torneoid={args.torneo} no tiene formato definido en el script. "
                f"(Definidos: {sorted(TORNEO_FORMATOS.keys())})"
            )

        participantes_rows = fetch_participantes_raw(conn, args.torneo, args.anio)
        if not participantes_rows:
            raise ValueError(f"No hay participantes en torneoequipo para torneoid={args.torneo}, año={args.anio}.")

        fmt = TORNEO_FORMATOS[args.torneo]
        matches: List[Match] = []

        if fmt["mode"] == "liga":
            ids = [int(r["torneoequipoid"]) for r in participantes_rows]
            matches = build_liga_matches(
                participantes=ids,
                rounds_count=int(fmt["rounds"]),
                fase="Liga",
                grupo=None,
                seed=args.seed,
            )

        elif fmt["mode"] == "grupos_playoff":
            matches = build_torneo6_matches(
                conn=conn,
                torneoid=args.torneo,
                anio=args.anio,
                participantes_rows=participantes_rows,
                seed=args.seed,
                generar_playoffs=bool(args.playoffs),
                finalistas=args.finalistas,
            )

        else:
            raise ValueError(f"Modo no soportado: {fmt['mode']}")

        if args.dry_run:
            print(f"Torneo: {torneo['torneoid']} - {torneo['nombre']} | estado={torneo['estado']}")
            print(f"Año: {args.anio}")
            print(f"Partidos a generar: {len(matches)}")
            print("Ejemplo (hasta 12):")
            for m in matches[:12]:
                print(f"  fecha={m.nrofecha} | fase={m.fase} | grupo={m.grupo} | {m.local_te_id} vs {m.visita_te_id}")
            conn.rollback()
            return

        deleted_matches_count = 0
        if args.replace:
            deleted_matches_count = reset_tournament_data(conn, args.torneo, args.anio)

        inserted = insert_partidos(conn, args.torneo, args.anio, matches)
        conn.commit()

        print(f"OK ✅ Torneo {args.torneo} año {args.anio}: insertados {inserted} partidos.")
        if args.replace:
            print(f"Reemplazo activo: reseteo completo (partidos eliminados: {deleted_matches_count}, ELO revertido, tabla borrada).")

        if args.torneo == 6 and args.playoffs:
            if not any(m.fase == "Semifinal" for m in matches):
                print("Nota: No se generaron semifinales. Necesitás tener tablaposiciones cargada.")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()