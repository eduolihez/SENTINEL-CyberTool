import sys
import os
from colorama import init, Fore, Style 

# Inicializa colorama para que funcione en diferentes terminales
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

# --- Configuración de Rutas y Módulos ---
# Añade el directorio 'modules' al path para poder importarlos
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
    
    # Importación de Módulos Funcionales
    from modules import web_analysis 
    from modules import osint_collector
    from modules import toolkit_utils 
    
except ImportError as e:
    clear_screen()
    print(ERROR + f"[ERROR CRÍTICO] No se pudo cargar un módulo necesario: {e}")
    print(WARNING + "Asegúrate de que los archivos 'web_analysis.py', 'osint_collector.py', y 'toolkit_utils.py' existan en la carpeta 'modules/'.")
    sys.exit(1)


# --- Funciones de Interfaz ---

def display_header():
    """Muestra un banner de SENTINEL mejorado con colores."""
    print(HEADER + "=" * 65)
    print(HEADER + "               █▓▒░ S E N T I N E L ░▒▓█")
    print(HEADER + "      Superherramienta Modular de Ciberseguridad Avanzada")
    print(HEADER + "=" * 65)
    print(RESET)

def display_menu():
    """Muestra las opciones principales de SENTINEL con formato de lista."""
    print(INFO + "\n[+] Menú Principal - Selecciona un Módulo:")
    print(SUCCESS + "  1 " + RESET + "- Análisis Web (Escaneo, Crawling, Subdominios)")
    print(WARNING + "  2 " + RESET + "- OSINT (Enumeración de Usuarios, Inteligencia Abierta)")
    print(Fore.BLUE + Style.BRIGHT + "  3 " + RESET + "- Toolkit (Generador de Hashes, Cifrado/Decodificación)")
    print(ERROR + "  0 " + RESET + "- Salir de SENTINEL")
    print("-" * 65)

def main():
    """Función principal que ejecuta el programa."""
    clear_screen() 
    display_header()
    
    while True:
        display_menu()
        
        try:
            choice = input(INFO + "SENTINEL" + Fore.WHITE + Style.BRIGHT + "> " + RESET).strip()
            
            # Limpiar la pantalla antes de entrar a un módulo para una interfaz limpia
            clear_screen()
            display_header() 
            
            if choice == '1':
                print(INFO + "\n[INFO] Accediendo al Módulo de Análisis Web...")
                web_analysis.run() # Llama a la función run del módulo web_analysis
                clear_screen()
                display_header()
                
            elif choice == '2':
                print(INFO + "\n[INFO] Accediendo al Módulo OSINT...")
                osint_collector.run() # Llama a la función run del módulo osint_collector
                clear_screen()
                display_header()
                
            elif choice == '3':
                print(INFO + "\n[INFO] Accediendo al Módulo Toolkit...")
                toolkit_utils.run() # Llama a la función run del módulo toolkit_utils
                clear_screen()
                display_header()
                
            elif choice == '0':
                print(SUCCESS + "\n[BYE] Saliendo de SENTINEL. ¡Gracias por usar la herramienta!")
                sys.exit(0)
                
            else:
                print(ERROR + "\n[ERROR] Opción no válida. Por favor, selecciona un número del 0 al 3.")
                input(INFO + "\nPresiona Enter para continuar..." + RESET)
                clear_screen()
                display_header()
                
        except KeyboardInterrupt:
            print(SUCCESS + "\n\n[BYE] Interrupción detectada. Saliendo de SENTINEL.")
            sys.exit(0)
        except Exception as e:
            print(ERROR + f"\n[CRITICAL ERROR] Ocurrió un error inesperado: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()