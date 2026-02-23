from flask import Flask, render_template, request, jsonify
from db import execute_query
import sys
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
DATABASE_DIR = os.path.join(PROJECT_ROOT, 'database')

sys.path.append(DATABASE_DIR)

try:
    from simulador_elo import SimuladorFutbol
except ImportError:
    print("Advertencia: No se encontró 'simulador_elo.py', la simulación no funcionará.")

app = Flask(__name__)


# ==========================================
# Home 
#
@app.route('/')
def index():
    stats = execute_query("""
        SELECT 
            (SELECT COUNT(*) FROM equipo) as total_equipos,
            (SELECT COUNT(*) FROM torneo WHERE estado = 'Activo') as torneos_activos,
            (SELECT COUNT(*) FROM partido WHERE estado = 'Finalizado') as partidos_jugados
    """)
    resumen = stats[0] if stats else {}
    recientes = execute_query("""
        SELECT p.nrofecha, el.nombre as local, ev.nombre as visitante, 
               p.goleslocal, p.golesvisitante, t.nombre as torneo
        FROM partido p
        JOIN torneoequipo tel ON p.equipolocaltorneoequipoid = tel.torneoequipoid
        JOIN torneoequipo tev ON p.equipovisitantetorneoequipoid = tev.torneoequipoid
        JOIN equipo el ON tel.equipoid = el.equipoid
        JOIN equipo ev ON tev.equipoid = ev.equipoid
        JOIN torneo t ON p.torneoid = t.torneoid
        WHERE p.estado = 'Finalizado'
        ORDER BY p.partidoid DESC LIMIT 3
    """)
    return render_template('index.html', resumen=resumen, recientes=recientes)
# ==========================================


# ==========================================
# Equipos
#
@app.route('/equipos')
def equipos_view():
    return render_template('equipos.html')

@app.route('/api/equipos/listar', methods=['GET'])
def equipos_listar():
    nombre = request.args.get('nombre', '')
    sql = """
        SELECT e.equipoid, 
               e.nombre, 
               e.codigoequipo, 
               COALESCE(c.nombre, 'N/A') as ciudad, 
               COALESCE(r.nombre, 'N/A') as region,
               e.aniofundacion, 
               e.elo, 
               e.tipoequipo,
               e.estado
        FROM equipo e
        LEFT JOIN ciudad c ON e.ciudadid = c.ciudadid
        LEFT JOIN region r ON e.regionid = r.regionid
        WHERE 1=1
    """
    params = []
    
    if nombre:
        sql += " AND e.nombre ILIKE %s"
        params.append(f"%{nombre}%")
        
    sql += " ORDER BY e.nombre ASC"
    
    data = execute_query(sql, tuple(params))
    return jsonify({'data': data})

@app.route('/api/equipos/buscar/<int:id>', methods=['GET'])
def equipos_buscar(id):
    sql = """
        SELECT e.equipoid, e.nombre, e.codigoequipo, e.aniofundacion, 
               e.estado, e.elo, e.tipoequipo,
               e.ciudadid, e.regionid, r.paisid
        FROM equipo e
        LEFT JOIN region r ON e.regionid = r.regionid
        WHERE e.equipoid = %s
    """
    data = execute_query(sql, (id,))
    return jsonify(data[0] if data else None)

