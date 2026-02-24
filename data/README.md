# Data Templates and Samples

Esta carpeta contiene archivos de carga masiva de ejemplo o plantillas. Nunca se deben subir dumps gigantes de bases de datos.

## Archivo: `templates/carga_de_datos_masivos.xlsx`

### Propósito
Es el archivo base (`xlsx`) que el sistema procesa para cargar la mayoría de los campeonatos, equipos y ediciones al iniciar el flujo de datos.

### Qué esperar:
- Hojas (sheets) dedicadas a configuraciones como Confedereaciones, Paises, Ligas, etc.
- Este archivo se lee desde algún script interno de carga masiva o desde el endpoint admin.

### Limitaciones:
- Este documento **debe ser pequeño** (menos de 5 MB idealmente).
- Si usas el excel completo con miles de registros de equipos reales, guárdalo fuera del repositorio o configúralo en LFS.

### Flujo recomendado
1. Completar o revisar las columnas en Excel.
2. Ejecutar script de importación /Endpoint de migración.
3. El Backend/Motor mapea el excel a registros insertándolos en la BD.
