import requests
import threading
from queue import Queue
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

# --- Utilidades ---

def clear_screen():
    """Limpia la terminal (funciona en Windows, Linux y macOS)."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- CONFIGURACIÓN Y FUNCIONES DEL USERNAME ENUMERATOR ---

# Lista de plataformas a escanear (puedes expandir esta lista)
# Formato: {Nombre de la Plataforma: URL de Perfil con placeholder {username}}
SOCIAL_SITES = {
    "Twitter/X":      "https://x.com/{username}",
    "Instagram":      "https://www.instagram.com/{username}",
    "Facebook":       "https://www.facebook.com/{username}",
    "Reddit":         "https://www.reddit.com/user/{username}",
    "GitHub":         "https://github.com/{username}",
    "LinkedIn (Pub)": "https://www.linkedin.com/in/{username}",
    "Pinterest":      "https://www.pinterest.com/{username}",
    "TikTok":         "https://www.tiktok.com/@{username}",
    "YouTube":        "https://www.youtube.com/@{username}"
}

# Cola para manejar las plataformas a escanear
q = Queue()
found_profiles = {} # {Plataforma: URL}
NUM_THREADS = 50

def check_username(platform, url_template, username):
    """
    Intenta acceder a la URL del perfil y determina si existe.
    La lógica de detección varía según la plataforma (código de estado o contenido).
    """
    url = url_template.format(username=username)
    
    try:
        # Usar un User-Agent común para simular un navegador
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=5)
        
        # Lógica de detección:
        # 1. La mayoría de sitios devuelven 200 (OK) si existe y 404 si no.
        # 2. Algunos sitios (como Twitter/X) devuelven 200 incluso para un perfil no existente,
        #    pero con contenido que indica que no se encontró (requiere análisis de contenido).
        
        if response.status_code == 200:
            # Comprobación de contenido específica para GitHub
            if "GitHub" in platform and "wasn't found" in response.text:
                return
            
            # Comprobación de contenido específica para Reddit (puede requerir más ajustes)
            if "Reddit" in platform and "user not found" in response.text.lower():
                return

            # Si el código es 200 (OK) y no se filtra por contenido, asumimos que existe
            found_profiles[platform] = url
            print(SUCCESS + f"[ENCONTRADO] {platform:<15}: {url}")
            
        elif response.status_code == 404 or response.status_code == 410:
            # 404 (Not Found) o 410 (Gone) generalmente significa que no existe
            # print(WARNING + f"[NO ENCONTRADO] {platform:<15}")
            pass
            
        else:
            # Otros códigos como 403 (Forbidden) o 500 (Server Error)
            print(WARNING + f"[AVISO] {platform:<15}: Código {response.status_code}. Revisión manual necesaria.")

    except requests.exceptions.RequestException:
        # Error de conexión, timeout, etc.
        # print(ERROR + f"[ERROR] {platform:<15}: Falló la conexión/timeout.")
        pass
    except Exception as e:
        # Otros errores
        # print(ERROR + f"[ERROR] {platform:<15}: Error inesperado: {e}")
        pass

def worker_osint(username):
    """Función para el hilo que toma una plataforma de la cola y la escanea."""
    while not q.empty():
        platform, url_template = q.get()
        check_username(platform, url_template, username)
        q.task_done()

def run_username_enum():
    """Función principal del Enumerador de Nombres de Usuario."""
    clear_screen()
    print(HEADER + "\n" + "="*60)
    print(HEADER + "      🕵️  MÓDULO OSINT: ENUMERACIÓN DE USUARIOS")
    print(HEADER + "="*60)

    username = input(INFO + "SENTINEL-OSINT (User)> Ingresa el nombre de usuario a buscar: " + RESET).strip()

    if not username:
        print(ERROR + "[ERROR] El nombre de usuario no puede estar vacío.")
        input(INFO + "\nPresiona Enter para volver..." + RESET)
        return

    print(INFO + f"\n[INFO] Iniciando búsqueda del usuario '{username}' en {len(SOCIAL_SITES)} plataformas.")
    
    # 1. Limpiar variables y llenar la cola
    found_profiles.clear()
    while not q.empty(): q.get()
    
    for platform, url_template in SOCIAL_SITES.items():
        q.put((platform, url_template))

    # 2. Crear y ejecutar los hilos de trabajo
    threads = []
    start_time = time.time()
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=worker_osint, args=(username,))
        t.daemon = True 
        t.start()
        threads.append(t)

    # 3. Esperar a que todos los hilos terminen
    q.join()
    end_time = time.time()
    
    # 4. Mostrar resultados
    print(HEADER + "\n" + "="*60)
    print(HEADER + "         ✅ RESULTADOS FINALES DE BÚSQUEDA")
    print(HEADER + "="*60)
    
    if found_profiles:
        print(SUCCESS + f"[ÉXITO] Perfiles encontrados ({len(found_profiles)}):")
        for platform, url in found_profiles.items():
            print(f"    - {platform:<15}: {url}")
    else:
        print(WARNING + "[AVISO] El nombre de usuario no se encontró en las plataformas comunes.")
        
    print(INFO + f"\n[TIEMPO] Búsqueda completada en {end_time - start_time:.2f} segundos.")

    input(INFO + "\nPresiona Enter para volver al menú OSINT..." + RESET)

# --- MENÚ PRINCIPAL DEL MÓDULO OSINT ---

def run():
    """Menú principal del módulo OSINT."""
    while True:
        # No limpiamos aquí. SENTINEL.py limpia ANTES de llamar a run()
        print(INFO + "\n[+] Módulo OSINT - Recolección de Inteligencia:")
        print(SUCCESS + "  1 " + RESET + "- Enumeración de Nombres de Usuario (Username Enumeration)")
        print(WARNING + "  2 " + RESET + "- Análisis de Metadatos de Archivos (Futuro)")
        print(ERROR + "  9 " + RESET + "- Volver al Menú Principal")
        print("-" * 50)
        
        osint_choice = input(INFO + "SENTINEL-OSINT> " + RESET).strip()
        
        if osint_choice == '1':
            run_username_enum()
        elif osint_choice == '2':
            print(WARNING + "[INFO] La funcionalidad de Análisis de Metadatos está en desarrollo.")
        elif osint_choice == '9':
            break 
        else:
            print(ERROR + "[ERROR] Opción no válida.")
            input(INFO + "\nPresiona Enter para continuar..." + RESET)
            clear_screen()

if __name__ == '__main__':
    run()