@app.route('/api/equipos/guardar', methods=['POST'])
def equipos_guardar():
    data = request.json
    try:
        equipoid = int(data.get('EquipoID', 0))
        ciudad_id = data.get('CiudadID') if data.get('CiudadID') else None
        region_id = data.get('RegionID') if data.get('RegionID') else None
        
        elo = float(data.get('ELO', 1000))
        tipo = data.get('Tipo')
        estado = data.get('Estado')

        if equipoid == 0:
            sql = """INSERT INTO equipo (nombre, codigoequipo, regionid, ciudadid, aniofundacion, 
                                         elo, tipoequipo, estado) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            params = (data['Nombre'], data['Codigo'], region_id, ciudad_id, data['Anio'], 
                      elo, tipo, estado)
        else:
            sql = """UPDATE equipo SET nombre=%s, codigoequipo=%s, regionid=%s, ciudadid=%s, 
                                       aniofundacion=%s, elo=%s, tipoequipo=%s, estado=%s
                     WHERE equipoid=%s"""
            params = (data['Nombre'], data['Codigo'], region_id, ciudad_id, data['Anio'], 
                      elo, tipo, estado, equipoid)
        
        execute_query(sql, params, fetch=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/equipos/eliminar/<int:id>', methods=['POST'])
def equipos_eliminar(id):
    try:
        execute_query("DELETE FROM equipo WHERE equipoid = %s", (id,), fetch=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': "No se puede eliminar. Posiblemente tenga partidos o historial asociado."})

# --
@app.route('/api/general/regiones', methods=['GET'])
def get_regiones():
    data = execute_query("SELECT regionid, nombre FROM region ORDER BY nombre")
    return jsonify(data)

@app.route('/api/general/ciudades/<int:region_id>', methods=['GET'])
def get_ciudades_por_region(region_id):
    sql = "SELECT ciudadid, nombre FROM ciudad WHERE regionid = %s ORDER BY nombre"
    data = execute_query(sql, (region_id,))
    return jsonify(data)

@app.route('/api/general/ciudades/pais/<int:pais_id>', methods=['GET'])
def get_ciudades_por_pais(pais_id):
    sql = """
        SELECT c.ciudadid, c.nombre, r.nombre as region_nombre, r.regionid
        FROM ciudad c
        JOIN region r ON c.regionid = r.regionid
        WHERE r.paisid = %s
        ORDER BY c.nombre ASC
    """
    data = execute_query(sql, (pais_id,))
    return jsonify(data)
# ==========================================


# ==========================================
# Torneos
# 
@app.route('/torneos')
def torneos_view():
    return render_template('torneos.html')

@app.route('/api/torneos/por_pais/<int:pais_id>', methods=['GET'])
def get_torneos_por_pais(pais_id):
    sql = """
        SELECT torneoid, nombre, tipotorneo, categoria 
        FROM torneo 
        WHERE paisid = %s AND estado = 'Activo'
        ORDER BY nombre
    """
    return jsonify(execute_query(sql, (pais_id,)))

@app.route('/api/torneos/equipos_participantes', methods=['GET'])
def get_equipos_participantes():
    torneo_id = request.args.get('torneo_id')
    anio = request.args.get('anio')
    
    sql = """
        SELECT e.nombre, e.codigoequipo, c.nombre as ciudad
        FROM torneoequipo te
        JOIN equipo e ON te.equipoid = e.equipoid
        LEFT JOIN ciudad c ON e.ciudadid = c.ciudadid
        WHERE te.torneoid = %s AND te.anioparticipacion = %s
        ORDER BY e.nombre
    """
    data = execute_query(sql, (torneo_id, anio))
    return jsonify({'data': data})

@app.route('/api/torneos/simular', methods=['POST'])
def simular_torneo():
    data = request.json
    torneo_nombre = data.get('nombre')
    anio = int(data.get('anio'))
    
    try:
        simulador = SimuladorFutbol()
        simulador.simular_torneo(torneo_nombre, anio)
        return jsonify({'success': True, 'message': 'Simulación completada.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ---
@app.route('/api/general/confederaciones', methods=['GET'])
def get_confederaciones_general():
    return jsonify(execute_query("SELECT confederacionid, nombre FROM confederacion ORDER BY nombre"))

@app.route('/api/general/paises/confederacion/<int:conf_id>', methods=['GET'])
def get_paises_por_confederacion(conf_id):
    print(f"Buscando países para Confederación ID: {conf_id}")
    sql = "SELECT paisid, nombre FROM pais WHERE confederacionid = %s ORDER BY nombre"
    resultado = execute_query(sql, (conf_id,))
    print(f"Se encontraron {len(resultado) if resultado else 0} países.")    
    return jsonify(resultado)
#==========================================


# ==========================================
# Confederaciones
# 
@app.route('/confederaciones')
def confederaciones_view():
    return render_template('confederaciones.html')

@app.route('/api/confederaciones/listar', methods=['GET'])
def confederaciones_listar():
    sql = "SELECT confederacionid, nombre FROM confederacion ORDER BY nombre ASC"
    data = execute_query(sql)
    return jsonify({'data': data})

@app.route('/api/confederaciones/buscar/<int:id>', methods=['GET'])
def confederaciones_buscar(id):
    sql = "SELECT confederacionid, nombre FROM confederacion WHERE confederacionid = %s"
    data = execute_query(sql, (id,))
    return jsonify(data[0] if data else None)

@app.route('/api/confederaciones/guardar', methods=['POST'])
def confederaciones_guardar():
    data = request.json
    try:
        conf_id = int(data.get('ConfederacionID', 0))
        nombre = data.get('Nombre').strip()
        
        if not nombre:
            return jsonify({'success': False, 'message': "El nombre es obligatorio."})

        if conf_id == 0: 
            sql = "INSERT INTO confederacion (nombre) VALUES (%s)"
            params = (nombre,)
        else:
            sql = "UPDATE confederacion SET nombre=%s WHERE confederacionid=%s"
            params = (nombre, conf_id)
            
        execute_query(sql, params, fetch=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/confederaciones/eliminar/<int:id>', methods=['POST'])
def confederaciones_eliminar(id):
    try:
        execute_query("DELETE FROM confederacion WHERE confederacionid = %s", (id,), fetch=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': "No se puede eliminar: Hay países asociados a esta confederación."})
# ==========================================


# ==========================================
# Países
# 
@app.route('/paises')
def paises_view():
    return render_template('paises.html')

@app.route('/api/paises/listar', methods=['GET'])
def paises_listar():
    sql = """
        SELECT p.paisid, p.nombre, p.codigofifa, c.nombre as nombreconfederacion
        FROM pais p
        JOIN confederacion c ON p.confederacionid = c.confederacionid
        ORDER BY p.nombre ASC
    """
    data = execute_query(sql)
    return jsonify({'data': data})

@app.route('/api/paises/buscar/<int:id>', methods=['GET'])
def paises_buscar(id):
    sql = "SELECT paisid, nombre, codigofifa, confederacionid FROM pais WHERE paisid = %s"
    data = execute_query(sql, (id,))
    return jsonify(data[0] if data else None)

@app.route('/api/paises/guardar', methods=['POST'])
def paises_guardar():
    data = request.json
    try:
        pais_id = int(data.get('PaisID', 0))
        
        if pais_id == 0:
            sql = """INSERT INTO pais (nombre, codigofifa, confederacionid, pertenecefifa) 
                     VALUES (%s, %s, %s, TRUE)"""
            params = (data['Nombre'], data['CodigoFIFA'], data['ConfederacionID'])
        else:
            sql = """UPDATE pais SET nombre=%s, codigofifa=%s, confederacionid=%s 
                     WHERE paisid=%s"""
            params = (data['Nombre'], data['CodigoFIFA'], data['ConfederacionID'], pais_id)
            
        execute_query(sql, params, fetch=False)
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error guardando país: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/paises/eliminar/<int:id>', methods=['POST'])
def paises_eliminar(id):
    try:
        execute_query("DELETE FROM pais WHERE paisid = %s", (id,), fetch=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': "No se puede eliminar: Probablemente tenga datos asociados."})

# ---
@app.route('/api/paises/confederaciones', methods=['GET'])
def paises_confederaciones():
    data = execute_query("SELECT confederacionid, nombre FROM confederacion ORDER BY nombre")
    return jsonify(data)
# ==========================================


# ==========================================
# Regiones
# 
@app.route('/regiones')
def regiones_view():
    return render_template('regiones.html')

@app.route('/api/regiones/listar', methods=['GET'])
def regiones_listar():
    sql = """
        SELECT r.regionid, r.nombre, r.tiporegion, p.nombre as nombrepais
        FROM region r
        JOIN pais p ON r.paisid = p.paisid
        ORDER BY r.nombre ASC
    """
    data = execute_query(sql)
    return jsonify({'data': data})

@app.route('/api/regiones/buscar/<int:id>', methods=['GET'])
def regiones_buscar(id):
    sql = "SELECT regionid, nombre, tiporegion, paisid FROM region WHERE regionid = %s"
    data = execute_query(sql, (id,))
    return jsonify(data[0] if data else None)

@app.route('/api/regiones/guardar', methods=['POST'])
def regiones_guardar():
    data = request.json
    try:
        region_id = int(data.get('RegionID', 0))
        nombre = data.get('Nombre')
        tipo = data.get('TipoRegion')
        pais_id = data.get('PaisID')

        if not pais_id:
            return jsonify({'success': False, 'message': "Debe seleccionar un país."})

        if region_id == 0:
            sql = "INSERT INTO region (nombre, tiporegion, paisid) VALUES (%s, %s, %s)"
            params = (nombre, tipo, pais_id)
        else:
            sql = "UPDATE region SET nombre=%s, tiporegion=%s, paisid=%s WHERE regionid=%s"
            params = (nombre, tipo, pais_id, region_id)
            
        execute_query(sql, params, fetch=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/regiones/eliminar/<int:id>', methods=['POST'])
def regiones_eliminar(id):
    try:
        execute_query("DELETE FROM region WHERE regionid = %s", (id,), fetch=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': "No se puede eliminar: Hay ciudades o equipos asociados."})

# ---
@app.route('/api/general/paises', methods=['GET'])
def get_paises_general():
    data = execute_query("SELECT paisid, nombre FROM pais ORDER BY nombre")
    return jsonify(data)

@app.route('/api/general/regiones/pais/<int:pais_id>', methods=['GET'])
def get_regiones_por_pais(pais_id):
    sql = "SELECT regionid, nombre FROM region WHERE paisid = %s ORDER BY nombre"
    data = execute_query(sql, (pais_id,))
    return jsonify(data)
# ==========================================


# ==========================================
# Ciudades
#
@app.route('/ciudades')
def ciudades_view():
    return render_template('ciudades.html')

@app.route('/api/ciudades/listar', methods=['GET'])
def ciudades_listar():
    sql = """
        SELECT c.ciudadid, c.nombre, c.escapital, 
               r.nombre as region, p.nombre as pais
        FROM ciudad c
        JOIN region r ON c.regionid = r.regionid
        JOIN pais p ON r.paisid = p.paisid
        ORDER BY c.nombre ASC
    """
    data = execute_query(sql)
    return jsonify({'data': data})

@app.route('/api/ciudades/buscar/<int:id>', methods=['GET'])
def ciudades_buscar(id):
    sql = """
        SELECT c.ciudadid, c.nombre, c.escapital, c.regionid, r.paisid
        FROM ciudad c
        JOIN region r ON c.regionid = r.regionid
        WHERE c.ciudadid = %s
    """
    data = execute_query(sql, (id,))
    return jsonify(data[0] if data else None)

@app.route('/api/ciudades/guardar', methods=['POST'])
def ciudades_guardar():
    data = request.json
    try:
        ciudad_id = int(data.get('CiudadID', 0))
        nombre = data.get('Nombre')
        region_id = data.get('RegionID')
        es_capital = bool(data.get('EsCapital')) 

        if not region_id:
            return jsonify({'success': False, 'message': "Debe seleccionar una región."})

        if ciudad_id == 0:
            sql = "INSERT INTO ciudad (nombre, regionid, escapital) VALUES (%s, %s, %s)"
            params = (nombre, region_id, es_capital)
        else:
            sql = "UPDATE ciudad SET nombre=%s, regionid=%s, escapital=%s WHERE ciudadid=%s"
            params = (nombre, region_id, es_capital, ciudad_id)
            
        execute_query(sql, params, fetch=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/ciudades/eliminar/<int:id>', methods=['POST'])
def ciudades_eliminar(id):
    try:
        execute_query("DELETE FROM ciudad WHERE ciudadid = %s", (id,), fetch=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': "No se puede eliminar: Hay equipos o torneos asociados."})
# ==========================================


# ========================================== 
# Partidos
#
@app.route('/api/partidos/listar', methods=['GET'])
def partidos_listar():
    torneo_id = request.args.get('torneo_id')
    anio = request.args.get('anio')
    
    sql = """
        SELECT p.partidoid, p.nrofecha, p.fase, p.grupo, p.estado,
               p.goleslocal, p.golesvisitante,
               el.nombre as local, el.codigoequipo as codigo_local,
               ev.nombre as visitante, ev.codigoequipo as codigo_visitante
        FROM partido p
        JOIN torneoequipo tel ON p.equipolocaltorneoequipoid = tel.torneoequipoid
        JOIN torneoequipo tev ON p.equipovisitantetorneoequipoid = tev.torneoequipoid
        JOIN equipo el ON tel.equipoid = el.equipoid
        JOIN equipo ev ON tev.equipoid = ev.equipoid
        WHERE p.torneoid = %s AND p.anioparticipacion = %s
        ORDER BY p.nrofecha ASC, p.partidoid ASC
    """
    data = execute_query(sql, (torneo_id, anio))
    return jsonify({'data': data})

@app.route('/api/partidos/guardar_resultado', methods=['POST'])
def partidos_guardar_manual():
    data = request.json
    try:
        partido_id = data.get('partido_id')
        goles_local = int(data.get('goles_local'))
        goles_visita = int(data.get('goles_visita'))
        sim = SimuladorFutbol()
        sim.registrar_manual(partido_id, goles_local, goles_visita)

        return jsonify({'success': True, 'message': 'Resultado guardado y ELO actualizado.'})

    except Exception as e:
        print(f"Error guardando manual: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/partidos/simular_uno/<int:partido_id>', methods=['POST'])
def simular_partido_individual(partido_id):
    try:
        simulador = SimuladorFutbol()
        exito = simulador.simular_uno(partido_id)
        
        if exito:
            return jsonify({'success': True, 'message': 'Partido simulado correctamente.'})
        else:
            return jsonify({'success': False, 'message': 'El partido no se pudo simular (quizás ya finalizó).'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/torneos/posiciones', methods=['GET'])
def obtener_posiciones_filtrado():
    torneo_id = request.args.get('torneo_id')
    anio = request.args.get('anio')
    
    sql = """
        SELECT e.nombre, tp.pj, tp.pg, tp.pe, tp.pp, tp.gf, tp.gc, tp.dg, tp.pts, 
               tp.fase, tp.grupo
        FROM tablaposiciones tp
        JOIN equipo e ON tp.equipoid = e.equipoid
        WHERE tp.torneoid = %s AND tp.anioparticipacion = %s
        ORDER BY tp.fase, tp.grupo, tp.pts DESC, tp.dg DESC, tp.gf DESC
    """
    data = execute_query(sql, (torneo_id, anio))
    return jsonify({'data': data})

@app.route('/api/torneos/generar_fixture', methods=['POST'])
def generar_fixture_api():
    data = request.json
    torneo_id = data.get('torneo_id')
    anio = data.get('anio')
    
    if not torneo_id or not anio:
        return jsonify({'success': False, 'message': 'Faltan datos (ID o Año).'})

    try:
        # Construimos la ruta al script 'generar_fixture.py'
        # Asumiendo que está en la carpeta 'database' como en tu estructura anterior
        script_path = os.path.join(DATABASE_DIR, 'generar_fixture.py')
        
        # Ejecutamos el script usando subprocess
        # Pasamos --replace para que borre datos viejos si existen
        result = subprocess.run(
            [sys.executable, script_path, '--torneo', str(torneo_id), '--anio', str(anio), '--replace'],
            capture_output=True,
            text=True
        )

        # Verificamos si el script terminó con éxito (código 0)
        if result.returncode == 0:
            print(f"✅ Fixture generado. Output:\n{result.stdout}")
            return jsonify({'success': True, 'message': 'Fixture generado correctamente.'})
        else:
            print(f"❌ Error en script:\n{result.stderr}")
            # Devolvemos el error que dio el script para poder depurar
            return jsonify({'success': False, 'message': f"Error interno del motor: {result.stderr}"})

    except Exception as e:
        print(f"Excepción en API: {e}")
        return jsonify({'success': False, 'message': str(e)})
# ==========================================

# ==========================================
# Palmarés
#
@app.route('/palmares')
def palmares_view():
    return render_template('palmares.html')

@app.route('/api/palmares/resumen', methods=['GET'])
def palmares_resumen():
    sql_ranking = """
        SELECT e.nombre, e.codigoequipo, COUNT(p.palmaresid) as total_titulos
        FROM palmares p
        JOIN equipo e ON p.equipoid = e.equipoid
        GROUP BY e.nombre, e.codigoequipo
        ORDER BY total_titulos DESC, e.nombre ASC
    """
    ranking = execute_query(sql_ranking)

    sql_historial = """
        SELECT p.aniotitulo, t.nombre as torneo, e.nombre as campeon, 
               t.categoria, e.codigoequipo
        FROM palmares p
        JOIN equipo e ON p.equipoid = e.equipoid
        JOIN torneo t ON p.torneoid = t.torneoid
        ORDER BY p.aniotitulo DESC, t.nombre ASC
    """
    historial = execute_query(sql_historial)

    return jsonify({
        'ranking': ranking,
        'historial': historial
    })
# ==========================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
# ==========================================