# launcher.py

import sys
import os
import subprocess
from colorama import init, Fore, Back, Style
from datetime import datetime
import json
from configparser import ConfigParser

# Inicializar colorama
init(autoreset=True)

VERSION = "v0.5 Clonechat Launcher"

def mostrar_ascii():
    ascii_art = [
        "  _____ _                         _____ _           _   ",
        " / ____| |                       / ____| |         | |  ",
        "| |    | | ___  __ _ ___  ___   | |    | |__   ___ | |_ ",
        "| |    | |/ _ \\/ _` / __|/ _ \\  | |    | '_ \\ / _ \\| __|",
        "| |____| |  __/ (_| \\__ \\  __/  | |____| | | | (_) | |_ ",
        " \\_____|_|\\___|\\__,_|___/\\___|   \\_____|_| |_|\\___/ \\__|",
    ]
    for line in ascii_art:
        print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
    version_texto = f" Versión: {VERSION} "
    print(f"{Back.BLUE}{Fore.BLACK}{version_texto.center(70)}{Style.RESET_ALL}\n")

opciones = [
    {'texto': 'N. Nuevo clon', 'accion': 'nuevo_clon', 'letra': 'N'},
    {'texto': 'R. Reanudar clon', 'accion': 'reanudar_clon', 'letra': 'R'},
    {'texto': 'K. Reclonar archivos omitidos', 'accion': 'reclonar_omitidos', 'letra': 'K'},
    {'texto': 'V. Ver historial de clonación', 'accion': 'ver_historial', 'letra': 'V'},
    {'texto': 'C. Configuración', 'accion': 'configuracion', 'letra': 'C'},
    {'texto': 'A. Acerca de...', 'accion': 'acerca_de', 'letra': 'A'},
    {'texto': 'S. Salir', 'accion': 'salir', 'letra': 'S'},
]

def mostrar_barra_estado():
    hora_actual = datetime.now().strftime("%H:%M:%S")
    estado = f"{Fore.WHITE}{Back.BLUE} Hora: {hora_actual} {Style.RESET_ALL}"
    print(estado)

def mostrar_menu(opciones):
    mostrar_ascii()
    mostrar_barra_estado()
    print(f"\n{Back.CYAN}{Fore.BLACK}===== CloneChat Launcher ====={Style.RESET_ALL}\n")
    for opcion in opciones:
        print(f" {opcion['texto']}")
    print(f"\nSelecciona una opción ingresando la letra correspondiente.")

def manejar_seleccion():
    letra = input("Tu elección: ").strip().upper()
    encontrado = False
    for opcion in opciones:
        if letra == opcion['letra'].upper():
            accion = opcion['accion']
            encontrado = True
            break
    if not encontrado:
        print(f"{Back.RED}{Fore.BLACK}Opción no válida. Intenta de nuevo.{Style.RESET_ALL}")
        return
    try:
        if accion == "salir":
            print(f"{Back.GREEN}{Fore.BLACK}Saliendo de CloneChat Launcher...{Style.RESET_ALL}")
            sys.exit()
        elif accion in ["nuevo_clon", "reanudar_clon", "reclonar_omitidos"]:
            ejecutar_clonechat_interactivo(accion)
        elif accion == "ver_historial":
            ver_historial()
        elif accion == "configuracion":
            configuracion()
        elif accion == "acerca_de":
            mostrar_acerca_de()
        else:
            print(f"{Back.RED}{Fore.BLACK}Función '{accion}' no encontrada.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Back.RED}{Fore.BLACK}Error al ejecutar la opción '{accion}': {e}{Style.RESET_ALL}")
    finally:
        input(f"{Fore.YELLOW}Presiona Enter para continuar...{Style.RESET_ALL}")

