Clonechat v0.5.1.1 rawr5-skip2
Clona todas las publicaciones del historial de un canal o grupo de Telegram a otro canal o grupo.

Nuevas características en v0.5.1.1 rawr5-skip2:
Soporte para clonación por lotes, con imágenes agrupadas en álbumes.
Modo de clonación flexible: permite clonar todos los archivos o seleccionar tipos específicos (fotos, documentos, videos, etc.).
Opción para reanudar clonaciones interrumpidas o reclonar archivos omitidos.
Registro detallado del historial de clonación, con posibilidad de continuar desde el punto exacto donde se detuvo.
Compatibilidad con múltiples destinos al mismo tiempo.
Modo usuario y modo bot: soporte para enviar mensajes con cuentas personales o mediante bots.
Gestión de errores mejorada con reintentos automáticos y reconexión en caso de fallos de conexión.
Configuración inicial
1. Actualización de dependencias
Ejecuta el archivo update_libs.bat para actualizar las bibliotecas y dependencias necesarias.
2. Configuración de credenciales
Registra tus credenciales de acceso a la API de Telegram en el archivo user/config.ini. Si no tienes estas credenciales, sigue los pasos descritos en la sección Generar credenciales de la API de Telegram.
3. Configuración del launcher
El archivo launcher.py permite ejecutar Clonechat mediante un menú interactivo con diversas opciones, facilitando la gestión y personalización del proceso de clonación.
Uso
1. Ejecutar vía línea de comandos
Comando básico:
bash
Copiar código
python clonechat.py --orig={chat_id del canal o grupo origen} --dest=-{chat_id del canal o grupo destino}
Ejemplo:
bash
Copiar código
python clonechat.py --orig=-100222222 --dest=-10011111111
2. Ejecutar con menú interactivo (Launcher)
Ejecuta el archivo launcher.py:
bash
Copiar código
python launcher.py
Ingresa el chat_id del canal/grupo origen.
Confirma con [ENTER].
Ingresa el chat_id del canal/grupo destino.
Confirma con [ENTER].
Elige entre las siguientes opciones:
Nuevo clon: Inicia una clonación desde cero.
Reanudar clon: Continúa una clonación previa interrumpida.
Reclonar omitidos: Vuelve a clonar archivos que fueron saltados u omitidos en intentos anteriores.
Ver historial de clonación: Muestra un registro de todas las clonaciones realizadas.
Configuración: Permite editar las credenciales de la API de Telegram.
Salir: Cierra el programa.
Finalización del proceso
Al finalizar una clonación, si no necesitas continuarla más tarde, elimina el archivo posted.json. Si este archivo no se elimina, la próxima vez que ejecutes el script, continuará la clonación desde donde quedó.
bash
Copiar código
rm user/tasks/{nombre_del_archivo}.json
FAQ
¿Cómo obtener el chat_id de un canal o grupo?
Existen varias formas de obtener el chat_id de un canal o grupo de Telegram. A continuación se explican dos métodos:

Utilizando el cliente de Telegram Kotatogram:

Abre la pantalla de descripción del canal o grupo.
Copia el chat_id que aparece debajo del nombre del canal.
Utilizando el bot Find_TGIDbot:

Abre una conversación con el bot.
Reenvía cualquier publicación del canal al bot.
El bot te responderá con el ID del remitente del mensaje (en este caso, el ID del canal).
¿Cómo generar las credenciales de la API de Telegram?
Para generar tus credenciales de la API de Telegram, sigue estos pasos:

Ve al sitio de Telegram Developer.
Inicia sesión con tu número de teléfono.
En la sección de API Development, crea una nueva aplicación.
Obtendrás un api_id y un api_hash. Estos datos son los que debes registrar en el archivo config.ini.
También puedes ver este video explicativo: Cómo obtener credenciales de la API de Telegram.

Consideraciones adicionales en la versión v0.5.1.1 rawr5-skip2
Control de flujo y reconexión automática: Si el proceso de clonación se interrumpe debido a problemas de conexión o bloqueos temporales, el sistema intentará reconectarse y continuar la clonación desde el punto exacto en el que se detuvo.
Tipos de archivos soportados: Se pueden clonar los siguientes tipos de archivos:
Fotos
Videos
Stickers
Documentos (PDF, ZIP, RAR)
Mensajes de voz
Encuestas
Texto
Archivos de audio (música)
Optimización de imágenes: En modo álbum, se puede elegir entre clonar imágenes sueltas o agruparlas en álbumes para ahorrar espacio y mejorar la organización.
Ejemplo de ejecución completa
Ejecutar launcher:
bash
Copiar código
python launcher.py
Seleccionar "Nuevo clon".

Ingresar el chat_id del canal origen: -1001127191881.

Ingresar el chat_id del canal destino: -1002261486832.

Seleccionar los tipos de archivos a clonar: Fotos y Documentos (1,3).

Comenzar el proceso de clonación.

El proceso iniciará y te mostrará una barra de progreso junto con la cantidad de mensajes enviados y totales.
