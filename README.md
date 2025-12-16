#🛡️ SENTINEL: Superherramienta Modular de Ciberseguridad

**SENTINEL** es una *suite* modular y avanzada para **Ciberseguridad**, unificando herramientas de **Análisis Web, OSINT y un *Toolkit*** esencial para profesionales de seguridad, *hackers* éticos y equipos de red team. Está diseñada para ser un punto de control centralizado en las fases de Reconocimiento y Evaluación de un objetivo.

---

## 🚀 Instalación y RequisitosSENTINEL está construido en Python 3.

### 1. Clonar el Repositorio

```bash
git clone https://github.com/SENTINEL-CyberTool/SENTINEL-CyberTool.git
cd SENTINEL-CyberTool

```

### 2. Instalación de Dependencias
Se requieren las siguientes librerías: `colorama`, `requests`, `beautifulsoup4`, y `hachoir-metadata`.

```bash
# Recomendado: crear y activar un entorno virtual
python3 -m venv venv
source venv/bin/activate 

# Instalar librerías
pip install colorama requests beautifulsoup4 hachoir-metadata

```

### 3. Crear Wordlists (Necesario)
Para que el Fuzzing de Directorios funcione, debes crear el archivo `dir_wordlist.txt` en la carpeta principal de `SENTINEL-CyberTool/` con una lista de rutas comunes (como `/admin`, `/login`, etc.).

### 4. Ejecutar SENTINEL
```bash
python3 SENTINEL.py
```

---

## 📋 Estructura de Módulos y Funcionalidades
SENTINEL se organiza en tres módulos principales, accesibles desde el menú interactivo.

### 1. ⚡ Módulo de Análisis Web (`web_analysis.py`)
Herramientas para el reconocimiento activo y pasivo de la infraestructura web y de red.

| Opción | Herramienta | Descripción |
| --- | --- | --- |
| **1** | Escáner de Puertos | Identifica puertos TCP comunes abiertos (80, 443, 22, etc.). |
| **2** | Rastreador Web (Crawler) | Mapea la estructura de un sitio web, con control de profundidad y filtro por tipo de archivo. |
| **3** | Enumeración de Subdominios | Descubre subdominios consultando servicios OSINT pasivos (Certificados SSL) y *bruteforcing* básico de DNS. |
| **4** | Fuzzing de Directorios | Utiliza una *wordlist* (`dir_wordlist.txt`) para buscar archivos y directorios ocultos o sensibles. |
| **5** | Detección de Tecnología | Analiza encabezados y código HTML para identificar el *Tech Stack* (Servidor, CMS, Frameworks JS). |
| **6** | Analizador de Seguridad | Evalúa la presencia de encabezados HTTP de seguridad cruciales (CSP, HSTS, X-Frame-Options, etc.). |

### 2. 🔎 Módulo OSINT (`osint_collector.py`)
Herramientas enfocadas en la recolección de inteligencia a partir de fuentes de información abiertas.

| Opción | Herramienta | Descripción |
| --- | --- | --- |
| **1** | Enumeración de Usuarios | Busca la existencia de un nombre de usuario dado en más de 10 plataformas de redes sociales populares. |
| **2** | Analizador de Metadatos | **(Requiere hachoir-metadata)** Extrae datos sensibles (autor, software, ubicación) de archivos locales (PDF, DOCX, JPG). |
| **3** | Verificador de Fugas | Consulta (simulada) bases de datos de fugas conocidas para verificar si un correo electrónico o usuario ha sido comprometido. |

### 3. 🔧 Módulo Toolkit (`toolkit_utils.py`)
Utilidades esenciales para el día a día de un *pentester* o analista.

| Opción | Herramienta | Descripción |
| --- | --- | --- |
| **1** | Generador de Hashes | Calcula y verifica *checksums* de archivos grandes usando algoritmos como MD5, SHA1 y SHA256. |
| **2** | Codificador/Decodificador Base64 | Herramienta simple para manipular cadenas codificadas en Base64. |
| **3** | Generador de Reverse Shells | Genera comandos listos para usar en diferentes lenguajes (Bash, Python, Netcat) especificando LHOST y LPORT. |

---

¡Por supuesto! Añadir hipervínculos a los créditos es esencial para que la gente pueda encontrar fácilmente el trabajo y las plataformas de **Edu Olivares**.

Aquí tienes el bloque de créditos actualizado con los enlaces activos en formato Markdown, listo para copiar y pegar en tu `README.md`.

---

## 👨‍💻 Créditos y Autoría
**SENTINEL** fue concebido y desarrollado por **Edu Olivares**. Su visión fue crear una herramienta unificada y modular para simplificar las tareas de reconocimiento y análisis en ciberseguridad.

Puedes conectar y seguir el trabajo de **Edu Olivares** en las siguientes plataformas:

| Plataforma | Enlace |
| --- | --- |
| **GitHub** | **[@eduolihez](https://www.google.com/search?q=https://github.com/eduolihez)** |
| **Instagram** | **[@eduolihez](https://www.google.com/search?q=https://www.instagram.com/eduolihez)** |
| **LinkedIn** | **[Edu Olivares](https://www.google.com/search?q=https://www.linkedin.com/in/eduolihez)** |
| **YouTube** | **[@eduolihez](https://www.google.com/search?q=https://www.youtube.com/%40eduolihez)** |

---

## 📄 LicenciaEste proyecto está bajo la Licencia **MIT**. Consulta el archivo `LICENSE` para más detalles.