def ejecutar_clonechat_interactivo(accion):
    if accion == "nuevo_clon":
        new_value = '1'
    elif accion == "reanudar_clon":
        new_value = '2'
    elif accion == "reclonar_omitidos":
        new_value = '3'
    else:
        new_value = '1'
    params = ['--new', new_value]
    
    if accion == "reanudar_clon":
        last_origin_chat_input, last_destination_chats = load_last_chats()
        if not last_origin_chat_input or not last_destination_chats:
            print(f"{Back.RED}{Fore.BLACK}No hay clonaciones previas para reanudar.{Style.RESET_ALL}")
            return
        orig = last_origin_chat_input
        dest = last_destination_chats
    else:
        orig = input("Ingresa el chat_id o username del origen: ").strip()
        dest = []
        while True:
            dest_input = input("Ingresa el chat_id o username del destino: ").strip()
            if dest_input:
                dest.append(dest_input)
                another = input("¿Deseas agregar otro destino? (Y/N): ").strip().upper()
                if another != 'Y':
                    break
            else:
                print("Entrada vacía. Inténtalo de nuevo.")
    
    mode = input("Selecciona el modo ('user' o 'bot'): ").strip()
    tipo_archivo = input("""\nIngresa el/los número(s) de tipo de archivo a clonar, separados por coma:
0 - Todos los archivos
1 - Fotos
2 - Texto
3 - Documentos (pdf, zip, rar...)
4 - Stickers
5 - Animación
6 - Archivos de audio (música)
7 - Mensaje de voz
8 - Videos
9 - Encuestas
Por ejemplo, para copiar fotos y documentos escribe: 1,3
Tu respuesta: """).strip()
    clone_mode = None
    if '0' in tipo_archivo:
        clone_mode = input("\nSelecciona el modo de clonación para 'Todos los archivos (0)':\nT - Todos los archivos, incluyendo imágenes individuales\nG - Copiar grupos de imágenes como álbumes y fotos individuales por separado\nC - Combinar imágenes sueltas en grupos de 3 a 10 elementos\nSelecciona una opción (T/G/C): ").strip().upper()
    params.extend(['--orig', orig])
    for d in dest:
        params.extend(['--dest', d])
    params.extend(['--mode', mode])
    params.extend(['--type', tipo_archivo])
    if clone_mode:
        params.extend(['--clone-mode', clone_mode])
    
    ejecutar_clonechat(*params)

def ejecutar_clonechat(*args):
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clonechat.py')
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"No se encontró clonechat.py en la ruta {script_path}")
        comando = [sys.executable, script_path] + list(args)
        subprocess.run(comando)
    except Exception as e:
        print(f"{Back.RED}{Fore.BLACK}Error al ejecutar clonechat.py: {e}{Style.RESET_ALL}")

def ver_historial():
    historial_file = "clone_history.txt"
    if os.path.exists(historial_file):
        with open(historial_file, "r", encoding='utf-8') as f:
            contenido = f.read()
            print(f"{Fore.CYAN}{contenido}{Style.RESET_ALL}")
    else:
        print(f"{Back.RED}{Fore.BLACK}No se encontró el historial de clonación.{Style.RESET_ALL}")

def configuracion():
    config_path = os.path.join("user", "config.ini")
    if not os.path.exists(config_path):
        print(f"{Back.RED}{Fore.BLACK}Archivo de configuración no encontrado. Creando uno nuevo.{Style.RESET_ALL}")
        ensure_folder_existence("user")
        config = ConfigParser()
        config['default'] = {
            'api_id': '',
            'api_hash': '',
            'bot_token': ''
        }
        with open(config_path, "w", encoding='utf-8') as f:
            config.write(f)
        print(f"{Fore.GREEN}Archivo de configuración creado en {config_path}. Por favor, edítalo con tus credenciales.{Style.RESET_ALL}")
        return
    print(f"Abriendo archivo de configuración: {config_path}")
    if sys.platform == "win32":
        os.startfile(config_path)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        os.system(f"{opener} {config_path}")

def mostrar_acerca_de():
    print(f"{Fore.CYAN}CloneChat - Herramienta para clonar chats de Telegram.")
    print("Desarrollado por ApenasR")
    print("Repositorio: github.com/apenasrr/clonechat")
    print(f"Versión: {VERSION}{Style.RESET_ALL}")

def load_last_chats():
    if os.path.exists("last_chats.json"):
        with open("last_chats.json", "r", encoding='utf-8') as f:
            data = json.load(f)
            return data.get("origin_chat_input"), data.get("destination_chats")
    else:
        return None, None

def save_last_chats(origin_chat_input, destination_chats):
    data = {
        "origin_chat_input": origin_chat_input,
        "destination_chats": destination_chats
    }
    with open("last_chats.json", "w", encoding='utf-8') as f:
        json.dump(data, f)

def ensure_folder_existence(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def main_launcher():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        mostrar_menu(opciones)
        manejar_seleccion()

if __name__ == "__main__":
    main_launcher()
