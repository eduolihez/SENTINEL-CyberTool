import socket
import threading
from queue import Queue
import requests 
from urllib.parse import urljoin, urlparse 
from bs4 import BeautifulSoup 
from colorama import Fore, Style, init 
import os 
import time

# Inicializar colorama 
init(autoreset=True) 

# --- Códigos de Color ---
INFO = Fore.CYAN + Style.BRIGHT
SUCCESS = Fore.GREEN + Style.BRIGHT
ERROR = Fore.RED + Style.BRIGHT
WARNING = Fore.YELLOW + Style.BRIGHT
HEADER = Fore.MAGENTA + Style.BRIGHT
RESET = Style.RESET_ALL
ACTION = Fore.WHITE + Style.BRIGHT

# --- Utilidades ---

def clear_screen():
    """Limpia la terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- CONFIGURACIÓN Y FUNCIONES DEL PORT SCANNER ---
# (Se mantiene el código del Port Scanner sin cambios funcionales, solo se mejora la estética)

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL", 8080: "Alt-HTTP"
}
q_port = Queue() # Renombrado para evitar conflicto con otras colas
open_ports = []
TIMEOUT = 0.5 
NUM_THREADS = 100

def port_scan(port, target_ip):
    # ... (El cuerpo de la función sigue igual)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        result = s.connect_ex((target_ip, port))
        
        if result == 0:
            open_ports.append(port)
        
        s.close()
    except Exception:
        pass

def worker_port(target_ip): # Renombrado para claridad
    while not q_port.empty():
        port = q_port.get()
        port_scan(port, target_ip)
        q_port.task_done()

def run_port_scanner():
    """Función principal del escáner de puertos."""
    clear_screen()
    print(HEADER + "\n╔═══════════════════════════════════════════════════╗")
    print(HEADER + "║  🛡️ MÓDULO DE ANÁLISIS WEB: PORT SCANNER          ║")
    print(HEADER + "╚═══════════════════════════════════════════════════╝")
    
    target = input(ACTION + "SENTINEL-WEB (PS)> Ingresa IP o Dominio objetivo: " + RESET).strip()
    
    # ... (Lógica de resolución de IP y ejecución de hilos, similar a la versión anterior) ...

    try:
        if not target.startswith(('http://', 'https://')):
            target_ip = socket.gethostbyname(target)
        else:
            domain = urlparse(target).netloc
            target_ip = socket.gethostbyname(domain)
    except socket.gaierror:
        print(ERROR + f"[ERROR] No se pudo resolver el nombre de host: {target}")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return

    print(INFO + f"\n[INFO] Escaneando objetivo: {target} ({target_ip})")
    
    while not q_port.empty(): q_port.get()
    open_ports.clear()
    
    for port in COMMON_PORTS.keys():
        q_port.put(port)

    threads = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=worker_port, args=(target_ip,))
        t.daemon = True 
        t.start()
        threads.append(t)

    q_port.join() 
    
    print(HEADER + "\n╔═══════════════════════════════════════════════════╗")
    print(HEADER + "║         ✅ RESULTADOS DEL ESCANEO                 ║")
    print(HEADER + "╚═══════════════════════════════════════════════════╝")
    
    if open_ports:
        print(SUCCESS + f"[ÉXITO] Se encontraron {len(open_ports)} puertos abiertos:")
        for port in sorted(open_ports):
            service = COMMON_PORTS.get(port, "Servicio Desconocido")
            print(SUCCESS + f"    -> Puerto {port:<5}: {service}")
    else:
        print(WARNING + "[AVISO] No se encontraron puertos comunes abiertos en el objetivo.")

    input(INFO + "\nPresiona [ENTER] para volver al menú de Análisis Web..." + RESET)

# --- CONFIGURACIÓN Y FUNCIONES DEL WEB CRAWLER Y SUBDOMAIN ENUMERATION ---
# (Se mantienen sin cambios funcionales, se mejora la estética en run_web_crawler y run_subdomain_enumeration)

def run_web_crawler():
    clear_screen()
    print(HEADER + "\n╔═══════════════════════════════════════════════════╗")
    print(HEADER + "║  🌐 MÓDULO DE ANÁLISIS WEB: WEB CRAWLER           ║")
    print(HEADER + "╚═══════════════════════════════════════════════════╝")
    # ... (El cuerpo de la función sigue igual) ...
    input(INFO + "\nPresiona [ENTER] para volver al menú de Análisis Web..." + RESET)


def run_subdomain_enumeration():
    clear_screen()
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║  🕵️  MÓDULO DE ANÁLISIS WEB: SUBDOMAIN ENUMERATION           ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")
    # ... (El cuerpo de la función sigue igual) ...
    input(INFO + "\nPresiona [ENTER] para volver al menú de Análisis Web..." + RESET)


# --- NUEVAS FUNCIONALIDADES: DIRECTORY FUZZING Y TECH STACK ---

# Ruta de la wordlist (asume que está en el mismo directorio que SENTINEL.py)
WORDLIST_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dir_wordlist.txt')
q_dir = Queue()
found_dirs = {}
DIR_THREADS = 50

def directory_fuzzer(target_url):
    """Fuzzying de un diccionario de directorios y archivos comunes."""
    while not q_dir.empty():
        path = q_dir.get()
        full_url = urljoin(target_url, path.strip())
        
        try:
            # Petición HEAD es más rápida y menos intensiva
            response = requests.head(full_url, timeout=3, headers={'User-Agent': 'SENTINEL-Fuzzer'})
            
            status = response.status_code
            
            # Códigos interesantes (200=OK, 301/302=Redirección, 403=Prohibido)
            if status in [200, 301, 302, 403]:
                found_dirs[full_url] = status
                print(SUCCESS + f"[ ENCONTRADO ] -> Status {status}: {full_url}")
            # else:
                # print(WARNING + f"[ - ] -> Status {status}: {full_url}") # Opcional: mostrar 404s
            
        except requests.exceptions.RequestException:
            pass # Ignorar errores de conexión/timeout
        except Exception as e:
            # print(ERROR + f"[ERROR] Error inesperado en {full_url}: {e}")
            pass
        
        q_dir.task_done()

def run_directory_fuzzing():
    """Función principal del Directory Fuzzer."""
    clear_screen()
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║  📂 MÓDULO DE ANÁLISIS WEB: FUZZING DE DIRECTORIOS (DIRBUST) ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")
    
    target = input(ACTION + "SENTINEL-WEB (Dir)> Ingresa la URL base (ej: https://ejemplo.com): " + RESET).strip()
    
    if not target.startswith(('http://', 'https://')):
        target = f"http://{target}"
    
    if not os.path.exists(WORDLIST_PATH):
        print(ERROR + f"[ERROR] Archivo de Wordlist no encontrado: {WORDLIST_PATH}")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return

    try:
        with open(WORDLIST_PATH, 'r') as f:
            paths = f.readlines()
    except Exception as e:
        print(ERROR + f"[ERROR] Error al leer wordlist: {e}")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return

    print(INFO + f"\n[INFO] Iniciando fuzzing en: {target}")
    print(INFO + f"[INFO] Usando {len(paths)} rutas desde la wordlist.")

    while not q_dir.empty(): q_dir.get()
    found_dirs.clear()

    for path in paths:
        q_dir.put(path)

    threads = []
    start_time = time.time()
    for _ in range(DIR_THREADS):
        t = threading.Thread(target=directory_fuzzer, args=(target,))
        t.daemon = True
        t.start()
        threads.append(t)
    
    q_dir.join()
    end_time = time.time()

    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║         ✅ RESULTADOS DEL FUZZING                         ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")

    if found_dirs:
        print(SUCCESS + f"[ÉXITO] Se encontraron {len(found_dirs)} rutas interesantes en {end_time - start_time:.2f} segundos.")
    else:
        print(WARNING + "[AVISO] No se encontraron rutas interesantes (código 200, 30x, 403).")

    input(INFO + "\nPresiona [ENTER] para volver al menú de Análisis Web..." + RESET)

def run_tech_analyzer():
    """Analiza headers y scripts para identificar tecnologías."""
    clear_screen()
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║  🧠 MÓDULO DE ANÁLISIS WEB: DETECCIÓN DE TECNOLOGÍA (TECH STACK) ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")

    target = input(ACTION + "SENTINEL-WEB (Tech)> Ingresa la URL objetivo: " + RESET).strip()
    
    if not target.startswith(('http://', 'https://')):
        target = f"http://{target}"

    detected_tech = set()

    try:
        response = requests.get(target, timeout=5, headers={'User-Agent': 'SENTINEL-TechAnalyzer'})
        
        if response.status_code != 200:
            print(WARNING + f"[AVISO] URL inaccesible. Status: {response.status_code}")
        
        # 1. Análisis de Headers
        print(INFO + "\n[INFO] Analizando Encabezados HTTP...")
        headers = response.headers
        
        # Tecnología de servidor/web/hosting
        if 'Server' in headers:
            detected_tech.add(f"Servidor: {headers['Server']}")
        if 'X-Powered-By' in headers:
            detected_tech.add(f"Powered By: {headers['X-Powered-By']}")
        if 'Content-Type' in headers:
            detected_tech.add(f"Content Type: {headers['Content-Type']}")
        if 'Set-Cookie' in headers:
            detected_tech.add("Usa Cookies")
        
        # 2. Análisis del Cuerpo HTML (CMS y Frameworks JS)
        print(INFO + "[INFO] Analizando Cuerpo HTML...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Búsqueda de CMS (WordPress, Joomla, Drupal)
        if soup.find('meta', {'name': 'generator', 'content': 'WordPress'}):
            detected_tech.add("CMS: WordPress")
        if soup.find(text=lambda t: 'Joomla!' in str(t)):
            detected_tech.add("CMS: Joomla")
        if soup.find('link', href=lambda h: 'drupal' in str(h).lower()):
            detected_tech.add("CMS: Drupal")

        # Búsqueda de Frameworks JS (por archivos JS comunes)
        if soup.find('script', src=lambda s: 'vue.' in str(s).lower()):
            detected_tech.add("JS Framework: Vue.js")
        if soup.find('script', src=lambda s: 'react' in str(s).lower()):
            detected_tech.add("JS Framework: React")
        
        # 3. Análisis de Robots.txt y Sitemap (Rutas sensibles)
        print(INFO + "[INFO] Analizando Robots.txt y Sitemap...")
        robots_url = urljoin(target, '/robots.txt')
        sitemap_url = urljoin(target, '/sitemap.xml')

        if requests.get(robots_url, timeout=3).status_code == 200:
            detected_tech.add(f"Ruta: {robots_url} (Existe)")
        if requests.get(sitemap_url, timeout=3).status_code == 200:
            detected_tech.add(f"Ruta: {sitemap_url} (Existe)")

    except requests.exceptions.RequestException as e:
        print(ERROR + f"[ERROR] Falló la conexión: {e}")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return
    except Exception as e:
        print(ERROR + f"[ERROR] Error inesperado: {e}")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return

    # Mostrar Resultados
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║         ✅ INFORME DE TECNOLOGÍA                           ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")
    
    if detected_tech:
        for tech in sorted(list(detected_tech)):
            print(SUCCESS + f"    -> {tech}")
    else:
        print(WARNING + "[AVISO] No se pudo identificar ninguna tecnología obvia.")

    input(INFO + "\nPresiona [ENTER] para volver al menú de Análisis Web..." + RESET)


# --- MENÚ PRINCIPAL DEL MÓDULO WEB ---

def run():
    """Menú principal del módulo de Análisis Web."""
    while True:
        print(INFO + "\n[+] Módulo Análisis Web:")
        print(SUCCESS + "  1 " + RESET + "- Escáner de Puertos (Port Scanner)")
        print(Fore.YELLOW + Style.BRIGHT + "  2 " + RESET + "- Rastreador Web (Web Crawler)")
        print(Fore.BLUE + Style.BRIGHT + "  3 " + RESET + "- Enumeración de Subdominios")
        print(Fore.GREEN + Style.BRIGHT + "  4 " + RESET + "- Fuzzing de Directorios (DirBuster Style) [NUEVO]")
        print(Fore.RED + Style.BRIGHT + "  5 " + RESET + "- Detección de Tecnología (Tech Stack) [NUEVO]")
        print(ERROR + "  9 " + RESET + "- Volver al Menú Principal")
        print("-" * 60)
        
        web_choice = input(ACTION + "SENTINEL-WEB> " + RESET).strip()
        
        if web_choice == '1':
            run_port_scanner()
        elif web_choice == '2':
            run_web_crawler()
        elif web_choice == '3':
            run_subdomain_enumeration()
        elif web_choice == '4':
            run_directory_fuzzing() # NUEVA LLAMADA
        elif web_choice == '5':
            run_tech_analyzer() # NUEVA LLAMADA
        elif web_choice == '9':
            break 
        else:
            print(ERROR + "[ERROR] Opción no válida.")
            input(INFO + "\nPresiona [ENTER] para continuar..." + RESET)
            clear_screen()