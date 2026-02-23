import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '..', 'docker', '.env')

load_dotenv(ENV_PATH)

DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_NAME = os.getenv('POSTGRES_DB')
EXCEL_FILE = os.path.join(BASE_DIR, 'sql', 'ListaClubes.xlsx')


engine = create_engine(
    f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)


def obtener_mapa_ids(tabla, campo_nombre, campo_id):
    """Descarga la tabla de la BD y crea un diccionario { 'Nombre': ID }"""
    with engine.connect() as conn:
        query = text(f"SELECT {campo_id}, {campo_nombre} FROM {tabla}")
        result = conn.execute(query)
        return {row[1]: row[0] for row in result}

def obtener_mapa_torneo_equipo():
    """
    Crea un diccionario complejo para buscar la inscripción:
    Clave: (torneoid, equipoid) -> Valor: torneoequipoid
    """
    with engine.connect() as conn:
        query = text("SELECT torneoequipoid, torneoid, equipoid FROM torneoequipo")
        result = conn.execute(query)
        return {(row[1], row[2]): row[0] for row in result}

def procesar_migracion():
    print("--- 1. Procesando Confederaciones ---")
    try:
        df_conf = pd.read_excel(EXCEL_FILE, sheet_name='Confederacion')
        df_conf.columns = df_conf.columns.str.lower()
        df_conf.to_sql('confederacion', engine, if_exists='append', index=False)
        print("Confederaciones insertadas.")
    except Exception:
        print("Probablemente ya existen datos en Confederacion.")
    
    mapa_conf = obtener_mapa_ids('confederacion', 'nombre', 'confederacionid')

    print("--- 2. Procesando Paises ---")
    df_pais = pd.read_excel(EXCEL_FILE, sheet_name='Pais')
    df_pais.columns = df_pais.columns.str.lower()
    
    if 'pertenecefifa' in df_pais.columns:
        df_pais['pertenecefifa'] = df_pais['pertenecefifa'].fillna(0).astype(bool)

    df_pais['confederacionid'] = df_pais['confederacionid'].map(mapa_conf)
    df_pais = df_pais.dropna(subset=['confederacionid']) 
    
    df_pais.to_sql('pais', engine, if_exists='append', index=False)
    print("Paises insertados.")
    
    mapa_pais = obtener_mapa_ids('pais', 'nombre', 'paisid')

    print("--- 3. Procesando Regiones ---")
    df_region = pd.read_excel(EXCEL_FILE, sheet_name='Region')
    df_region.columns = df_region.columns.str.lower()
    
    df_region['paisid'] = df_region['paisid'].map(mapa_pais)
    df_region = df_region.dropna(subset=['paisid'])
    
    df_region.to_sql('region', engine, if_exists='append', index=False)
    print("Regiones insertadas.")

    mapa_region = obtener_mapa_ids('region', 'nombre', 'regionid')

    print("--- 4. Procesando Ciudades ---")
    df_ciudad = pd.read_excel(EXCEL_FILE, sheet_name='Ciudad')
    df_ciudad.columns = df_ciudad.columns.str.lower()
    
    if 'escapital' in df_ciudad.columns:
        df_ciudad['escapital'] = df_ciudad['escapital'].fillna(0).astype(bool)
    
    df_ciudad['regionid'] = df_ciudad['regionid'].map(mapa_region)
    df_ciudad = df_ciudad.dropna(subset=['regionid'])
    
    df_ciudad.to_sql('ciudad', engine, if_exists='append', index=False)
    print("Ciudades insertadas.")
    
    mapa_ciudad = obtener_mapa_ids('ciudad', 'nombre', 'ciudadid')

    print("--- 5. Procesando Torneos ---")
    df_torneo = pd.read_excel(EXCEL_FILE, sheet_name='Torneo')
    df_torneo.columns = df_torneo.columns.str.lower()
    
    df_torneo['paisid'] = df_torneo['paisid'].map(mapa_pais)
    df_torneo['confederacionid'] = df_torneo['confederacionid'].map(mapa_conf)
    
    df_torneo.to_sql('torneo', engine, if_exists='append', index=False)
    print("Torneos insertados.")
    
    mapa_torneo = obtener_mapa_ids('torneo', 'nombre', 'torneoid')

    print("--- 6. Procesando Equipos ---")
    df_equipo = pd.read_excel(EXCEL_FILE, sheet_name='Equipo')
    df_equipo.columns = df_equipo.columns.str.lower()
    
    if 'ciudadid' in df_equipo.columns:
        df_equipo['ciudadid'] = df_equipo['ciudadid'].map(mapa_ciudad)
    
    if 'regionid' in df_equipo.columns:
        df_equipo['regionid'] = df_equipo['regionid'].map(mapa_region)

    columnas_renombrar = {
        'añofundacion': 'aniofundacion', 
        'año': 'anio',
        'anio': 'aniofundacion'
    }
    df_equipo.rename(columns=columnas_renombrar, inplace=True)

    df_equipo.to_sql('equipo', engine, if_exists='append', index=False)
    print("Equipos insertados.")
    
    mapa_equipo = obtener_mapa_ids('equipo', 'nombre', 'equipoid')

    print("--- 7. Procesando Participantes (TorneoEquipo) ---")
    df_te = pd.read_excel(EXCEL_FILE, sheet_name='TorneoEquipo')
    df_te.columns = df_te.columns.str.lower()
    
    df_te.rename(columns={'añoparticipacion': 'anioparticipacion'}, inplace=True)

    df_te['torneoid'] = df_te['torneoid'].map(mapa_torneo)
    df_te['equipoid'] = df_te['equipoid'].map(mapa_equipo)
    
    df_te = df_te.dropna(subset=['torneoid', 'equipoid'])
    
    df_te.to_sql('torneoequipo', engine, if_exists='append', index=False)
    print("Participantes vinculados.")


    print("--- 8. Procesando Partidos ---")
    try:
        df_partido = pd.read_excel(EXCEL_FILE, sheet_name='Partido')
        df_partido.columns = df_partido.columns.str.lower()
        df_partido['torneoid'] = df_partido['torneoid'].map(mapa_torneo)
        df_partido['id_local_temp'] = df_partido['equipolocaltorneoequipoid'].map(mapa_equipo)
        df_partido['id_visitante_temp'] = df_partido['equipovisitantetorneoequipoid'].map(mapa_equipo)
        mapa_te_complejo = obtener_mapa_torneo_equipo()
        
        def buscar_inscripcion(row, col_equipo_temp):
            clave = (row['torneoid'], row[col_equipo_temp])
            return mapa_te_complejo.get(clave, None)

        df_partido['equipolocaltorneoequipoid'] = df_partido.apply(lambda row: buscar_inscripcion(row, 'id_local_temp'), axis=1)
        df_partido['equipovisitantetorneoequipoid'] = df_partido.apply(lambda row: buscar_inscripcion(row, 'id_visitante_temp'), axis=1)

        df_partido.rename(columns={'añoparticipacion': 'anioparticipacion'}, inplace=True)
        
        cols_db = ['torneoid', 'equipolocaltorneoequipoid', 'equipovisitantetorneoequipoid', 
                   'goleslocal', 'golesvisitante', 'nrofecha', 'anioparticipacion', 'fase', 'grupo', 'estado']
        
        df_final_partidos = df_partido.dropna(subset=['equipolocaltorneoequipoid', 'equipovisitantetorneoequipoid'])[cols_db]
        
        df_final_partidos.to_sql('partido', engine, if_exists='append', index=False)
        print(f"{len(df_final_partidos)} Partidos insertados.")
        
    except Exception as e:
        print(f"Error en Partidos: {e}")

    print("--- 9. Procesando Resultados ---")
    try:
        df_res = pd.read_excel(EXCEL_FILE, sheet_name='TorneoResultados')
        df_res.columns = df_res.columns.str.lower()
        
        df_res['torneoid'] = df_res['torneoid'].map(mapa_torneo)
        df_res['campeonequipoid'] = df_res['campeonequipoid'].map(mapa_equipo)
        df_res['subcampeonequipoid'] = df_res['subcampeonequipoid'].map(mapa_equipo)
        
        df_res.rename(columns={'añotorneo': 'aniotorneo'}, inplace=True)
        
        df_res = df_res.dropna(subset=['torneoid', 'aniotorneo'])
        
        df_res.to_sql('torneoresultados', engine, if_exists='append', index=False)
        print("Resultados insertados.")
        
    except Exception as e:
        print(f"Error en Resultados: {e}")
    
    print("--- 10. Procesando Palmares (Automático) ---")
    try:
        df_palmares = df_res[['aniotorneo', 'campeonequipoid', 'torneoid']].copy()
        
        df_palmares.rename(columns={
            'aniotorneo': 'aniotitulo',
            'campeonequipoid': 'equipoid'
        }, inplace=True)
        
        df_palmares = df_palmares.dropna(subset=['equipoid'])
        
        df_palmares.to_sql('palmares', engine, if_exists='append', index=False)
        print(f"{len(df_palmares)} Registros de Palmares insertados.")
        
    except Exception as e:
        print(f"Error generando Palmares: {e}")

if __name__ == "__main__":
    try:
        procesar_migracion()
        print("\n¡MIGRACIÓN EXITOSA!")
    except Exception as e:
        print(f"\nERROR CRÍTICO: {e}")