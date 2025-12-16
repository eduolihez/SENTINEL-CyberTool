import requests
import threading
from queue import Queue
from colorama import Fore, Style, init 
import os
import time
import sys
# Importación para Metadata (Asegúrate de tener 'hachoir-metadata' instalado)
try:
    from hachoir.parser import createParser
    from hachoir.metadata import extractMetadata
    from hachoir.core.tools import humanDuration
    HACHOIR_AVAILABLE = True
except ImportError:
    HACHOIR_AVAILABLE = False
    
# Inicializar colorama 
init(autoreset=True) 

# --- Códigos de Color ---
INFO = Fore.CYAN + Style.BRIGHT
SUCCESS = Fore.GREEN + Style.BRIGHT
ERROR = Fore.RED + Style.BRIGHT
WARNING = Fore.YELLOW + Style.BRIGHT
HEADER = Fore.MAGENTA + Style.BRIGHT
ACTION = Fore.WHITE + Style.BRIGHT 
RESET = Style.RESET_ALL

# --- Utilidades ---

def clear_screen():
    """Limpia la terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- CONFIGURACIÓN Y FUNCIONES DEL USERNAME ENUMERATOR ---

SOCIAL_SITES = {
    "Twitter/X":      "https://x.com/{username}",
    "Instagram":      "https://www.instagram.com/{username}",
    "Reddit":         "https://www.reddit.com/user/{username}",
    "GitHub":         "https://github.com/{username}",
    "TikTok":         "https://www.tiktok.com/@{username}",
    "Pinterest":      "https://www.pinterest.com/{username}"
}
q_user = Queue()
found_profiles = {}
NUM_THREADS = 50

def check_username(platform, url_template, username):
    """Intenta acceder a la URL del perfil y determina si existe."""
    url = url_template.format(username=username)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; SENTINEL-OSINT/1.0)'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            # Filtro básico por contenido para evitar falsos positivos
            if "GitHub" in platform and "wasn't found" in response.text:
                return
            if "Reddit" in platform and "user not found" in response.text.lower():
                return
            if "Instagram" in platform and 'pagina no encontrada' in response.text.lower():
                return
                
            found_profiles[platform] = url
            print(SUCCESS + f"[ENCONTRADO] {platform:<15}: {url}")
            
    except requests.exceptions.RequestException:
        pass

def worker_osint(username):
    """Función para el hilo que toma una plataforma de la cola."""
    while not q_user.empty():
        platform, url_template = q_user.get()
        check_username(platform, url_template, username)
        q_user.task_done()

def run_username_enum():
    """Función principal del Enumerador de Nombres de Usuario."""
    clear_screen()
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║  🕵️  MÓDULO OSINT: ENUMERACIÓN DE USUARIOS (Concurrente)    ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")

    username = input(ACTION + "SENTINEL-OSINT (User)> Ingresa el nombre de usuario a buscar: " + RESET).strip()

    if not username:
        print(ERROR + "[ERROR] El nombre de usuario no puede estar vacío.")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return

    print(INFO + f"\n[INFO] Iniciando búsqueda del usuario '{username}' en {len(SOCIAL_SITES)} plataformas.")
    
    global q_user, found_profiles
    found_profiles.clear()
    while not q_user.empty(): q_user.get()
    
    for platform, url_template in SOCIAL_SITES.items():
        q_user.put((platform, url_template))

    threads = []
    start_time = time.time()
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=worker_osint, args=(username,))
        t.daemon = True 
        t.start()
        threads.append(t)

    q_user.join()
    end_time = time.time()
    
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║         ✅ RESULTADOS FINALES DE BÚSQUEDA                  ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")
    
    if found_profiles:
        print(SUCCESS + f"[ÉXITO] Perfiles encontrados ({len(found_profiles)}) en {end_time - start_time:.2f}s:")
        for platform, url in found_profiles.items():
            print(SUCCESS + f"    -> {platform:<15}: {url}")
    else:
        print(WARNING + "[AVISO] El nombre de usuario no se encontró en las plataformas comunes.")
        
    input(INFO + "\nPresiona [ENTER] para volver al menú OSINT..." + RESET)

# --- NUEVA FUNCIONALIDAD: METADATA ANALYZER ---

def run_metadata_analyzer():
    """Extrae metadatos de un archivo local (PDF, DOCX, JPG, etc.)."""
    clear_screen()
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║  📄 MÓDULO OSINT: ANALIZADOR DE METADATOS (Local File)      ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")

    if not HACHOIR_AVAILABLE:
        print(ERROR + "[ERROR CRÍTICO] La librería 'hachoir-metadata' no está instalada o no se pudo importar.")
        print(WARNING + "Instálala con: pip install hachoir-metadata")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return

    filepath = input(ACTION + "SENTINEL-OSINT (Meta)> Ingresa la ruta al archivo (ej: /home/user/doc.pdf): " + RESET).strip()

    if not os.path.exists(filepath):
        print(ERROR + "[ERROR] Archivo no encontrado. Verifica la ruta.")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return

    parser = createParser(filepath)
    if not parser:
        print(ERROR + "[ERROR] No se pudo parsear el archivo. Formato no soportado.")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return

    try:
        with parser:
            metadata = extractMetadata(parser)

            print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
            print(HEADER + "║         ✅ METADATOS EXTRAÍDOS DE ARCHIVO                  ║")
            print(HEADER + "╚════════════════════════════════════════════════════════════╝")

            if metadata:
                for line in metadata.exportPlaintext(human=False):
                    # Filtramos líneas que no son información útil
                    if ":" in line:
                        key, value = line.split(":", 1)
                        if value.strip() and key.strip().lower() not in ['file', 'mime_type', 'duration']:
                            # Usamos el color de éxito para destacar la información
                            print(SUCCESS + f"    -> {key.strip():<20}: {value.strip()}")
            else:
                print(WARNING + "[AVISO] No se encontraron metadatos extraíbles en este archivo.")

    except Exception as e:
        print(ERROR + f"[ERROR] Ocurrió un error al intentar extraer metadatos: {e}")

    input(INFO + "\nPresiona [ENTER] para volver al menú OSINT..." + RESET)


# --- NUEVA FUNCIONALIDAD: BREACH CHECKER ---

# NOTA: Esta es una implementación pasiva y de ejemplo. Las APIs como HIBP
# requieren una clave de API o son de uso limitado/pago. Usaremos un patrón
# simple de consulta pública (requiere una API key real para ser efectivo).
def run_breach_checker():
    """Consulta servicios públicos para verificar si un correo/usuario ha sido comprometido."""
    clear_screen()
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║  🚨 MÓDULO OSINT: VERIFICADOR DE FUGAS (BREACH CHECK)       ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")

    target = input(ACTION + "SENTINEL-OSINT (Breach)> Ingresa Correo Electrónico o Nombre de Usuario: " + RESET).strip()
    
    if not target:
        print(ERROR + "[ERROR] El campo no puede estar vacío.")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return
        
    print(WARNING + "\n[AVISO] Esta función utiliza un servicio público (ejemplo de patrón). La precisión depende de la API usada.")
    print(INFO + f"[INFO] Verificando la posible exposición de: {target}...")

    # Simulación de consulta a una API (ej: Have I Been Pwned - HIBP)
    # Patrón de consulta para el servicio "Dehashed" (simulado)
    # Si quisieras usar HIBP, la URL es https://api.pwnedpasswords.com/range/SHA1-PREFIX
    
    # URL de ejemplo de API pública (debe ser reemplazada por una API real)
    MOCK_API_URL = "https://mock-breach-api.com/search?q={target}" 
    
    try:
        # Aquí se debería realizar la consulta a un servicio real
        # response = requests.get(MOCK_API_URL.format(target=target), timeout=10)
        # data = response.json() 

        # SIMULACIÓN de respuesta de una API de brechas
        if target.startswith("test@") or "testuser" in target:
            is_pwned = True
            breaches = ["Adobe (2013)", "Collection #1 (2019)"]
        else:
            is_pwned = False
            breaches = []
        
        print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
        print(HEADER + "║         ✅ RESULTADOS DE LA VERIFICACIÓN                   ║")
        print(HEADER + "╚════════════════════════════════════════════════════════════╝")

        if is_pwned:
            print(ERROR + f"[ PELIGRO ] ¡El objetivo '{target}' ha sido encontrado en las siguientes fugas!:")
            for breach in breaches:
                print(ERROR + f"    -> {breach}")
        else:
            print(SUCCESS + f"[ SEGURO ] El objetivo '{target}' no se encontró en las fugas más conocidas.")
            
    except requests.exceptions.RequestException:
        print(ERROR + "[ERROR] Falló la conexión al servicio de verificación de fugas.")
    except Exception as e:
        print(ERROR + f"[ERROR] Error inesperado en la verificación: {e}")

    input(INFO + "\nPresiona [ENTER] para volver al menú OSINT..." + RESET)


# --- MENÚ PRINCIPAL DEL MÓDULO OSINT (MEJORADO) ---

def run():
    """Menú principal del módulo OSINT."""
    while True:
        clear_screen()
        print(HEADER + "╔════════════════════════════════════════════════════════════╗")
        print(HEADER + "║               MÓDULO OSINT (Recolección de Inteligencia)   ║")
        print(HEADER + "╚════════════════════════════════════════════════════════════╝")
        
        print(INFO + "\n[ 🕵️ HERRAMIENTAS DE INTELIGENCIA DE FUENTE ABIERTA ]")
        print(SUCCESS + "  1 " + RESET + "- 👤 Enumeración de Nombres de Usuario (Social Media)")
        
        if HACHOIR_AVAILABLE:
            print(Fore.YELLOW + Style.BRIGHT + "  2 " + RESET + "- 📄 Analizador de Metadatos de Archivos (Local)")
        else:
             print(ERROR + "  2 " + RESET + "- 📄 Analizador de Metadatos [REQUIERE 'hachoir']")
             
        print(Fore.BLUE + Style.BRIGHT + "  3 " + RESET + "- 🚨 Verificador de Fugas (Breach Check - Simulación)")
        print(ERROR + "  9 " + RESET + "- Volver al Menú Principal")
        print("-" * 60)
        
        osint_choice = input(ACTION + "SENTINEL-OSINT> " + RESET).strip()
        
        if osint_choice == '1':
            run_username_enum()
        elif osint_choice == '2':
            run_metadata_analyzer()
        elif osint_choice == '3':
            run_breach_checker()
        elif osint_choice == '9':
            break 
        else:
            print(ERROR + "[ERROR] Opción no válida.")
            input(INFO + "\nPresiona [ENTER] para continuar..." + RESET)