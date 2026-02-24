import re
import os
from datetime import date
from sqlalchemy.future import select
from sqlalchemy import text
from app.models import geo, world, team, common
from app.models import competition as comp_models

LEGACY_DIR = "../database_legacy"
GLOBAL_FILE = os.path.join(LEGACY_DIR, "2-InsertarDatosGlobales_FutbolDB2.sql")
PARAGUAY_FILE = os.path.join(LEGACY_DIR, "Paraguay_CargaDatos_FutbolDB2.sql")

class SeedingService:
    def __init__(self, db):
        self.db = db

    async def _read_file(self, filepath, encoding_options=['utf-16', 'latin-1']):
        for enc in encoding_options:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    return f.read()
            except UnicodeError:
                continue
            except FileNotFoundError:
                return None
        return None

    async def reset_db(self):
        # Truncate all tables in schema futsim
        # ORDER IS IMPORTANT due to FKs
        tables = [
             "participante", "competencia_edicion", "competencia", "temporada",
             "equipo_rating_actual", "equipo", "ciudad", "region", "pais", "confederacion",
             "cat_competencia_tipo", "mundo"
        ]
        for tbl in tables:
             await self.db.execute(text(f"TRUNCATE TABLE futsim.{tbl} CASCADE"))
        await self.db.commit()
        return {"status": "Database reset complete"}

    async def seed_world(self):
        result = await self.db.execute(select(world.Mundo).filter_by(mundo_id=1))
        if not result.scalars().first():
            mundo = world.Mundo(mundo_id=1, nombre="Tierra Real", semilla_rng=12345)
            self.db.add(mundo)
            await self.db.commit()
            return "World created."
        return "World already exists."

    async def seed_confederations(self):
        content = await self._read_file(GLOBAL_FILE, ['latin-1'])
        if not content: return "Global file not found."
        
        matches = re.findall(r"INSERT INTO Confederacion \(Nombre\) VALUES\s*(.*?);", content, re.DOTALL)
        count = 0
        for block in matches:
            rows = re.findall(r"\('([^']+)'\)", block)
            for name in rows:
                exists = await self.db.execute(select(geo.Confederacion).filter_by(nombre=name))
                if not exists.scalars().first():
                    conf = geo.Confederacion(nombre=name)
                    self.db.add(conf)
                    count += 1
        await self.db.commit()
        return f"Seeded {count} confederations."

    async def seed_countries(self):
        content = await self._read_file(GLOBAL_FILE, ['latin-1'])
        if not content: return "Global file not found."

        res = await self.db.execute(select(geo.Confederacion))
        confeds = {c.nombre: c.confederacion_id for c in res.scalars().all()}
        
        lines = content.split('\n')
        count = 0
        for line in lines:
            if "INSERT INTO Pais" in line: continue
            match = re.search(r"\('([^']+)', '([^']+)', \(SELECT .*? WHERE Nombre = '([^']+)'\)\)", line)
            if match:
                name, iso, conf_name = match.groups()
                if conf_name in confeds:
                    exists = await self.db.execute(select(geo.Pais).filter_by(iso_code=iso))
                    if not exists.scalars().first():
                        pais = geo.Pais(nombre=name, iso_code=iso, confederacion_id=confeds[conf_name])
                        self.db.add(pais)
                        count += 1
        await self.db.commit()
        return f"Seeded {count} countries."

    async def seed_paraguay_geo(self):
        content = await self._read_file(PARAGUAY_FILE)
        if not content: return "Paraguay file not found."
        
        # Ensure Paraguay exists
        res = await self.db.execute(select(geo.Pais).filter_by(nombre="Paraguay"))
        paraguay = res.scalars().first()
        if not paraguay: return "Paraguay country not found. Run global seed first."
        
        # Regions
        reg_matches = re.findall(r"\('([^']+)', '([^']+)', \(SELECT .*? 'Paraguay'\)\)", content)
        reg_count = 0
        for name, tipo in reg_matches:
            exists = await self.db.execute(select(geo.Region).filter_by(nombre=name, pais_id=paraguay.pais_id))
            if not exists.scalars().first():
                self.db.add(geo.Region(nombre=name, tipo_region=tipo, pais_id=paraguay.pais_id))
                reg_count += 1
        await self.db.commit()

        # Cities
        res = await self.db.execute(select(geo.Region))
        regions = {r.nombre: r.region_id for r in res.scalars().all()}
        
        cit_matches = re.findall(r"\('([^']+)', \(SELECT .*? WHERE Nombre = '([^']+)'\), \d\)", content)
        cit_count = 0
        for name, region_name in cit_matches:
            if region_name in regions:
                exists = await self.db.execute(select(geo.Ciudad).filter_by(nombre=name, region_id=regions[region_name]))
                if not exists.scalars().first():
                    self.db.add(geo.Ciudad(nombre=name, region_id=regions[region_name]))
                    cit_count += 1
        await self.db.commit()
        
        return f"Seeded {reg_count} regions and {cit_count} cities."

    async def seed_teams(self):
        content = await self._read_file(PARAGUAY_FILE)
        if not content: return "Paraguay file not found."
        
        res = await self.db.execute(select(geo.Ciudad))
        cities = {c.nombre: c.ciudad_id for c in res.scalars().all()}
        
        # Updated Regex
        pattern = r"\('([^']+)', '([^']+)', (?:NULL|\(SELECT .*?Region WHERE Nombre = '([^']+)'\)), (?:NULL|\(SELECT .*?Ciudad WHERE Nombre = '([^']+)'\)), (\d+|NULL), ([\d\.]+|NULL), '([^']+)', '([^']+)'\)"
        matches = re.findall(pattern, content)
        
        count = 0
        for name, code, region_name, city_name, year, elo, tipo, estado in matches:
             # Basic existence check
             exists = await self.db.execute(select(team.Equipo).filter_by(nombre=name, mundo_id=1))
             if exists.scalars().first(): continue
             
             new_team = team.Equipo(
                 mundo_id=1,
                 nombre=name,
                 codigo_tla=code if len(code) <= 3 else code[:3],
                 anio_fundacion=int(year) if year != 'NULL' else None,
                 estado=estado.upper()
             )
             self.db.add(new_team)
             await self.db.flush()
             
             if elo != 'NULL':
                  rating = team.EquipoRatingActual(
                      equipo_id=new_team.equipo_id,
                      elo_actual=float(elo),
                      ataque=int(float(elo)/20), defensa=int(float(elo)/20), mediocampo=int(float(elo)/20)
                  )
                  self.db.add(rating)
             count += 1
             
        await self.db.commit()
        return f"Seeded {count} teams."

    async def seed_tournaments(self):
        content = await self._read_file(PARAGUAY_FILE)
        if not content: return "Paraguay file not found."
        
        # 1. Catalogs
        types = [("LIGA", "Liga"), ("COPA", "Copa"), ("SUPERCOPA", "Supercopa"), ("AMISTOSO", "Amistoso"), ("OTRO", "Otro")]
        for code, desc in types:
             exists = await self.db.execute(select(common.CatCompetenciaTipo).filter_by(codigo=code))
             if not exists.scalars().first():
                 self.db.add(common.CatCompetenciaTipo(codigo=code, descripcion=desc))
        await self.db.commit()
        
        # 2. Seasons
        matches = re.findall(r", (\d{4}), ", content)
        for year_str in sorted(list(set(matches))):
            year = int(year_str)
            exists = await self.db.execute(select(world.Temporada).filter_by(mundo_id=1, nombre=str(year)))
            if not exists.scalars().first():
                self.db.add(world.Temporada(mundo_id=1, nombre=str(year), fecha_inicio=date(year, 1, 1), fecha_fin=date(year, 12, 31), es_actual=(year==2025)))
        await self.db.commit()

        # 3. Competitions
        res = await self.db.execute(select(common.CatCompetenciaTipo))
        cats = {c.descripcion.upper(): c.tipo_id for c in res.scalars().all()}
        
        pattern = r"\('([^']+)', '([^']+)', (?:NULL|'([^']+)'),"
        matches = re.findall(pattern, content)
        comp_count = 0
        for name, tipo, cat in matches:
             exists = await self.db.execute(select(comp_models.Competencia).filter_by(nombre=name, mundo_id=1))
             if not exists.scalars().first():
                 cat_id = cats.get("LIGA") 
                 if "COPA" in tipo.upper(): cat_id = cats.get("COPA")
                 self.db.add(comp_models.Competencia(mundo_id=1, nombre=name, tipo_id=cat_id))
                 comp_count += 1
        await self.db.commit()
        
        # 4. Participants
        # Reuse logic from seed_legacy.py but condensed
        res = await self.db.execute(select(comp_models.Competencia).filter_by(mundo_id=1))
        comps = {c.nombre: c.competencia_id for c in res.scalars().all()}
        res = await self.db.execute(select(world.Temporada).filter_by(mundo_id=1))
        seasons = {s.nombre: s.temporada_id for s in res.scalars().all()}
        res = await self.db.execute(select(team.Equipo).filter_by(mundo_id=1))
        teams = {t.nombre: t.equipo_id for t in res.scalars().all()}
        
        pattern = r"\(SELECT TorneoID .*? Nombre = '([^']+)'\).*?\(SELECT EquipoID .*? Nombre = '([^']+)'\).*?, (\d{4}), '([^']+)', (?:NULL|'([^']+)')"
        matches = re.findall(pattern, content)
        
        part_count = 0
        editions_cache = {} # (comp_id, season_id) -> ed_id

        for comp_name, team_name, year_str, fase, group in matches:
             if comp_name not in comps or team_name not in teams or year_str not in seasons: continue
             
             comp_id, season_id, team_id = comps[comp_name], seasons[year_str], teams[team_name]
             key = (comp_id, season_id)
             
             if key not in editions_cache:
                  res = await self.db.execute(select(comp_models.CompetenciaEdicion).filter_by(competencia_id=comp_id, temporada_id=season_id))
                  ed = res.scalars().first()
                  if not ed:
                       ed = comp_models.CompetenciaEdicion(competencia_id=comp_id, temporada_id=season_id, nombre_display=f"{comp_name} {year_str}")
                       self.db.add(ed)
                       await self.db.flush()
                  editions_cache[key] = ed.edicion_id
             
             ed_id = editions_cache[key]
             res = await self.db.execute(select(comp_models.Participante).filter_by(edicion_id=ed_id, equipo_id=team_id))
             if not res.scalars().first():
                  self.db.add(comp_models.Participante(edicion_id=ed_id, equipo_id=team_id, grupo_inicial_texto=group if group else None))
                  part_count += 1
        
        await self.db.commit()
        return f"Seeded {comp_count} competitions and {part_count} participants."
