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
ACTION = Fore.WHITE + Style.BRIGHT 
RESET = Style.RESET_ALL

# --- Utilidades ---

def clear_screen():
    """Limpia la terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- CONFIGURACIÓN GLOBAL ---

COMMON_PORTS = {80: "HTTP", 443: "HTTPS", 21: "FTP", 22: "SSH", 3306: "MySQL"}
TIMEOUT = 0.5 
NUM_THREADS = 100
DIR_THREADS = 50 # Concurrencia para Directory Fuzzing
WORDLIST_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dir_wordlist.txt')
SUBDOMAIN_WORDLIST = ['www', 'dev', 'test', 'admin', 'api', 'blog', 'mail', 'ftp', 'webmail', 'panel']

# --- PORT SCANNER UTILITIES ---

q_port = Queue()
open_ports = []

def port_scan(port, target_ip):
    """Función de escaneo de puerto única."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        result = s.connect_ex((target_ip, port))
        
        if result == 0:
            open_ports.append(port)
        
        s.close()
    except Exception:
        pass

def worker_port(target_ip):
    """Manejador de hilos para el escaneo de puertos."""
    while not q_port.empty():
        port = q_port.get()
        port_scan(port, target_ip)
        q_port.task_done()

# --- WEB CRAWLER UTILITIES ---

crawled_links = set()
internal_links = set()
external_links = set()
target_extensions = []

