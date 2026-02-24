import pandas as pd
import io
import json
from sqlalchemy import text, String, Date, DateTime, Text, Integer
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.dialects.postgresql import JSONB
from app.models import world, team, competition, geo, common, match, narrative
import logging

logger = logging.getLogger(__name__)

# Order matches dependencies (Parent -> Child for Insert)
TABLE_MODEL_MAP = {
    "cat_dominio": common.CatDominio,
    "cat_parametro": common.CatParametro,
    "media_asset": common.MediaAsset,
    "confederacion": geo.Confederacion,
    "pais": geo.Pais,
    "region": geo.Region,
    "perfil_climatico": geo.PerfilClimatico,
    "ciudad": geo.Ciudad,
    "estadio": geo.Estadio,
    "asociacion": geo.Asociacion,
    "mundo": world.Mundo,
    "sistema_ranking": narrative.SistemaRanking,
    "temporada": world.Temporada,
    "regla_elegibilidad": competition.ReglaElegibilidad,
    "equipo": team.Equipo,
    "equipo_rating_actual": team.EquipoRatingActual,
    "equipo_institucion": team.EquipoInstitucion,
    "equipo_finanzas": team.EquipoFinanzas,
    "equipo_estadio_hist": team.EquipoEstadioHist,
    "equipo_elo_hist": narrative.EquipoEloHist,
    "rivalidad": team.Rivalidad,
    "perfil_sorteo": competition.PerfilSorteo,
    "competencia": competition.Competencia,
    "competencia_reputacion": competition.CompetenciaReputacion,
    "competencia_edicion": competition.CompetenciaEdicion,
    "etapa": competition.Etapa,
    "ronda": competition.Ronda,
    "grupo": competition.Grupo,
    "regla_clasificacion": narrative.ReglaClasificacion,
    "regla_asignacion_cupos": narrative.ReglaAsignacionCupos,
    "participante": competition.Participante,
    "tabla_posiciones": competition.TablaPosiciones,
    "ranking_entrada": narrative.RankingEntrada,
    "partido": match.Partido,
    "partido_clima": match.PartidoClima,
    "partido_contexto": match.PartidoContexto,
    "partido_stats_equipo": match.PartidoStatsEquipo,
    "evento_equipo": team.EventoEquipo,
    "historial_enfrentamiento": team.HistorialEnfrentamiento,
    "historia_narrativa": narrative.HistoriaNarrativa,
    "noticia": narrative.Noticia,
    "mundo_snapshot": world.MundoSnapshot,
    "snapshot_equipo": narrative.SnapshotEquipo,
    "sim_log": world.SimLog,
    "estadistica_global": narrative.EstadisticaGlobal
}

