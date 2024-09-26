# clonechat.py

import argparse
import json
import os
import sys
import time
import threading
from configparser import ConfigParser

import pyrogram
from pyrogram.errors import ChannelInvalid, FloodWait, PeerIdInvalid, RPCError
from pyrogram.types import InputMediaPhoto, InputMediaVideo

DELAY_AMOUNT = 10
DELAY_SKIP = 0
PAUSE_EVENT = threading.Event()
EXIT_EVENT = threading.Event()


def reconnect_on_failure(func):
    def wrapper(*args, **kwargs):
        attempts = 0
        max_attempts = 3
        rounds = 0
        max_rounds = 3
        global tg
        while rounds < max_rounds:
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, RPCError) as e:
                    print(f"Conexión perdida: {e}. Intentando reconectar... (Intento {attempts + 1} de {max_attempts})")
                    time.sleep(5)
                    try:
                        tg.disconnect()
                        tg.connect()
                        print("Reconexión exitosa.")
                    except Exception as e_connect:
                        print(f"Error al reconectar: {e_connect}")
                    attempts += 1
                except Exception as e:
                    print(f"Error inesperado: {e}")
                    break
            rounds += 1
            attempts = 0
            print(f"Iniciando ronda {rounds + 1} de reconexión.")
        print("Máximo de intentos de reconexión alcanzados. Por favor, reinicia el programa o inténtalo más tarde.")
        sys.exit(1)
    return wrapper


@reconnect_on_failure
def forward_photo(message, destination_chat):
    caption = get_caption(message)
    if not caption:
        caption = "<loose-image>"
    photo_id = message.photo.file_id
    while True:
        try:
            tg.send_photo(
                chat_id=destination_chat,
                photo=photo_id,
                caption=caption,
            )
            break
        except FloodWait as e:
            print(f"..FloodWait {e.value} segundos..")
            time.sleep(e.value)
        except Exception as e:
            print(f"Intentando de nuevo... Debido a: {e}")
            time.sleep(10)


@reconnect_on_failure
def forward_text(message, destination_chat):
    text = get_text(message)
    while True:
        try:
            tg.send_message(
                chat_id=destination_chat,
                text=text,
                disable_notification=True,
                disable_web_page_preview=True,
            )
            break
        except FloodWait as e:
            print(f"..FloodWait {e.value} segundos..")
            time.sleep(e.value)
        except Exception as e:
            print(f"Intentando de nuevo... Debido a: {e}")
            time.sleep(10)


@reconnect_on_failure
def forward_sticker(message, destination_chat):
    sticker_id = message.sticker.file_id
    while True:
        try:
            tg.send_sticker(chat_id=destination_chat, sticker=sticker_id)
            break
        except FloodWait as e:
            print(f"..FloodWait {e.value} segundos..")
            time.sleep(e.value)
        except Exception as e:
            print(f"Intentando de nuevo... Debido a: {e}")
            time.sleep(10)


@reconnect_on_failure
def forward_document(message, destination_chat):
    caption = get_caption(message)
    document_id = message.document.file_id
    while True:
        try:
            tg.send_document(
                chat_id=destination_chat,
                document=document_id,
                disable_notification=True,
                caption=caption,
            )
            break
        except FloodWait as e:
            print(f"..FloodWait {e.value} segundos..")
            time.sleep(e.value)
        except Exception as e:
            print(f"Intentando de nuevo... Debido a: {e}")
            time.sleep(10)


@reconnect_on_failure
def forward_animation(message, destination_chat):
    caption = get_caption(message)
    animation_id = message.animation.file_id
    while True:
        try:
            tg.send_animation(
                chat_id=destination_chat,
                animation=animation_id,
                disable_notification=True,
                caption=caption,
            )
            break
        except FloodWait as e:
            print(f"..FloodWait {e.value} segundos..")
            time.sleep(e.value)
        except Exception as e:
            print(f"Intentando de nuevo... Debido a: {e}")
            time.sleep(10)


@reconnect_on_failure
def forward_audio(message, destination_chat):
    caption = get_caption(message)
    audio_id = message.audio.file_id
    while True:
        try:
            tg.send_audio(
                chat_id=destination_chat,
                audio=audio_id,
                disable_notification=True,
                caption=caption,
            )
            break
        except FloodWait as e:
            print(f"..FloodWait {e.value} segundos..")
            time.sleep(e.value)
        except Exception as e:
            print(f"Intentando de nuevo... Debido a: {e}")
            time.sleep(10)


@reconnect_on_failure
def forward_voice(message, destination_chat):
    caption = get_caption(message)
    voice_id = message.voice.file_id
    while True:
        try:
            tg.send_voice(
                chat_id=destination_chat,
                voice=voice_id,
                disable_notification=True,
                caption=caption,
            )
            break
        except FloodWait as e:
            print(f"..FloodWait {e.value} segundos..")
            time.sleep(e.value)
        except Exception as e:
            print(f"Intentando de nuevo... Debido a: {e}")
            time.sleep(10)


