# Security Policy

## Supported Versions
Solo la rama `main` (última versión) recibe actualizaciones de seguridad.

## Reporting a Vulnerability

Si encuentras una vulnerabilidad de credenciales expuestas, inyección SQL o similares, por favor **NO ABRAS UN ISSUE PÚBLICO**.
Envía un mensaje privado o correo a los mantenedores principales del repositorio.

Responderemos a los reportes de vulnerabilidades de seguridad en un plazo razonable. 

### Hardcoded Credentials
Está estrictamente prohibido commitear credenciales hardcodeadas (contraseñas, tokens, URLs completas de bases de datos con contraseñas en texto claro). Siempre se deben usar variables de entorno (ej. `.env`). Si por error subes credenciales, estas deben ser rotadas inmediatamente y el historial del repositorio debe ser purgado.