def crawl(url, target_domain, max_depth, current_depth=0):
    """Rastrea recursivamente una URL con control de profundidad y extensión."""
    if url in crawled_links or current_depth > max_depth or len(crawled_links) >= 150: # Límite de 150 enlaces
        return

    try:
        # Asegura el esquema
        if not url.startswith(('http://', 'https://')): url = f"http://{url}"
        
        response = requests.get(url, timeout=5, headers={'User-Agent': 'SENTINEL-Crawler'})
        
        if response.status_code not in [200, 301, 302]: return

        crawled_links.add(url)
        print(f"{INFO}[DEPTH {current_depth}][CRAWLED {len(crawled_links)}]{RESET} -> {url}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for link_tag in soup.find_all('a', href=True):
            href = link_tag.get('href')
            if href:
                full_url = urljoin(url, href) 
                parsed_url = urlparse(full_url)
                clean_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
                
                is_internal = parsed_url.netloc == target_domain
                
                if is_internal and clean_url not in internal_links and clean_url not in crawled_links:
                    
                    if target_extensions and not any(clean_url.endswith(ext) for ext in target_extensions):
                        continue 

                    internal_links.add(clean_url)
                    crawl(clean_url, target_domain, max_depth, current_depth + 1)

                elif parsed_url.netloc != target_domain and parsed_url.netloc != "":
                    external_links.add(parsed_url.netloc)
                        
    except requests.exceptions.RequestException:
        pass
    except Exception:
        pass

# --- DIRECTORY FUZZING UTILITIES ---

q_dir = Queue()
found_dirs = {}

def directory_fuzzer(target_url):
    """Fuzzying de un diccionario de directorios y archivos comunes."""
    while not q_dir.empty():
        path = q_dir.get()
        full_url = urljoin(target_url, path.strip())
        
        try:
            # Petición HEAD es más rápida y menos intensiva
            response = requests.head(full_url, timeout=3, headers={'User-Agent': 'SENTINEL-Fuzzer'})
            
            status = response.status_code
            
            if status in [200, 301, 302, 403]:
                found_dirs[full_url] = status
                print(SUCCESS + f"[ ENCONTRADO ] -> Status {status}: {full_url}")
            
        except requests.exceptions.RequestException:
            pass 
        except Exception:
            pass
        
        q_dir.task_done()

# --- SUBDOMAIN ENUMERATION UTILITIES ---

found_subdomains = []
q_sub = Queue()

def subdomain_resolver(domain):
    """Intenta resolver subdominios."""
    while not q_sub.empty():
        subdomain = q_sub.get()
        full_domain = f"{subdomain}.{domain}"
        
        try:
            ip = socket.gethostbyname(full_domain)
            found_subdomains.append((full_domain, ip))
            print(SUCCESS + f"[ ENCONTRADO ] -> {full_domain} ({ip})")
        except socket.gaierror:
            pass # No existe
        except Exception:
            pass
        
        q_sub.task_done()

# --- IMPLEMENTACIÓN DE LOS MENÚS (RUN_FUNCTIONS) ---

def run_port_scanner():
    """Función principal del escáner de puertos."""
    clear_screen()
    print(HEADER + "\n╔═══════════════════════════════════════════════════╗")
    print(HEADER + "║  🛡️ MÓDULO DE ANÁLISIS WEB: ESCÁNER DE PUERTOS    ║")
    print(HEADER + "╚═══════════════════════════════════════════════════╝")
    
    target = input(ACTION + "SENTINEL-WEB (PS)> Ingresa IP o Dominio objetivo: " + RESET).strip()
    
    try:
        # Intenta obtener la IP incluso si se da un dominio con esquema
        domain_or_ip = urlparse(target).netloc if target.startswith(('http://', 'https://')) else target
        target_ip = socket.gethostbyname(domain_or_ip)
    except socket.gaierror:
        print(ERROR + f"[ERROR] No se pudo resolver el nombre de host: {target}")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return

    print(INFO + f"\n[INFO] Escaneando objetivo: {target} ({target_ip})")
    
    global q_port, open_ports
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
        print(WARNING + "[AVISO] No se encontraron puertos comunes abiertos.")

    input(INFO + "\nPresiona [ENTER] para volver al menú de Análisis Web..." + RESET)

def run_web_crawler():
    """Función principal del Web Crawler."""
    clear_screen()
    print(HEADER + "\n╔═══════════════════════════════════════════════════╗")
    print(HEADER + "║  🌐 MÓDULO DE ANÁLISIS WEB: WEB CRAWLER           ║")
    print(HEADER + "╚═══════════════════════════════════════════════════╝")
    
    start_url = input(ACTION + "SENTINEL-WEB (WC)> Ingresa la URL inicial: " + RESET).strip()
    depth_input = input(ACTION + "SENTINEL-WEB (WC)> Profundidad máxima (ej: 2): " + RESET).strip()
    ext_input = input(ACTION + "SENTINEL-WEB (WC)> Filtrar por extensiones (ej: .js,.pdf, o vacío): " + RESET).strip()
    
    max_depth = int(depth_input) if depth_input.isdigit() else 2
    
    global target_extensions
    target_extensions = [ext.strip() for ext in ext_input.split(',') if ext.strip()]

    if not start_url.startswith(('http://', 'https://')): start_url = f"http://{start_url}"

    try:
        target_domain = urlparse(start_url).netloc
    except Exception:
        print(ERROR + "[ERROR] URL inválida.")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return

    print(INFO + f"\n[INFO] Iniciando rastreo en: {start_url} (Profundidad: {max_depth})")
    
    global crawled_links, internal_links, external_links
    crawled_links.clear(); internal_links.clear(); external_links.clear()

    crawl(start_url, target_domain, max_depth)
    
    print(HEADER + "\n╔═══════════════════════════════════════════════════╗")
    print(HEADER + "║         ✅ RESULTADOS DEL RASTREO                 ║")
    print(HEADER + "╚═══════════════════════════════════════════════════╝")

    print(SUCCESS + f"\n[ INTERNOS ] Se encontraron {len(internal_links)} enlaces internos:")
    for link in internal_links:
        print(f"    -> {link}")
    
    print(WARNING + f"\n[ EXTERNOS ] Se encontraron {len(external_links)} dominios externos:")
    for domain in external_links:
        print(f"    -> {domain}")

    input(INFO + "\nPresiona [ENTER] para volver al menú de Análisis Web..." + RESET)

def run_subdomain_enumeration():
    """Función principal para la enumeración simple de subdominios."""
    clear_screen()
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║  🕵️  MÓDULO DE ANÁLISIS WEB: SUBDOMAIN ENUMERATION           ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")

    target_domain = input(ACTION + "SENTINEL-WEB (Sub)> Ingresa el Dominio raíz (ej: google.com): " + RESET).strip()

    print(INFO + f"\n[INFO] Iniciando enumeración básica en: {target_domain}")
    
    global q_sub, found_subdomains
    while not q_sub.empty(): q_sub.get()
    found_subdomains.clear()

    # Llenar la cola con la wordlist
    for sub in SUBDOMAIN_WORDLIST:
        q_sub.put(sub)

    threads = []
    start_time = time.time()
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=subdomain_resolver, args=(target_domain,))
        t.daemon = True
        t.start()
        threads.append(t)
    
    q_sub.join()
    end_time = time.time()
    
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║         ✅ RESULTADOS DE SUBDOMINIOS                       ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")

    if found_subdomains:
        print(SUCCESS + f"[ÉXITO] Se encontraron {len(found_subdomains)} subdominios en {end_time - start_time:.2f} segundos.")
        for domain, ip in found_subdomains:
            print(SUCCESS + f"    -> {domain:<20} ({ip})")
    else:
        print(WARNING + "[AVISO] No se encontraron subdominios comunes.")

    input(INFO + "\nPresiona [ENTER] para volver al menú de Análisis Web..." + RESET)

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
        print(WARNING + "Asegúrate de haber creado el archivo 'dir_wordlist.txt' en la carpeta principal.")
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

    global q_dir, found_dirs
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
        for url, status in found_dirs.items():
            print(SUCCESS + f"    -> Status {status}: {url}")
    else:
        print(WARNING + "[AVISO] No se encontraron rutas interesantes (código 200, 30x, 403).")

    input(INFO + "\nPresiona [ENTER] para volver al menú de Análisis Web..." + RESET)