@reconnect_on_failure
def forward_video_note(message, destination_chat):
    video_note_id = message.video_note.file_id
    while True:
        try:
            tg.send_video_note(
                chat_id=destination_chat,
                video_note=video_note_id,
                disable_notification=True,
            )
            break
        except FloodWait as e:
            print(f"..FloodWait {e.value} segundos..")
            time.sleep(e.value)
        except Exception as e:
            print(f"Intentando de nuevo... Debido a: {e}")
            time.sleep(10)


@reconnect_on_failure
def forward_video(message, destination_chat):
    caption = get_caption(message)
    video_id = message.video.file_id
    while True:
        try:
            tg.send_video(
                chat_id=destination_chat,
                video=video_id,
                disable_notification=True,
                caption=caption,
            )
            break
        except FloodWait as e:
            print(f"..FloodWait {e.value} segundos..")
            time.sleep(e.value)
        except Exception as e:
            print(f"Intentando de nuevo... Debido a: {e}")
            time.sleep(10)


@reconnect_on_failure
def forward_poll(message, destination_chat):
    if message.poll.type != "regular":
        return
    while True:
        try:
            tg.send_poll(
                chat_id=destination_chat,
                question=message.poll.question,
                options=[option.text for option in message.poll.options],
                is_anonymous=message.poll.is_anonymous,
                allows_multiple_answers=message.poll.allows_multiple_answers,
                disable_notification=True,
            )
            break
        except FloodWait as e:
            print(f"..FloodWait {e.value} segundos..")
            time.sleep(e.value)
        except Exception as e:
            print(f"Intentando de nuevo... Debido a: {e}")
            time.sleep(10)


def get_caption(message):
    return message.caption if message.caption else None


def get_text(message):
    return message.text if message.text else ""


def get_sender(message):
    if message.photo:
        return forward_photo
    if message.text:
        return forward_text
    if message.document:
        return forward_document
    if message.sticker:
        return forward_sticker
    if message.animation:
        return forward_animation
    if message.audio:
        return forward_audio
    if message.voice:
        return forward_voice
    if message.video:
        return forward_video
    if message.video_note:
        return forward_video_note
    if message.poll:
        return forward_poll
    if message.service:
        return None
    return None


def get_input_type_to_copy():
    print("0 - Todos los archivos")
    print("1 - Fotos")
    print("2 - Texto")
    print("3 - Documentos (pdf, zip, rar, ...)")
    print("4 - Stickers")
    print("5 - Animación")
    print("6 - Archivos de audio (música)")
    print("7 - Mensaje de voz")
    print("8 - Videos")
    print("9 - Encuestas\n")
    print(
        "Ingresa el/los número(s) de tipo de archivo a clonar, separados por coma."
    )
    print("Por ejemplo, para copiar fotos y documentos escribe: 1,3")
    answer = input("Tu respuesta: ")
    return answer


def get_clone_mode():
    while True:
        print("\nOpciones de clonación para 'Todos los archivos (0)':")
        print("T - Todos los archivos, incluyendo imágenes individuales")
        print("G - Copiar grupos de imágenes como álbumes y fotos individuales por separado")
        print("C - Combinar imágenes sueltas en grupos de 3 a 10 elementos")
        choice = input("Selecciona una opción (T/G/C): ").strip().upper()
        if choice in ['T', 'G', 'C']:
            return choice
        else:
            print("Opción inválida. Por favor, ingresa 'T', 'G' o 'C'.")


def select_destination_groups(destination_chats):
    print("\n¿Hacia qué grupo desea enviar los álbumes?")
    for idx, chat in enumerate(destination_chats, 1):
        print(f"{idx}. {chat}")
    while True:
        album_choice = input(f"Tu elección (1-{len(destination_chats)}): ").strip()
        if album_choice in [str(i) for i in range(1, len(destination_chats)+1)]:
            album_destination = destination_chats[int(album_choice)-1]
            break
        else:
            print("Opción inválida. Por favor, elige una opción válida.")

    print("\n¿Hacia dónde desea enviar el resto de las imágenes?")
    for idx, chat in enumerate(destination_chats, 1):
        print(f"{idx}. {chat}")
    while True:
        image_choice = input(f"Tu elección (1-{len(destination_chats)}): ").strip()
        if image_choice in [str(i) for i in range(1, len(destination_chats)+1)]:
            image_destination = destination_chats[int(image_choice)-1]
            break
        else:
            print("Opción inválida. Por favor, elige una opción válida.")
    return album_destination, image_destination


def get_files_type_excluded_by_input(input_string, files_type_excluded):
    if "0" in input_string:
        return files_type_excluded
    else:
        if "1" not in input_string:
            files_type_excluded.append(forward_photo)
        if "2" not in input_string:
            files_type_excluded.append(forward_text)
        if "3" not in input_string:
            files_type_excluded.append(forward_document)
        if "4" not in input_string:
            files_type_excluded.append(forward_sticker)
        if "5" not in input_string:
            files_type_excluded.append(forward_animation)
        if "6" not in input_string:
            files_type_excluded.append(forward_audio)
        if "7" not in input_string:
            files_type_excluded.append(forward_voice)
        if "8" not in input_string:
            files_type_excluded.append(forward_video)
        if "9" not in input_string:
            files_type_excluded.append(forward_poll)
    if len(files_type_excluded) == 9:
        print("¡Opción inválida! Inténtalo de nuevo.")
        return get_files_type_excluded_by_input(get_input_type_to_copy(), [])
    return files_type_excluded


