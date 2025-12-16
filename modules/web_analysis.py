import socket
import threading
from queue import Queue
import requests 
from urllib.parse import urljoin, urlparse 
from bs4 import BeautifulSoup 
from colorama import Fore, Style, init 
import os # Necesario para la limpieza de pantalla
import time # Para pausas en el escaneo

# Inicializar colorama 
init(autoreset=True) 

# --- Códigos de Color ---
INFO = Fore.CYAN + Style.BRIGHT
SUCCESS = Fore.GREEN + Style.BRIGHT
ERROR = Fore.RED + Style.BRIGHT
WARNING = Fore.YELLOW + Style.BRIGHT
HEADER = Fore.MAGENTA + Style.BRIGHT
RESET = Style.RESET_ALL

# --- Funciones de Utilidad ---

def clear_screen():
    """Limpia la terminal (funciona en Windows, Linux y macOS)."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- CONFIGURACIÓN Y FUNCIONES DEL PORT SCANNER ---

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 139: "NetBIOS", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 8080: "HTTP Proxy/Alt"
}
q = Queue()
open_ports = []
TIMEOUT = 0.5 
NUM_THREADS = 100

def port_scan(port, target_ip):
    # ... (Funciones port_scan, worker y run_port_scanner son iguales) ...
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        result = s.connect_ex((target_ip, port))
        
        if result == 0:
            open_ports.append(port)
        
        s.close()
    except Exception:
        pass

def worker(target_ip):
    while not q.empty():
        port = q.get()
        port_scan(port, target_ip)
        q.task_done()

def run_port_scanner():
    """Función principal del escáner de puertos."""
    clear_screen()
    print(HEADER + "\n" + "="*50)
    print(HEADER + "      🛡️  MÓDULO DE ANÁLISIS WEB: PORT SCANNER")
    print(HEADER + "="*50)
    
    target = input(INFO + "SENTINEL-WEB (PS)> Ingresa IP o Dominio objetivo: " + RESET).strip()
    
    try:
        if not target.startswith(('http://', 'https://')):
            target_ip = socket.gethostbyname(target)
        else:
            domain = urlparse(target).netloc
            target_ip = socket.gethostbyname(domain)
    except socket.gaierror:
        print(ERROR + f"[ERROR] No se pudo resolver el nombre de host: {target}")
        input(INFO + "\nPresiona Enter para volver..." + RESET)
        return

    print(INFO + f"\n[INFO] Escaneando objetivo: {target} ({target_ip})")
    
    # Limpiar cola y lista de puertos antes de escanear
    while not q.empty(): q.get()
    open_ports.clear()
    
    for port in COMMON_PORTS.keys():
        q.put(port)

    threads = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=worker, args=(target_ip,))
        t.daemon = True 
        t.start()
        threads.append(t)

    q.join() 
    
    print(HEADER + "\n" + "="*50)
    print(HEADER + "         ✅ RESULTADOS DEL ESCANEO")
    print(HEADER + "="*50)
    
    if open_ports:
        print(SUCCESS + f"[ÉXITO] Se encontraron {len(open_ports)} puertos abiertos:")
        for port in sorted(open_ports):
            service = COMMON_PORTS.get(port, "Servicio Desconocido")
            print(SUCCESS + f"    - Puerto {port:<5}: {service}")
    else:
        print(WARNING + "[AVISO] No se encontraron puertos comunes abiertos en el objetivo.")

    input(INFO + "\nPresiona Enter para volver al menú de Análisis Web..." + RESET)

# --- CONFIGURACIÓN Y FUNCIONES DEL WEB CRAWLER ---

crawled_links = set() 
internal_links = set()
external_links = set()
MAX_LINKS = 50 

def crawl(url, target_domain):
    """Rastrea recursivamente una URL para encontrar enlaces."""
    # Control de límite y duplicados
    if url in crawled_links or len(crawled_links) >= MAX_LINKS:
        return

    try:
        if not url.startswith(('http://', 'https://')):
            url = f"http://{url}"

        # Usamos un user-agent común para evitar bloqueos básicos
        response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0 (compatible; SENTINEL-Crawler/1.0)'})
        
        # Solo seguir enlaces si el código de estado es OK
        if response.status_code not in [200, 301, 302]:
            return

        crawled_links.add(url)
        print(f"{INFO}[CRAWL {len(crawled_links)}/{MAX_LINKS}]{RESET} -> {url}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for link_tag in soup.find_all('a', href=True):
            href = link_tag.get('href')
            if href:
                full_url = urljoin(url, href) 
                parsed_url = urlparse(full_url)
                
                # Excluir enlaces de fragmentos (#), javascript y correos
                if parsed_url.fragment or parsed_url.scheme in ('mailto', 'tel', 'javascript'):
                    continue

                clean_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
                
                # Clasificar enlaces
                if parsed_url.netloc == target_domain and clean_url not in internal_links and clean_url not in crawled_links:
                    internal_links.add(clean_url)
                    # Recursividad: continuar rastreando si no hemos alcanzado el límite
                    if len(crawled_links) < MAX_LINKS:
                        crawl(clean_url, target_domain)

                elif parsed_url.netloc != target_domain and parsed_url.netloc != "":
                    external_links.add(parsed_url.netloc)
                        
    except requests.exceptions.RequestException as e:
        # print(f"{WARNING}[WARNING] Error de conexión o timeout en {url}")
        pass
    except Exception as e:
        # print(f"{ERROR}[ERROR] Error inesperado en el crawler: {e}")
        pass

def run_web_crawler():
    """Función principal del Web Crawler."""
    clear_screen()
    print(HEADER + "\n" + "="*50)
    print(HEADER + "      🌐 MÓDULO DE ANÁLISIS WEB: WEB CRAWLER")
    print(HEADER + "="*50)
    
    start_url = input(INFO + "SENTINEL-WEB (WC)> Ingresa la URL inicial (ej: https://ejemplo.com): " + RESET).strip()
    
    if not start_url.startswith(('http://', 'https://')):
        start_url = f"http://{start_url}"

    try:
        target_domain = urlparse(start_url).netloc
    except Exception:
        print(ERROR + "[ERROR] URL inválida.")
        input(INFO + "\nPresiona Enter para volver..." + RESET)
        return

    print(INFO + f"\n[INFO] Iniciando rastreo en: {start_url}")
    
    crawled_links.clear()
    internal_links.clear()
    external_links.clear()

    crawl(start_url, target_domain)
    
    # Mostrar Resultados
    print(HEADER + "\n" + "="*50)
    print(HEADER + "         ✅ RESULTADOS DEL RASTREO")
    print(HEADER + "="*50)

    print(SUCCESS + f"\n[RESUMEN] Se rastrearon {len(crawled_links)} URLs.")
    
    print(INFO + "\n[INTERNOS] Enlaces internos descubiertos:")
    if internal_links:
        for link in sorted(list(internal_links)):
            print(f"    -> {link}")
    else:
        print(WARNING + "    -> No se encontraron enlaces internos únicos adicionales.")

    print(INFO + "\n[EXTERNOS] Dominios externos referenciados:")
    if external_links:
        for domain in sorted(list(external_links)):
            print(f"    -> {domain}")
    else:
        print(WARNING + "    -> No se encontraron referencias a dominios externos.")

    input(INFO + "\nPresiona Enter para volver al menú de Análisis Web..." + RESET)


# --- CONFIGURACIÓN Y FUNCIONES DE SUBDOMAIN ENUMERATION (NUEVO) ---

# URL de la API de Crt.sh (OSINT pasivo) y lista de subdominios
CRT_SH_URL = "https://crt.sh/?q=%25.{target}&output=json"
found_subdomains = set()

def run_subdomain_enumeration():
    """Busca subdominios utilizando fuentes de OSINT pasivas (Crt.sh)."""
    clear_screen()
    print(HEADER + "\n" + "="*60)
    print(HEADER + "      🕵️  MÓDULO DE ANÁLISIS WEB: SUBDOMAIN ENUMERATION")
    print(HEADER + "="*60)

    target_domain = input(INFO + "SENTINEL-WEB (SD)> Ingresa el Dominio objetivo (ej: google.com): " + RESET).strip()

    if not target_domain:
        print(ERROR + "[ERROR] El dominio no puede estar vacío.")
        input(INFO + "\nPresiona Enter para volver..." + RESET)
        return

    print(INFO + f"\n[INFO] Iniciando enumeración pasiva para: {target_domain}")
    found_subdomains.clear()

    try:
        # 1. Consulta Crt.sh para certificados SSL
        print(INFO + "[INFO] Consultando Crt.sh (Certificados SSL)...")
        crt_url = CRT_SH_URL.format(target=target_domain)
        response = requests.get(crt_url, timeout=10)
        
        if response.status_code == 200 and response.json():
            data = response.json()
            for entry in data:
                # El campo 'name_value' a menudo contiene múltiples subdominios separados por salto de línea
                subdomains_raw = entry.get('name_value', '').split('\n')
                
                for sub in subdomains_raw:
                    sub = sub.strip().lower()
                    # Filtra y añade solo subdominios que terminen en el dominio objetivo
                    if sub.endswith(target_domain) and not sub.startswith('*'):
                        found_subdomains.add(sub)
            print(SUCCESS + f"[ÉXITO] Se encontraron {len(found_subdomains)} posibles subdominios en Crt.sh.")
        else:
            print(WARNING + "[AVISO] Crt.sh no devolvió datos o hubo un error en la solicitud.")
        
        # 2. Muestra los resultados finales
        print(HEADER + "\n" + "="*60)
        print(HEADER + "         ✅ RESULTADOS FINALES DE SUBDOMINIOS")
        print(HEADER + "="*60)

        if found_subdomains:
            sorted_subs = sorted(list(found_subdomains))
            print(SUCCESS + f"[RESUMEN] Se encontraron {len(sorted_subs)} subdominios únicos para {target_domain}:")
            for sub in sorted_subs:
                print(f"    -> {sub}")
        else:
            print(WARNING + f"[AVISO] No se encontraron subdominios únicos para {target_domain} mediante OSINT pasivo.")

    except requests.exceptions.RequestException as e:
        print(ERROR + f"[ERROR CRÍTICO] Error de conexión al servicio de OSINT: {e}")
    except Exception as e:
        print(ERROR + f"[ERROR CRÍTICO] Error inesperado: {e}")

    input(INFO + "\nPresiona Enter para volver al menú de Análisis Web..." + RESET)


# --- MENÚ PRINCIPAL DEL MÓDULO WEB ---

def run():
    """Menú principal del módulo de Análisis Web."""
    while True:
        # No limpiamos aquí. SENTINEL.py limpia ANTES de llamar a run()
        print(INFO + "\n[+] Módulo Análisis Web:")
        print(SUCCESS + "  1 " + RESET + "- Escáner de Puertos (Port Scanner)")
        print(Fore.YELLOW + Style.BRIGHT + "  2 " + RESET + "- Rastreador Web (Web Crawler)")
        print(Fore.BLUE + Style.BRIGHT + "  3 " + RESET + "- Enumeración de Subdominios (Subdomain Enumeration)")
        print(ERROR + "  9 " + RESET + "- Volver al Menú Principal")
        print("-" * 50)
        
        web_choice = input(INFO + "SENTINEL-WEB> " + RESET).strip()
        
        if web_choice == '1':
            run_port_scanner()
        elif web_choice == '2':
            run_web_crawler()
        elif web_choice == '3':
            run_subdomain_enumeration() # NUEVA FUNCIONALIDAD
        elif web_choice == '9':
            break # Salir del bucle y volver al main de SENTINEL.py
        else:
            print(ERROR + "[ERROR] Opción no válida.")
            input(INFO + "\nPresiona Enter para continuar..." + RESET)
            clear_screen()

if __name__ == '__main__':
    run()