def run_tech_analyzer():
    """Analiza headers y scripts para identificar tecnologías (Corregido y Mejorado)."""
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
        headers = response.headers
        
        if 'Server' in headers: detected_tech.add(f"Servidor: {headers['Server']}")
        if 'X-Powered-By' in headers: detected_tech.add(f"Powered By: {headers['X-Powered-By']}")
        if 'Content-Type' in headers: detected_tech.add(f"Content Type: {headers['Content-Type'].split(';')[0]}")
        
        # 2. Análisis del Cuerpo HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Búsqueda de CMS y Frameworks
        if soup.find('meta', {'name': 'generator'}):
             gen = soup.find('meta', {'name': 'generator'}).get('content')
             detected_tech.add(f"Generador (CMS): {gen}")
        if soup.find('script', src=lambda s: 'jquery' in str(s).lower()):
            detected_tech.add("Librería JS: jQuery")
        if soup.find('meta', {'name': 'keywords'}):
            detected_tech.add("Metadatos Keywords detectados")
        
        # 3. Análisis de Robots.txt y Sitemap
        robots_url = urljoin(target, '/robots.txt')
        sitemap_url = urljoin(target, '/sitemap.xml')

        if requests.get(robots_url, timeout=3, headers={'User-Agent': 'SENTINEL'}).status_code == 200:
            detected_tech.add(f"Ruta: {robots_url} (Existe)")
        if requests.get(sitemap_url, timeout=3, headers={'User-Agent': 'SENTINEL'}).status_code == 200:
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

def run_security_headers_analyzer():
    """Analiza la respuesta HTTP en busca de encabezados de seguridad críticos."""
    clear_screen()
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║  🔒 MÓDULO DE ANÁLISIS WEB: ANALIZADOR DE SEGURIDAD (HEADERS) ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")

    target = input(ACTION + "SENTINEL-WEB (Sec)> Ingresa la URL objetivo: " + RESET).strip()
    
    if not target.startswith(('http://', 'https://')):
        target = f"https://{target}" 

    SECURITY_HEADERS = {
        'Content-Security-Policy': 'Crítico (XSS)',
        'X-Content-Type-Options': 'Crítico (MIME-sniffing)',
        'X-Frame-Options': 'Crítico (Clickjacking)',
        'Strict-Transport-Security': 'Alta (Uso forzado de HTTPS)',
        'Referrer-Policy': 'Media (Fuga de información)',
    }

    missing_headers = []
    present_headers = {}

    try:
        response = requests.get(target, timeout=5, allow_redirects=True, headers={'User-Agent': 'SENTINEL-SecurityAnalyzer'})
        headers = response.headers

        # 1. Verificar encabezados críticos
        for header, severity in SECURITY_HEADERS.items():
            if header not in headers:
                missing_headers.append((header, severity))
            else:
                present_headers[header] = headers[header]

    except requests.exceptions.RequestException as e:
        print(ERROR + f"[ERROR] Falló la conexión o timeout: {e}")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return
    except Exception as e:
        print(ERROR + f"[ERROR] Error inesperado: {e}")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return

    # Mostrar Resultados
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║         ✅ INFORME DE ENCABEZADOS DE SEGURIDAD             ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")

    if missing_headers:
        print(ERROR + f"\n[ CRÍTICO ] Faltan {len(missing_headers)} Encabezados de Seguridad Clave:")
        for header, severity in missing_headers:
            print(f"    ❌ {header:<25} -> {severity}")
    else:
        print(SUCCESS + "[ ÉXITO ] Todos los encabezados de seguridad críticos están presentes.")
    
    print(INFO + "\n[ PRESENTE ] Encabezados detectados:")
    for header, value in present_headers.items():
        print(f"    ✔️ {header:<25}: {value}")


    input(INFO + "\nPresiona [ENTER] para volver al menú de Análisis Web..." + RESET)

# --- MENÚ PRINCIPAL DEL MÓDULO WEB ---

def run():
    """Menú principal del módulo de Análisis Web."""
    while True:
        clear_screen()
        print(HEADER + "╔════════════════════════════════════════════════════════════╗")
        print(HEADER + "║               MÓDULO DE ANÁLISIS WEB (6 Herramientas)      ║")
        print(HEADER + "╚════════════════════════════════════════════════════════════╝")
        
        print(INFO + "\n[ 💻 HERRAMIENTAS DE RECONOCIMIENTO Y AUDITORÍA ]")
        print(SUCCESS + "  1 " + RESET + "- 🛡️ Escáner de Puertos")
        print(Fore.YELLOW + Style.BRIGHT + "  2 " + RESET + "- 🌐 Rastreador Web (Crawler)")
        print(Fore.BLUE + Style.BRIGHT + "  3 " + RESET + "- 🕵️ Enumeración de Subdominios (Básica)")
        print(Fore.GREEN + Style.BRIGHT + "  4 " + RESET + "- 📂 Fuzzing de Directorios (DirBuster Style)")
        print(Fore.RED + Style.BRIGHT + "  5 " + RESET + "- 🧠 Detección de Tecnología (Tech Stack)")
        print(Fore.MAGENTA + Style.BRIGHT + "  6 " + RESET + "- 🔒 Analizador de Encabezados de Seguridad")
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
            run_directory_fuzzing()
        elif web_choice == '5':
            run_tech_analyzer()
        elif web_choice == '6':
            run_security_headers_analyzer()
        elif web_choice == '9':
            break 
        else:
            print(ERROR + "[ERROR] Opción no válida.")
            input(INFO + "\nPresiona [ENTER] para continuar..." + RESET)