def get_list_posted(int_task_type, cache_file):
    if int_task_type == 1:
        if os.path.exists(cache_file):
            os.remove(cache_file)
        return []
    else:
        if os.path.exists(cache_file):
            with open(cache_file, mode="r", encoding='utf-8') as file:
                try:
                    posted = json.load(file)
                    return posted
                except json.JSONDecodeError:
                    print("Archivo de caché corrupto. Iniciando desde cero.")
                    return []
        else:
            return []


@reconnect_on_failure
def get_message(origin_chat, message_id):
    try:
        message = tg.get_messages(origin_chat, message_id)
        return message
    except FloodWait as e:
        print(f"..FloodWait {e.value} segundos..")
        time.sleep(e.value)
        return get_message(origin_chat, message_id)
    except Exception as e:
        print(f"Error inesperado al obtener el mensaje: {e}")
        time.sleep(10)
        return get_message(origin_chat, message_id)


def task_type_selection():
    print("¿Nuevo clon, continuación o reclonar archivos omitidos?")
    print("1 = Nuevo")
    print("2 = Reanudar")
    print("3 = Reclonar archivos omitidos")
    while True:
        answer = input("Tu respuesta: ")
        if answer == "1":
            return 1
        elif answer == "2":
            return 2
        elif answer == "3":
            return 3
        else:
            print("\nRespuesta inválida.\n")


def get_last_message_id(origin_chat):
    try:
        iter_message = tg.get_chat_history(origin_chat)
        message = next(iter_message)
        return message.id
    except StopIteration:
        print("No se encontraron mensajes en el chat de origen.")
        return 0
    except Exception as e:
        print(f"Error inesperado al obtener el último mensaje: {e}")
        return 0


def is_empty_message(message, message_id, last_message_id):
    return message is None or getattr(message, 'empty', False) or (not message.text and not message.media)


def wait_a_moment(message_id, delay_amount, delay_skip, skip=False):
    if message_id != 1:
        if skip:
            time.sleep(delay_skip)
        else:
            time.sleep(delay_amount)


def update_cache(cache_file, list_posted):
    try:
        with open(cache_file, mode="w", encoding='utf-8') as file:
            json.dump(list_posted, file)
    except Exception as e:
        print("Error al actualizar el caché:", e)


