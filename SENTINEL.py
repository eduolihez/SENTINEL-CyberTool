import sys
import os
from colorama import init, Fore, Style 

# Inicializa colorama para que funcione en diferentes terminales (especialmente Windows)
init(autoreset=True) 

# --- Códigos de Color ---
INFO = Fore.CYAN + Style.BRIGHT
SUCCESS = Fore.GREEN + Style.BRIGHT
ERROR = Fore.RED + Style.BRIGHT
WARNING = Fore.YELLOW + Style.BRIGHT
HEADER = Fore.MAGENTA + Style.BRIGHT
RESET = Style.RESET_ALL

# --- Configuración de Rutas y Módulos ---
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
    
    # Importación de Módulos Funcionales
    from modules import web_analysis 
    
    # Importación de Módulos Futuros (Descomentar al crearlos)
    # from modules import osint_collector 
    # from modules import toolkit

except ImportError as e:
    print(ERROR + f"[ERROR CRÍTICO] No se pudo cargar un módulo necesario: {e}")
    print(WARNING + "Asegúrate de que los archivos de los módulos existan en la carpeta 'modules/'.")
    sys.exit(1)


# --- Funciones de Utilidad ---

def clear_screen():
    """Limpia la terminal (funciona en Windows, Linux y macOS)."""
    # Para Windows: 'cls', para Unix/Linux/macOS: 'clear'
    os.system('cls' if os.name == 'nt' else 'clear')


# --- Funciones de Interfaz Mejoradas ---

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
    print(SUCCESS + "  1 " + RESET + "- Análisis Web (Escaneo de puertos, Crawling, Subdominios)")
    print(WARNING + "  2 " + RESET + "- OSINT (Recolección de Inteligencia de Fuente Abierta) [Pendiente]")
    print(Fore.BLUE + Style.BRIGHT + "  3 " + RESET + "- Toolkit (Utilidades de Cifrado, Hashing, Manipulación) [Pendiente]")
    print(ERROR + "  0 " + RESET + "- Salir de SENTINEL")
    print("-" * 65)

def main():
    """Función principal que ejecuta el programa."""
    clear_screen() # Limpieza inicial para empezar de cero
    display_header()
    
    while True:
        display_menu()
        
        try:
            choice = input(INFO + "SENTINEL" + Fore.WHITE + Style.BRIGHT + "> " + RESET).strip()
            
            # Limpiar la pantalla antes de entrar al módulo para mayor claridad
            clear_screen()
            display_header() # Se muestra el encabezado en la nueva pantalla
            
            if choice == '1':
                print(INFO + "\n[INFO] Accediendo al Módulo de Análisis Web...")
                web_analysis.run() 
                # Después de que el módulo termina, limpiamos la pantalla de nuevo
                clear_screen()
                display_header()
                
            elif choice == '2':
                print(INFO + "\n[INFO] Iniciando Módulo OSINT...")
                # osint_collector.run() 
                print(WARNING + "[!] El Módulo OSINT está en desarrollo. Volviendo al menú principal.")
                # Damos un momento para leer el mensaje y luego limpiamos
                input(INFO + "\nPresiona Enter para continuar..." + RESET)
                clear_screen()
                display_header()
                
            elif choice == '3':
                print(INFO + "\n[INFO] Iniciando Toolkit de Utilidades...")
                # toolkit.run() 
                print(WARNING + "[!] El Módulo Toolkit está en desarrollo. Volviendo al menú principal.")
                input(INFO + "\nPresiona Enter para continuar..." + RESET)
                clear_screen()
                display_header()
                
            elif choice == '0':
                print(SUCCESS + "\n[BYE] Saliendo de SENTINEL. ¡Gracias por usar la herramienta!")
                sys.exit(0)
                
            else:
                print(ERROR + "\n[ERROR] Opción no válida. Por favor, selecciona un número del 0 al 3.")
                # Damos un momento para leer el error y luego limpiamos
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