class DataTransferService:
    def __init__(self, db_session):
        self.db = db_session

    async def export_to_excel(self) -> tuple[bytes, list[str]]:
        """Exports DB to Excel bytes (Non-blocking) with logs."""
        logs = []
        all_data = {}
        
        logs.append("Starting database export...")
        processed = 0
        total = len(TABLE_MODEL_MAP)

        for table_name, model in TABLE_MODEL_MAP.items():
            processed += 1
            pct = int((processed / total) * 100)
            try:
                result = await self.db.execute(select(model))
                scalars = result.scalars().all()
                cols = [c.name for c in model.__table__.columns]
                
                rows = []
                for scalar in scalars:
                    row_dict = {}
                    for col in cols:
                        row_dict[col] = getattr(scalar, col, None)
                    rows.append(row_dict)
                
                all_data[table_name] = {"rows": rows, "cols": cols}
                logs.append(f"[{pct}%] Exported table: {table_name} ({len(rows)} rows)")
            except Exception as e:
                logs.append(f"[{pct}%] ERROR exporting {table_name}: {e}")
                all_data[table_name] = {"rows": [], "cols": []}

        import asyncio
        excel_bytes = await asyncio.to_thread(self._write_excel_sync, all_data)
        
        logs.append("[100%] Export file generated.")
        return excel_bytes, logs

    def _write_excel_sync(self, all_data: dict) -> bytes:
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        
        for table_name, content in all_data.items():
            try:
                df = pd.DataFrame(content["rows"])
                if df.empty and content["cols"]:
                    df = pd.DataFrame(columns=content["cols"])
                df.to_excel(writer, sheet_name=table_name, index=False)
            except Exception as e:
                print(f"Error writing sheet {table_name}: {e}")
                
        writer.close()
        return output.getvalue()

    async def reset_database(self) -> list[str]:
        """Truncates all tables with logging."""
        logs = []
        tables = list(TABLE_MODEL_MAP.keys())[::-1] # Child -> Parent
        total = len(tables)
        
        logs.append("--- Starting Database Reset ---")
        for i, table in enumerate(tables):
            pct = int(((i + 1) / total) * 100)
            try:
                await self.db.execute(text(f"TRUNCATE TABLE futsim.{table} RESTART IDENTITY CASCADE"))
                logs.append(f"[{pct}%] Deleted data from: {table}")
            except Exception as e:
                logs.append(f"[{pct}%] ERROR deleting {table}: {e}")

        await self.db.commit()
        logs.append("[100%] Database Wipe Complete.")
        return logs

    async def _get_catalog_cache(self):
        """Preloads all parameters into a cache for mapping strings to IDs."""
        from app.models.common import CatParametro
        
        stmt = select(CatParametro).options(joinedload(CatParametro.dominio))
        result = await self.db.execute(stmt)
        params = result.scalars().all()
        
        cache = {} # domain_code -> {param_code: id, param_desc: id}
        for p in params:
            d_code = p.dominio.codigo
            if d_code not in cache:
                cache[d_code] = {}
            cache[d_code][p.codigo] = p.parametro_id
            cache[d_code][p.descripcion] = p.parametro_id
        return cache

    async def import_from_excel(self, file_content: bytes) -> list[str]:
        """Imports Excel massive dump with Catalog Resolution (v7.0)."""
        logs = []
        try:
            xls = pd.ExcelFile(io.BytesIO(file_content))
        except Exception as e:
            return [f"CRITICAL ERROR: Invalid Excel file. {str(e)}"]

        # 1. Reset
        logs.append("Phase 1: Resetting Database...")
        reset_logs = await self.reset_database()
        logs.extend(reset_logs)
        
        # 2. Insert
        logs.append("Phase 2: Mass Insertion with ID Resolution...")
        sheets = xls.sheet_names
        total_sheets = len(sheets)
        
        # Initial cache (might be empty if catalogs are in this Excel)
        catalog_cache = await self._get_catalog_cache()

        COLUMN_DOMAIN_MAP = {
            "estado_id": "ESTADO_GENERICO",
            "estilo_id": "ESTILO_JUEGO",
            "salida_id": "TIPO_SALIDA",
            "transicion_id": "TRANSICION",
            "tipo_propiedad_id": "TIPO_PROPIEDAD",
            "tipo_cesped_id": "TIPO_CESPED",
            "condicion_id": "CLIMA_CONDICION",
            "metodo_id": "METODO_CLASIFICACION"
        }

        TABLE_SPECIFIC_DOMAINS = {
            "competencia": {"tipo_id": "COMPETENCIA_TIPO"},
            "etapa": {"tipo_id": "ETAPA_TIPO"},
            "evento_equipo": {"tipo_id": "EVENTO_EQUIPO"},
            "historia_narrativa": {"tipo_id": "NARRATIVA_TIPO"},
            "noticia": {"tipo_id": "NOTICIA_TIPO"},
        }

        processed_count = 0
        for table_name, model in TABLE_MODEL_MAP.items():
            if table_name in sheets:
                processed_count += 1
                pct = int((processed_count / total_sheets) * 100)
                
                try:
                    df = pd.read_excel(xls, sheet_name=table_name)
                    if not df.empty:
                        model_columns = {c.name: c for c in model.__table__.columns}
                        
                        # Handle Legacy columns (e.g. "estado" -> "estado_id")
                        for col in list(df.columns):
                            id_col = f"{col}_id"
                            if id_col in model_columns and col not in model_columns:
                                df[id_col] = df[col]

                        # 1. JSONB: Parse strings to dicts
                        json_cols = [c.name for c in model.__table__.columns if isinstance(c.type, JSONB)]
                        for col in json_cols:
                            if col in df.columns:
                                def parse_json(x):
                                    if isinstance(x, str):
                                        try:
                                            # Try standard JSON first
                                            return json.loads(x.replace("'", '"'))
                                        except:
                                            # Fallback: maybe it's already a dict representation as string
                                            try:
                                                import ast
                                                return ast.literal_eval(x)
                                            except:
                                                return x 
                                    return x
                                df[col] = df[col].apply(parse_json)

                        # 2. String/Text conversion
                        str_cols = [c.name for c in model.__table__.columns if isinstance(c.type, (String, Text))]
                        for col in str_cols:
                            if col in df.columns:
                                df[col] = df[col].apply(lambda x: str(x) if pd.notnull(x) and x is not None else None)

                        # 3. Date/DateTime conversion
                        date_cols = [c.name for c in model.__table__.columns if isinstance(c.type, (Date, DateTime))]
                        for col in date_cols:
                            if col in df.columns:
                                def parse_date(x):
                                    if pd.isnull(x): return None
                                    if hasattr(x, 'to_pydatetime'): return x.to_pydatetime()
                                    return x
                                df[col] = df[col].apply(parse_date)

                        # 4. ID Resolution (Skip for catalogs themselves)
                        if table_name not in ["cat_dominio", "cat_parametro"]:
                            for col in df.columns:
                                if col in model_columns and isinstance(model_columns[col].type, Integer):
                                    domain = TABLE_SPECIFIC_DOMAINS.get(table_name, {}).get(col) or COLUMN_DOMAIN_MAP.get(col)
                                    if domain and domain in catalog_cache:
                                        def resolve(val):
                                            if val is None or val == '' or pd.isna(val): return None
                                            if isinstance(val, (int, float)): 
                                                try: return int(float(val))
                                                except: return None
                                            s_val = str(val).strip()
                                            res = catalog_cache[domain].get(s_val)
                                            if res is None:
                                                for k, v in catalog_cache[domain].items():
                                                    if k.lower() == s_val.lower(): return v
                                            return res
                                        df[col] = df[col].apply(resolve)

                        # 4b. Special case for cat_parametro: ensure 'codigo' exists
                        if table_name == "cat_parametro":
                            if "codigo" not in df.columns:
                                df["codigo"] = None
                            
                            def ensure_code(row):
                                if pd.isnull(row.get("codigo")) or row.get("codigo") == "":
                                    desc = str(row.get("descripcion", f"param_{row.get('parametro_id')}"))
                                    return desc.replace(" ", "_").title()
                                return row["codigo"]
                            
                            df["codigo"] = df.apply(ensure_code, axis=1)

                        # 5. Final Cleanup: NaN -> None
                        df = df.astype(object)
                        df = df.where(pd.notnull(df), None)
                        
                        if table_name == "equipo_rating_actual":
                            stat_cols = ['ataque', 'defensa', 'mediocampo', 'moral', 'cohesion', 'disciplina']
                            for c in stat_cols:
                                if c in df.columns:
                                    def sanitize_stat(val):
                                        if val is None: return 50
                                        try:
                                            v = int(val); return v if v >= 1 else 50
                                        except: return 50
                                    df[c] = df[c].apply(sanitize_stat)
                            if 'equipo_id' in df.columns: df = df.dropna(subset=['equipo_id']) 
                            if 'elo_actual' in df.columns:
                                def sanitize_elo(val):
                                    if pd.isna(val) or val == '' or val is None: return None
                                    try: return float(val)
                                    except: return None
                                df['elo_actual'] = df['elo_actual'].apply(sanitize_elo)

                        final_cols = [c for c in df.columns if c in model_columns]
                        records = df[final_cols].to_dict('records')
                        
                        # Check for duplicates in records (ID column)
                        id_col = f"{table_name}_id"
                        if id_col in final_cols:
                            ids = [r[id_col] for r in records if r[id_col] is not None]
                            if len(ids) != len(set(ids)):
                                logs.append(f"WARNING: Duplicate IDs found in sheet '{table_name}'. First few rows might be overwritten or cause error.")

                        await self.db.run_sync(lambda session: session.bulk_insert_mappings(model, records))
                        
                        # Refresh cache if catalogs were updated
                        if table_name == "cat_parametro":
                            await self.db.commit() # Ensure they are persisted
                            catalog_cache = await self._get_catalog_cache()
                            logs.append(f"Refreshed catalog cache with {len(catalog_cache)} domains.")
                        
                        logs.append(f"[{pct}%] Inserted {len(records)} rows into '{table_name}'")
                    else:
                        logs.append(f"[{pct}%] Skipped '{table_name}' (Empty)")
                except Exception as e:
                    logs.append(f"[{pct}%] ERROR inserting '{table_name}': {str(e)}")
            
        try:
            await self.db.commit()
            logs.append("[100%] Mass Import Finished Successfully.")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"FATAL ERROR DURING COMMIT: {str(e)}")
            raise e
            
        return logs
