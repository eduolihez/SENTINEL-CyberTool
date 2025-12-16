import os
import hashlib
from colorama import Fore, Style, init

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
    """Limpia la terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- CONFIGURACIÓN Y FUNCIONES DE HASHING ---

def calculate_file_hash(filepath, algorithm):
    """Calcula el hash de un archivo grande."""
    try:
        # Crea el objeto hash (md5, sha1, sha256, etc.)
        hasher = hashlib.new(algorithm)
    except ValueError:
        return f"[ERROR] Algoritmo de hash no soportado: {algorithm}"

    try:
        # Abrir el archivo en modo binario
        with open(filepath, 'rb') as file:
            # Leer en bloques para manejar archivos grandes
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
    print(HEADER + "\n" + "="*50)
    print(HEADER + "      ⚙️  MÓDULO TOOLKIT: GENERADOR DE HASHES")
    print(HEADER + "="*50)

    filepath = input(INFO + "SENTINEL-TOOLKIT (Hash)> Ingresa la ruta del archivo: " + RESET).strip()
    
    # Lista de algoritmos comunes
    algorithms = ['md5', 'sha1', 'sha256', 'sha512']
    
    print(INFO + "\n[INFO] Calculando hashes...")
    
    # Calculamos y mostramos los hashes para cada algoritmo
    for algo in algorithms:
        print(INFO + f"[CALCULANDO] Algoritmo: {algo.upper()}...")
        hash_value = calculate_file_hash(filepath, algo)
        
        if hash_value.startswith("[ERROR]"):
            # Si hay un error, lo imprimimos y rompemos el bucle
            print(ERROR + hash_value)
            break
        else:
            print(SUCCESS + f"    -> {algo.upper():<7}: {hash_value}")

    input(INFO + "\nPresiona Enter para volver al menú Toolkit..." + RESET)

# --- MENÚ PRINCIPAL DEL MÓDULO TOOLKIT ---

def run():
    """Menú principal del módulo Toolkit."""
    while True:
        print(INFO + "\n[+] Módulo Toolkit - Utilidades:")
        print(SUCCESS + "  1 " + RESET + "- Generador de Hashes (MD5, SHA256, etc.)")
        print(WARNING + "  2 " + RESET + "- Codificador/Decodificador Base64 (Futuro)")
        print(ERROR + "  9 " + RESET + "- Volver al Menú Principal")
        print("-" * 50)
        
        toolkit_choice = input(INFO + "SENTINEL-TOOLKIT> " + RESET).strip()
        
        if toolkit_choice == '1':
            run_hash_generator()
        elif toolkit_choice == '2':
            print(WARNING + "[INFO] El Codificador/Decodificador Base64 está en desarrollo.")
        elif toolkit_choice == '9':
            break 
        else:
            print(ERROR + "[ERROR] Opción no válida.")
            input(INFO + "\nPresiona Enter para continuar..." + RESET)
            clear_screen()

if __name__ == '__main__':
    run()