def ensure_folder_existence(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def get_task_file(origin_chat_title, destination_chats):
    ensure_folder_existence("user")
    ensure_folder_existence(os.path.join("user", "tasks"))
    
    # Verificar si destination_chats es una lista de tuplas o de strings
    if isinstance(destination_chats[0], tuple) and len(destination_chats[0]) == 2:
        dest_str = "-".join([chat_input for chat_input, _ in destination_chats])
    elif isinstance(destination_chats[0], str):
        dest_str = "-".join(destination_chats)
    else:
        print("Formato inesperado para destination_chats.")
        dest_str = "destinacion_invalida"
    
    task_file_name = f"{origin_chat_title}-{dest_str}.json"
    task_file_path = os.path.join("user", "tasks", task_file_name)
    return task_file_path


def check_chat_id(chat_id, mode):
    try:
        print(f"Intentando obtener el chat con ID: {chat_id}")
        chat_obj = tg.get_chat(chat_id)
        chat_title = chat_obj.title if chat_obj.title else chat_obj.first_name
        print(f"Chat encontrado: {chat_title}")
        return chat_title
    except ChannelInvalid:
        print("\nChat no accesible.")
        if mode == "bot":
            print(
                "\nVerifica que el bot sea parte del chat como administrador."
                + " Es necesario para el modo bot."
            )
        else:
            print("\nVerifica que la cuenta de usuario sea parte del chat.")
        return False
    except PeerIdInvalid as e:
        print(f"\nInvalid chat_id: {chat_id}")
        print(f"Detalles: {e}")
        print("Posibles razones:")
        print("- El chat_id es incorrecto o no existe.")
        print("- El chat_id se refiere a un grupo o canal del que no eres miembro.")
        print("- El argumento chat_id que pasaste es una cadena; debes convertirlo a entero con int(chat_id).")
        print("- El chat_id se refiere a un usuario o chat que tu sesión actual aún no ha encontrado.")
        print("Para comunicarte con un usuario, considera:")
        print("- Buscar su nombre de usuario.")
        print("- Estar en un grupo común.")
        print("- Tener sus contactos telefónicos guardados.")
        print("- Recibir un mensaje mencionándolo.")
        print("- Obtener la lista de diálogos.")
        return False
    except Exception as e:
        print(f"\nError inesperado al verificar el chat_id: {e}")
        return False


def resolve_username_to_chat_id(client, username):
    try:
        if username.startswith("t.me/"):
            username = username.split("t.me/")[-1]
        if not username.startswith("@"):
            username = "@" + username
        chat = client.get_chat(username)
        return chat.id
    except pyrogram.errors.UsernameNotOccupied:
        print(f"Error: El nombre de usuario '{username}' no está ocupado por nadie.")
    except pyrogram.errors.UsernameInvalid:
        print(f"Error: El nombre de usuario '{username}' es inválido.")
    except ChannelInvalid:
        print("Error: El chat no es accesible o el bot/usuario no es miembro.")
    except PeerIdInvalid as e:
        print(f"Error: PeerIdInvalid - {e}")
    except RPCError as e:
        print(f"RPCError: {e}")
    except Exception as e:
        print(f"Error inesperado al resolver username: {e}")
    return None


def normalize_chat_id(chat_id_str):
    chat_id_str = chat_id_str.strip()
    if chat_id_str.startswith("@") or chat_id_str.startswith("t.me/"):
        chat_id = resolve_username_to_chat_id(tg, chat_id_str)
        return chat_id
    elif chat_id_str.startswith("-100"):
        try:
            return int(chat_id_str)
        except ValueError:
            print("El ID del chat debe ser un número entero.")
            return None
    elif chat_id_str.startswith("100"):
        try:
            return -int(chat_id_str)
        except ValueError:
            print("El ID del chat debe ser un número entero.")
            return None
    else:
        try:
            return int(chat_id_str)
        except ValueError:
            print("El ID del chat debe ser un número entero o un username válido (por ejemplo, '@nombrecanal').")
            return None


def ensure_connection(mode, config_file):
    if mode == "user":
        try:
            print("Intentando iniciar sesión como usuario...")
            useraccount = pyrogram.Client(
                "user",
                api_id=int(config_file["default"].get("api_id")),
                api_hash=config_file["default"].get("api_hash")
            )
            useraccount.start()
            print("Cliente de usuario iniciado correctamente.")
            return useraccount
        except Exception as e:
            print(f"Error al iniciar el cliente de usuario: {e}")
            api_id = input("Ingresa tu api_id: ").strip()
            api_hash = input("Ingresa tu api_hash: ").strip()
            config_file["default"]["api_id"] = api_id
            config_file["default"]["api_hash"] = api_hash
            try:
                with open("user/config.ini", "w", encoding='utf-8') as configfile:
                    config_file.write(configfile)
                print("Archivo de configuración guardado correctamente.")
            except Exception as e_write:
                print(f"Error al escribir en config.ini: {e_write}")
                exit(1)
            try:
                useraccount = pyrogram.Client(
                    "user", api_id=int(api_id), api_hash=api_hash
                )
                useraccount.start()
                print("Cliente de usuario iniciado correctamente después de ingresar credenciales.")
                return useraccount
            except Exception as e:
                print(f"Error al iniciar sesión como usuario: {e}")
                exit(1)
    elif mode == "bot":
        try:
            print("Intentando iniciar sesión como bot...")
            bot = pyrogram.Client(
                "bot",
                api_id=int(config_file["default"].get("api_id")),
                api_hash=config_file["default"].get("api_hash"),
                bot_token=config_file["default"].get("bot_token")
            )
            bot.start()
            print("Cliente de bot iniciado correctamente.")
            return bot
        except Exception as e:
            print(f"Error al iniciar el cliente de bot: {e}")
            api_id = input("Ingresa tu api_id: ").strip()
            api_hash = input("Ingresa tu api_hash: ").strip()
            bot_token = input("Ingresa tu bot_token: ").strip()
            config_file["default"]["api_id"] = api_id
            config_file["default"]["api_hash"] = api_hash
            config_file["default"]["bot_token"] = bot_token
            try:
                with open("user/config.ini", "w", encoding='utf-8') as configfile:
                    config_file.write(configfile)
                print("Archivo de configuración guardado correctamente.")
            except Exception as e_write:
                print(f"Error al escribir en config.ini: {e_write}")
                exit(1)
            try:
                bot = pyrogram.Client(
                    "bot", api_id=int(api_id), api_hash=config_file["default"].get("api_hash"), bot_token=bot_token
                )
                bot.start()
                print("Cliente de bot iniciado correctamente después de ingresar credenciales.")
                return bot
            except Exception as e:
                print(f"Error al iniciar sesión como bot: {e}")
                exit(1)


def log_clone_history(origin_chat_title, destination_chat_ids, posicion, numero, nombre, file_id, tipo, status):
    history_file = "clone_history.txt"
    ensure_folder_existence("user")
    with open(history_file, "a", encoding='utf-8') as f:
        if posicion == 1 and numero == 1:
            dest_str = ",".join(map(str, destination_chat_ids))
            f.write(f"Grupo de origen: {origin_chat_title} - {dest_str}\n")
        dest_str = ",".join(map(str, destination_chat_ids)) if isinstance(destination_chat_ids, list) else str(destination_chat_ids)
        nombre = nombre.replace(";", ",")
        f.write(f"{posicion};{numero};{nombre};{file_id};{tipo};{status}\n")


def get_file_id(message):
    if message.photo:
        return message.photo.file_id
    if message.document:
        return message.document.file_id
    if message.animation:
        return message.animation.file_id
    if message.audio:
        return message.audio.file_id
    if message.video:
        return message.video.file_id
    if message.sticker:
        return message.sticker.file_id
    if message.voice:
        return message.voice.file_id
    if message.video_note:
        return message.video_note.file_id
    return "N/A"


def get_message_type(message):
    if message.photo:
        return "photo"
    if message.text:
        return "text"
    if message.document:
        return "document"
    if message.sticker:
        return "sticker"
    if message.animation:
        return "animation"
    if message.audio:
        return "audio"
    if message.voice:
        return "voice"
    if message.video:
        return "video"
    if message.video_note:
        return "video_note"
    if message.poll:
        return "poll"
    if message.service:
        return "service"
    return "unknown"


def save_last_chats(origin_chat_input, destination_chats):
    data = {
        "origin_chat_input": origin_chat_input,
        "destination_chats": destination_chats
    }
    with open("last_chats.json", "w", encoding='utf-8') as f:
        json.dump(data, f)


def load_last_chats():
    if os.path.exists("last_chats.json"):
        with open("last_chats.json", "r", encoding='utf-8') as f:
            data = json.load(f)
            return data.get("origin_chat_input"), data.get("destination_chats")
    else:
        return None, None


def monitor_keyboard():
    while not EXIT_EVENT.is_set():
        user_input = sys.stdin.readline().strip().upper()
        if user_input == 'X':
            print("Proceso pausado. Regresando al menú de selección de archivos.")
            PAUSE_EVENT.set()
        elif user_input == 'S':
            print("Saliendo del programa.")
            EXIT_EVENT.set()
            os._exit(0)


def get_config_data(path_file_config="user/config.ini"):
    config_file = ConfigParser()
    config_file.read(path_file_config)
    return config_file


def main(args=None):
    global tg, FILES_TYPE_EXCLUDED, DELAY_AMOUNT, DELAY_SKIP, destination_chats

    print(
        f"\n....:: Clonechat - v0.5.1.1 rawr5-skip2 ::....\n"
        + "github.com/apenasrr/clonechat/\n"
    )

    config_path = os.path.join("user", "config.ini")
    if not os.path.exists(config_path):
        ensure_folder_existence("user")
        with open(config_path, "w", encoding='utf-8') as configfile:
            configfile.write("[default]\n")

    config_file = get_config_data(path_file_config=config_path)

    try:
        USER_DELAY_SECONDS = float(
            config_file["default"].get("user_delay_seconds", 10)
        )
        BOT_DELAY_SECONDS = float(
            config_file["default"].get("bot_delay_seconds", 10)
        )
        SKIP_DELAY_SECONDS = float(
            config_file["default"].get("skip_delay_seconds", 0)
        )
        LIMIT_STANDALONE_IMAGES = config_file["default"].get("limit_standalone_images", "off").lower()
    except ValueError:
        print("Valores de delay en config.ini no son válidos. Usando valores por defecto.")
        USER_DELAY_SECONDS = 10
        BOT_DELAY_SECONDS = 10
        SKIP_DELAY_SECONDS = 0
        LIMIT_STANDALONE_IMAGES = "off"

    parser = argparse.ArgumentParser(
        description="Clonar chats de Telegram de un chat a otro."
    )
    parser.add_argument("--orig", type=str, help="chat_id o username del chat/grupo/canal de origen")
    parser.add_argument("--dest", type=str, nargs='+', help="chat_id o username del chat/grupo/canal de destino (puedes especificar múltiples destinos separados por espacio)")
    parser.add_argument(
        "--mode",
        choices=["user", "bot"],
        help='"user" es lento. "bot" requiere token_bot en las credenciales.',
    )
    parser.add_argument(
        "--new", type=int, choices=[1, 2, 3], help="1 = nuevo, 2 = reanudar, 3 = reclonar omitidos"
    )
    help_type = """Lista separada por comas de tipo de mensaje a clonar:
0 = Todos los archivos
1 = Fotos
2 = Texto
3 = Documentos (pdf, zip, rar...)
4 = Stickers
5 = Animación
6 = Archivos de audio (música)
7 = Mensaje de voz
8 = Videos
9 = Encuestas"""
    parser.add_argument("--type", help=help_type)
    parser.add_argument("--clone-mode", choices=['T', 'G', 'C'], help="Modo de clonación para 'Todos los archivos (0)'")
    parser.add_argument("--limit-standalone-images", choices=['on', 'off'], help="Limitar imágenes individuales")
    parser.add_argument("--skip-delay", type=float, help="Tiempo de espera al omitir mensajes")
    parser.add_argument("--user-delay", type=float, help="Tiempo de espera entre mensajes en modo usuario")
    parser.add_argument("--bot-delay", type=float, help="Tiempo de espera entre mensajes en modo bot")
    options = parser.parse_args(args)

    MODE = options.mode if options.mode else config_file["default"].get("mode", "user")

    tg = ensure_connection(MODE, config_file)
    if MODE == "bot":
        DELAY_AMOUNT = BOT_DELAY_SECONDS
    else:
        DELAY_AMOUNT = USER_DELAY_SECONDS

    if options.user_delay:
        DELAY_AMOUNT = options.user_delay
    if options.bot_delay and MODE == "bot":
        DELAY_AMOUNT = options.bot_delay
    if options.skip_delay:
        DELAY_SKIP = options.skip_delay
    LIMIT_STANDALONE_IMAGES = options.limit_standalone_images if options.limit_standalone_images else LIMIT_STANDALONE_IMAGES

    NEW = options.new if options.new else task_type_selection()

    while True:
        last_origin_chat_input, last_destination_chats = load_last_chats()
        use_last_chats = False

        if last_origin_chat_input and last_destination_chats:
            choice = input("¿Deseas continuar con el último chat de origen y destino? (Y/N): ").strip().upper()
            if choice == "Y":
                use_last_chats = True

        if use_last_chats:
            origin_chat_input = last_origin_chat_input
        elif options.orig:
            origin_chat_input = options.orig.strip()
        else:
            while True:
                origin_chat_input = input("Ingresa el chat_id o username del origen: ").strip()
                if not origin_chat_input:
                    print("Entrada vacía. Inténtalo de nuevo.")
                    continue
                break

        origin_chat_int = normalize_chat_id(origin_chat_input)
        if origin_chat_int is None:
            raise AttributeError("Corrige el chat_id del origen")
        ORIGIN_CHAT_TITLE = check_chat_id(origin_chat_int, MODE)
        if not ORIGIN_CHAT_TITLE:
            raise AttributeError("Corrige el chat_id del origen")

        if use_last_chats:
            destination_chats_inputs = last_destination_chats
        elif options.dest:
            destination_chats_inputs = options.dest
        else:
            destination_chats_inputs = []
            while True:
                dest_prompt = "Ingresa el chat_id o username del destino {}: ".format(len(destination_chats_inputs)+1)
                destination_chat_input = input(dest_prompt).strip()
                if not destination_chat_input:
                    print("Entrada vacía. Inténtalo de nuevo.")
                    continue
                destination_chats_inputs.append(destination_chat_input)
                add_more = input("¿Deseas agregar otro destino? (Y/N): ").strip().upper()
                if add_more != "Y":
                    break

        if not destination_chats_inputs:
            print("Debe haber al menos un destino válido.")
            exit(1)

        destination_chats = []
        for chat_input in destination_chats_inputs:
            chat_id = normalize_chat_id(chat_input)
            if chat_id is None:
                print(f"Error al resolver el chat de destino: {chat_input}")
                exit(1)
            DESTINATION_CHAT_TITLE = check_chat_id(chat_id, MODE)
            if DESTINATION_CHAT_TITLE:
                destination_chats.append((chat_input, chat_id))

        if not destination_chats:
            print("No se pudieron resolver los chats de destino.")
            exit(1)

        save_last_chats(origin_chat_input, [chat_input for chat_input, _ in destination_chats])

        if options.type:
            TYPE = options.type.strip()
            if "0" in TYPE:
                clone_mode = options.clone_mode if options.clone_mode else get_clone_mode()
                if clone_mode in ['G', 'C']:
                    album_destination_input, image_destination_input = select_destination_groups([chat_input for chat_input, _ in destination_chats])
                else:
                    album_destination_input = image_destination_input = None
            else:
                clone_mode = None
                album_destination_input, image_destination_input = None, None
            FILES_TYPE_EXCLUDED = get_files_type_excluded_by_input(TYPE, [])
        else:
            input_type = get_input_type_to_copy()
            if "0" in input_type:
                clone_mode = get_clone_mode()
                if clone_mode in ['G', 'C']:
                    album_destination_input, image_destination_input = select_destination_groups([chat_input for chat_input, _ in destination_chats])
                else:
                    album_destination_input = image_destination_input = None
            else:
                clone_mode = None
                album_destination_input, image_destination_input = None, None
            FILES_TYPE_EXCLUDED = get_files_type_excluded_by_input(input_type, [])

        album_destination = None
        image_destination = None
        for chat_input, chat_id in destination_chats:
            if chat_input == album_destination_input:
                album_destination = chat_id
            if chat_input == image_destination_input:
                image_destination = chat_id

        if clone_mode in ['G', 'C'] and (album_destination is None or image_destination is None):
            print("No se pudieron resolver los destinos para álbumes o imágenes.")
            exit(1)

        CACHE_FILE = get_task_file(ORIGIN_CHAT_TITLE, [chat_input for chat_input, _ in destination_chats])

        if NEW == 1:
            last_message_id = get_last_message_id(origin_chat_int)
            list_posted = get_list_posted(NEW, CACHE_FILE)
            message_id = list_posted[-1] if list_posted else 0
        elif NEW == 2:
            last_message_id = get_last_message_id(origin_chat_int)
            list_posted = get_list_posted(NEW, CACHE_FILE)
            message_id = list_posted[-1] if list_posted else 0
        elif NEW == 3:
            list_posted = []
            reclone_message_ids = []
            if os.path.exists("clone_history.txt"):
                with open("clone_history.txt", "r", encoding='utf-8') as f:
                    lines = f.readlines()
                    dest_str = ",".join([chat_input for chat_input, _ in destination_chats])
                    group_header = f"Grupo de origen: {ORIGIN_CHAT_TITLE} - {dest_str}\n"
                    if group_header in lines:
                        header_index = lines.index(group_header)
                        for line in lines[header_index + 1:]:
                            if line.startswith("Grupo de origen:"):
                                break
                            parts = line.strip().split(";", 5)
                            if len(parts) < 6:
                                continue
                            posicion, numero, nombre, file_id, tipo, status = parts
                            if status == "salteado":
                                try:
                                    reclone_message_ids.append(int(numero))
                                except ValueError:
                                    continue
                            elif status == "clonado":
                                list_posted.append(int(numero))
                    else:
                        print("No se encontraron registros previos para este grupo de origen y destino.")
                if not reclone_message_ids:
                    print("No hay archivos omitidos para reclonar.")
                    print("Finalizando el programa. ¡Hasta luego!")
                    exit(0)
                message_id = 0
            else:
                print("No existe el archivo clone_history.txt. No hay archivos omitidos para reclonar.")
                exit(0)

        keyboard_thread = threading.Thread(target=monitor_keyboard, daemon=True)
        keyboard_thread.start()

        pending_images = []
        pending_captions = []

        max_standalone_images = 20
        limit_images = LIMIT_STANDALONE_IMAGES == "on"

        history_cloned = set()
        history_omitted = set()
        if os.path.exists("clone_history.txt"):
            with open("clone_history.txt", "r", encoding='utf-8') as f:
                for line in f:
                    if not line.startswith("Grupo de origen:"):
                        parts = line.strip().split(";", 5)
                        if len(parts) >= 6:
                            numero = parts[1]
                            status = parts[5]
                            try:
                                num = int(numero)
                                if status == "clonado":
                                    history_cloned.add(num)
                                elif status == "salteado":
                                    history_omitted.add(num)
                            except ValueError:
                                continue

        while True:
            if NEW in [1, 2, 3]:
                while message_id < last_message_id:
                    if PAUSE_EVENT.is_set():
                        PAUSE_EVENT.clear()
                        input_type = get_input_type_to_copy()
                        FILES_TYPE_EXCLUDED = get_files_type_excluded_by_input(input_type, [])
                        message_id = list_posted[-1] if list_posted else 0
                        continue

                    message_id += 1
                    if message_id in list_posted or message_id in history_cloned:
                        continue

                    if message_id in history_omitted and NEW != 3:
                        continue

                    message = get_message(origin_chat_int, message_id)

                    if is_empty_message(message, message_id, last_message_id):
                        if message:
                            list_posted.append(message.id)
                        else:
                            list_posted.append(message_id)
                        update_cache(CACHE_FILE, list_posted)
                        log_clone_history(
                            ORIGIN_CHAT_TITLE,
                            [chat_input for chat_input, _ in destination_chats],
                            posicion=message_id,
                            numero=message_id,
                            nombre="Empty Message",
                            file_id="N/A",
                            tipo="empty",
                            status="salteado"
                        )
                        print(f"{message_id}/{last_message_id}")
                        continue

                    func_sender = get_sender(message)
                    if func_sender is None:
                        list_posted.append(message.id)
                        update_cache(CACHE_FILE, list_posted)
                        log_clone_history(
                            ORIGIN_CHAT_TITLE,
                            [chat_input for chat_input, _ in destination_chats],
                            posicion=message_id,
                            numero=message_id,
                            nombre="Unsupported Message",
                            file_id="N/A",
                            tipo=get_message_type(message),
                            status="salteado"
                        )
                        print(f"{message_id}/{last_message_id}")
                        continue

                    if func_sender in FILES_TYPE_EXCLUDED:
                        print(f"{message_id}/{last_message_id} (se omitió por tipo)")
                        list_posted.append(message.id)
                        update_cache(CACHE_FILE, list_posted)
                        log_clone_history(
                            ORIGIN_CHAT_TITLE,
                            [chat_input for chat_input, _ in destination_chats],
                            posicion=message_id,
                            numero=message_id,
                            nombre=get_caption(message) if get_caption(message) else "<loose-image>",
                            file_id=get_file_id(message),
                            tipo=get_message_type(message),
                            status="salteado"
                        )
                        wait_a_moment(message_id, DELAY_AMOUNT, DELAY_SKIP, skip=True)
                        continue

                    if message.media_group_id:
                        media_group_id = message.media_group_id
                        media_messages = []
                        current_id = message_id
                        while True:
                            media_msg = get_message(origin_chat_int, current_id)
                            if media_msg and media_msg.media_group_id == media_group_id:
                                media_messages.append(media_msg)
                                current_id += 1
                                message_id = current_id - 1
                            else:
                                break
                        media_list = []
                        for idx, msg in enumerate(media_messages):
                            caption = get_caption(msg) if get_caption(msg) else None
                            if msg.photo:
                                media_list.append(InputMediaPhoto(media=msg.photo.file_id, caption=caption))
                            elif msg.video:
                                media_list.append(InputMediaVideo(media=msg.video.file_id, caption=caption))
                        try:
                            attempts = 0
                            while attempts < 3:
                                try:
                                    tg.send_media_group(chat_id=album_destination, media=media_list)
                                    break
                                except PeerIdInvalid:
                                    print("Error: PeerIdInvalid al enviar álbum. Recalculando chat_id.")
                                    album_destination = normalize_chat_id(album_destination_input)
                                    attempts += 1
                            else:
                                print("Error persistente al enviar álbum. Saltando.")
                                continue

                            print(f"Álbum enviado: mensajes {media_messages[0].id}-{media_messages[-1].id}")
                            for msg in media_messages:
                                list_posted.append(msg.id)
                                log_clone_history(
                                    ORIGIN_CHAT_TITLE,
                                    album_destination_input,
                                    posicion=msg.id,
                                    numero=msg.id,
                                    nombre=get_caption(msg) if get_caption(msg) else "<loose-image>",
                                    file_id=get_file_id(msg),
                                    tipo=get_message_type(msg),
                                    status="clonado"
                                )
                            update_cache(CACHE_FILE, list_posted)
                            wait_a_moment(message_id, DELAY_AMOUNT, DELAY_SKIP)
                        except FloodWait as e:
                            print(f"..FloodWait {e.value} segundos..")
                            time.sleep(e.value)
                        except Exception as e:
                            print(f"Error al enviar el álbum: {e}")
                            time.sleep(10)
                        print(f"{message_id}/{last_message_id}")
                        continue

                    else:
                        if limit_images and func_sender == forward_photo:
                            pending_images.append(message)
                            if len(pending_images) >= max_standalone_images:
                                media_list = []
                                for msg in pending_images:
                                    caption = get_caption(msg) if get_caption(msg) else "<loose-image>"
                                    if msg.photo:
                                        media_list.append(InputMediaPhoto(media=msg.photo.file_id, caption=caption))
                                try:
                                    tg.send_media_group(chat_id=album_destination, media=media_list)
                                    for msg in pending_images:
                                        list_posted.append(msg.id)
                                        log_clone_history(
                                            ORIGIN_CHAT_TITLE,
                                            album_destination_input,
                                            posicion=msg.id,
                                            numero=msg.id,
                                            nombre=get_caption(msg) if get_caption(msg) else "<loose-image>",
                                            file_id=get_file_id(msg),
                                            tipo=get_message_type(msg),
                                            status="clonado"
                                        )
                                    update_cache(CACHE_FILE, list_posted)
                                    pending_images = []
                                    wait_a_moment(message_id, DELAY_AMOUNT, DELAY_SKIP)
                                except Exception as e:
                                    print(f"Error al enviar imágenes combinadas: {e}")
                                    time.sleep(10)
                                print(f"{message_id}/{last_message_id}")
                                continue
                            else:
                                list_posted.append(message.id)
                                update_cache(CACHE_FILE, list_posted)
                                log_clone_history(
                                    ORIGIN_CHAT_TITLE,
                                    [chat_input for chat_input, _ in destination_chats],
                                    posicion=message_id,
                                    numero=message_id,
                                    nombre=get_caption(message) if get_caption(message) else "<loose-image>",
                                    file_id=get_file_id(message),
                                    tipo=get_message_type(message),
                                    status="clonado"
                                )
                                for dest_input, dest_id in destination_chats:
                                    attempts = 0
                                    while attempts < 3:
                                        try:
                                            func_sender(message, dest_id)
                                            break
                                        except PeerIdInvalid:
                                            print(f"Error: PeerIdInvalid al enviar mensaje a {dest_input}. Recalculando chat_id.")
                                            dest_id = normalize_chat_id(dest_input)
                                            attempts += 1
                                    else:
                                        print(f"Error persistente al enviar mensaje a {dest_input}. Saltando.")
                                        continue
                                wait_a_moment(message_id, DELAY_AMOUNT, DELAY_SKIP)
                        else:
                            log_clone_history(
                                ORIGIN_CHAT_TITLE,
                                [chat_input for chat_input, _ in destination_chats],
                                posicion=message_id,
                                numero=message_id,
                                nombre=get_caption(message) if get_caption(message) else "<loose-image>",
                                file_id=get_file_id(message),
                                tipo=get_message_type(message),
                                status="clonado"
                            )
                            for dest_input, dest_id in destination_chats:
                                attempts = 0
                                while attempts < 3:
                                    try:
                                        func_sender(message, dest_id)
                                        break
                                    except PeerIdInvalid:
                                        print(f"Error: PeerIdInvalid al enviar mensaje a {dest_input}. Recalculando chat_id.")
                                        dest_id = normalize_chat_id(dest_input)
                                        attempts += 1
                                else:
                                    print(f"Error persistente al enviar mensaje a {dest_input}. Saltando.")
                                    continue
                            list_posted.append(message.id)
                            update_cache(CACHE_FILE, list_posted)
                            wait_a_moment(message_id, DELAY_AMOUNT, DELAY_SKIP)
                    print(f"{message_id}/{last_message_id}")

                    if EXIT_EVENT.is_set():
                        print("Saliendo del programa.")
                        os._exit(0)

            else:
                print("Opción de tarea no válida.")
                break

        print(
            "\n¡Clonación del chat completada! :)\n"
            + "Si no vas a continuar esta tarea para estos chats, "
            + "elimina el archivo posted.json"
        )

        while True:
            final_option = input("¿Deseas iniciar una nueva clonación? (Y/N): ").strip().upper()
            if final_option == "Y":
                print("\nReiniciando el proceso de clonación...\n")
                NEW = task_type_selection()
                break
            elif final_option == "N":
                print("\nFinalizando el programa. ¡Hasta luego!")
                exit(0)
            else:
                print("Opción inválida. Por favor, ingresa 'Y' o 'N'.")


if __name__ == "__main__":
    main()
