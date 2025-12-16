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
ACTION = Fore.WHITE + Style.BRIGHT # Color para la entrada del usuario
RESET = Style.RESET_ALL

# --- Funciones de Utilidad ---

def clear_screen():
    """Limpia la terminal (funciona en Windows, Linux y macOS)."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Configuración de Rutas y Módulos ---
# Aseguramos la importación de los módulos (se asume que existen)
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
    
    # Importación de Módulos Funcionales
    from modules import web_analysis 
    from modules import osint_collector
    from modules import toolkit_utils 
    
except ImportError as e:
    clear_screen()
    print(ERROR + "╔═════════════════════════════════════════════════════════╗")
    print(ERROR + f"║ [ERROR CRÍTICO] No se pudo cargar un módulo: {e}")
    print(WARNING + "║ Asegúrate de que los archivos de los módulos existan en la carpeta 'modules/'. ║")
    print(ERROR + "╚═════════════════════════════════════════════════════════╝")
    sys.exit(1)


# --- Funciones de Interfaz Mejoradas ---

def display_header():
    """Muestra un banner de SENTINEL más estilizado."""
    print(HEADER + "╔" + "═" * 63 + "╗")
    print(HEADER + "║       🛡️  S E N T I N E L   C Y B E R S E C U R I T Y 🛡️        ║")
    print(HEADER + "║  Superherramienta Modular (Web Analysis | OSINT | Toolkit)  ║")
    print(HEADER + "╚" + "═" * 63 + "╝")
    print(RESET)

def display_menu():
    """Muestra las opciones principales con separación y símbolos Unicode."""
    print(INFO + "\n[ C O N T R O L   P A N E L ]\n")
    
    # Opción 1: Análisis Web (Énfasis en la acción)
    print(SUCCESS + "  [1] " + RESET + "⚡ Análisis Web")
    print("      " + INFO + "  > Escaneo de Puertos, Rastreo Web, Enumeración de Subdominios")
    print("-" * 65)
    
    # Opción 2: OSINT
    print(WARNING + "  [2] " + RESET + "🔎 OSINT")
    print("      " + INFO + "  > Recolección de Inteligencia, Búsqueda de Usuarios y Huellas digitales")
    print("-" * 65)
    
    # Opción 3: Toolkit
    print(Fore.BLUE + Style.BRIGHT + "  [3] " + RESET + "🔧 Toolkit")
    print("      " + INFO + "  > Utilidades de Cifrado, Hashing y Manipulación de datos")
    print("-" * 65)
    
    # Opción 0: Salir (Énfasis en la salida)
    print(ERROR + "  [0] " + RESET + "❌ Salir de SENTINEL")
    print("\n" + "=" * 65)

def main():
    """Función principal que ejecuta el programa."""
    clear_screen() 
    display_header()
    
    while True:
        display_menu()
        
        try:
            choice = input(ACTION + "SENTINEL > Introduce tu opción: " + RESET).strip()
            
            # Limpiar la pantalla antes de entrar a un módulo
            clear_screen()
            display_header() 
            
            if choice == '1':
                print(INFO + "\n[ INICIO ] Accediendo al Módulo de Análisis Web...")
                web_analysis.run() 
                clear_screen()
                display_header()
                
            elif choice == '2':
                print(INFO + "\n[ INICIO ] Accediendo al Módulo OSINT...")
                osint_collector.run()
                clear_screen()
                display_header()
                
            elif choice == '3':
                print(INFO + "\n[ INICIO ] Accediendo al Módulo Toolkit...")
                toolkit_utils.run()
                clear_screen()
                display_header()
                
            elif choice == '0':
                print(SUCCESS + "\n[ EXIT ] Cerrando SENTINEL. ¡Gracias por usar la herramienta!")
                sys.exit(0)
                
            else:
                print(ERROR + "\n[ ERROR ] Opción no válida. Por favor, selecciona un número del 0 al 3.")
                input(INFO + "\nPresiona [ENTER] para continuar..." + RESET)
                clear_screen()
                display_header()
                
        except KeyboardInterrupt:
            print(SUCCESS + "\n\n[ EXIT ] Interrupción detectada (Ctrl+C). Saliendo de SENTINEL.")
            sys.exit(0)
        except Exception as e:
            print(ERROR + f"\n[ CRITICAL ERROR ] Ocurrió un error inesperado: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()