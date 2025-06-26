# 🤖 FlexBot - Asistente de Moderación para Discord

[![Estado del Proyecto: En Desarrollo](https://img.shields.io/badge/Estado-En%20Desarrollo-green.svg)](https://github.com/R4F405/Bot_Discord_Moderacion_comandos)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![discord.py](https://img.shields.io/badge/discord.py-v2.3.0%2B-7289DA.svg?logo=discord&logoColor=white)](https://discordpy.readthedocs.io/en/latest/)
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**FlexBot** es un bot de Discord versátil y fácil de usar, diseñado para potenciar la moderación de tu servidor con un amplio abanico de funcionalidades. Simplifica la gestión de usuarios, reportes y la configuración de tu comunidad.

## 🌟 Características Principales

FlexBot está equipado con un conjunto de herramientas intuitivas para mantener tu servidor seguro y ordenado:

*   **Sistema de Moderación Integral:**
    *   Expulsar (`kick`), banear (`ban`) y desbanear (`unban`) usuarios.
    *   Silenciar (`mute`) y desilenciar (`unmute`) miembros temporalmente con duración personalizable.
    *   Sistema de advertencias (`warn`) para notificar a los usuarios sobre comportamientos inadecuados.
*   **Gestión Avanzada de Reportes:**
    *   Comando `report` para que los usuarios informen sobre conductas inapropiadas.
    *   Canal dedicado `#reportes` para la revisión centralizada por parte de los moderadores.
    *   Acciones rápidas mediante reacciones (✅ Resolver, ❌ Descartar, 🔨 Aplicar Sanción) directamente en los mensajes de reporte.
    *   Visualización de reportes por estado: pendientes, resueltos, todos (`!flex reports [estado]`).
*   **Protección Anti-Spam Automática:**
    *   Detección y silenciamiento temporal automático de usuarios que envíen mensajes masivos en cortos periodos.
    *   Exención para moderadores y administradores.
*   **Gestión de Hilos (Threads):**
    *   Designar canales específicos (`!flex designarhilocanal`) donde se pueden crear hilos gestionados.
    *   Crear hilos (`!flex crearhilo`) con nombres personalizados, duración temporal opcional y opción de notificar a participantes.
    *   Cierre automático de hilos temporales tras expirar su duración.
    *   Cierre manual de hilos por moderadores (`!flex cerrarhilo`).
*   **Comandos de Información Útiles:**
    *   `!flex info`: Ayuda para usuarios generales.
    *   `!flex info2`: Ayuda detallada para moderadores.
    *   `!flex userinfo [@usuario/ID]`: Información detallada sobre un miembro del servidor.
    *   `!flex serverinfo`: Estadísticas y detalles del servidor.
*   **Utilidades Adicionales:**
    *   `!flex clear [cantidad]`: Limpieza de mensajes en un canal.
    *   `!flex slowmode [segundos]`: Configuración del modo lento en canales.
*   **Configuración Dinámica:**
    *   Creación automática del rol `Muted` (con permisos configurados) si no existe.
    *   Creación automática del canal `#reportes` y la categoría `Moderación` si no existen.

## 📋 Requisitos Previos

Antes de instalar FlexBot, asegúrate de tener:

*   Python 3.8 o superior.
*   Una cuenta de Discord.
*   Un servidor de Discord donde tengas permisos administrativos para añadir bots.
*   Conocimientos básicos sobre cómo funciona un bot de Discord y el Portal de Desarrolladores.

## 🚀 Instalación y Configuración

Sigue estos pasos para poner en marcha FlexBot en tu servidor:

### 1. Clonar el Repositorio

```bash
git clone https://github.com/R4F405/Bot_Discord_Moderacion_comandos.git
cd Bot_Discord_Moderacion_comandos
```

### 2. Instalar Dependencias

Crea un entorno virtual (recomendado) e instala las dependencias:

```bash
python -m venv venv
# En Windows:
# venv\Scripts\activate
# En macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configuración del Bot en Discord Developer Portal

1.  Ve al [Portal de Desarrolladores de Discord](https://discord.com/developers/applications).
2.  Haz clic en "**New Application**" y asígnale un nombre (ej. "FlexBot Moderador").
3.  Navega a la pestaña "**Bot**" en el menú lateral.
4.  Haz clic en "**Add Bot**" y confirma.
5.  **Obtén el Token del Bot:** Bajo el nombre del bot, haz clic en "**Reset Token**" y copia el token generado. ¡Guárdalo en un lugar seguro, lo necesitarás pronto!
6.  **Habilita las Intenciones Privilegiadas (Privileged Gateway Intents):** Asegúrate de que las siguientes intenciones estén activadas:
    *   `Presence Intent` (Intención de Presencia)
    *   `Server Members Intent` (Intención de Miembros del Servidor)
    *   `Message Content Intent` (Intención de Contenido de Mensajes)

### 4. Configurar el Archivo `.env`

1.  En la raíz del proyecto, renombra el archivo `.env.example` a `.env`.
2.  Abre el archivo `.env` y reemplaza `tu_token_aquí` con el token de tu bot que copiaste anteriormente:

    ```env
    DISCORD_TOKEN=AQUÍ_VA_EL_TOKEN_DE_TU_BOT
    ```

### 5. Invitar el Bot a tu Servidor

1.  Vuelve al Portal de Desarrolladores, selecciona tu aplicación y ve a "**OAuth2**" -> "**URL Generator**".
2.  En "**Scopes**", selecciona:
    *   `bot`
    *   `applications.commands` (Aunque este bot usa prefijos, es buena práctica incluirlo para futura compatibilidad).
3.  En "**Bot Permissions**", selecciona los siguientes permisos necesarios para el funcionamiento completo de FlexBot:
    *   `Manage Channels` (Gestionar Canales)
    *   `Manage Roles` (Gestionar Roles)
    *   `Kick Members` (Expulsar Miembros)
    *   `Ban Members` (Banear Miembros)
    *   `Manage Messages` (Gestionar Mensajes)
    *   `Read Message History` (Leer Historial de Mensajes) - Implícito con `View Channels`.
    *   `Send Messages` (Enviar Mensajes)
    *   `Create Public Threads` (Crear Hilos Públicos)
    *   `Create Private Threads` (Crear Hilos Privados) - Opcional si no se usan.
    *   `Send Messages in Threads` (Enviar Mensajes en Hilos)
    *   `Manage Threads` (Gestionar Hilos)
    *   `Embed Links` (Incrustar Enlaces) - Para los mensajes de ayuda e información.
    *   `Attach Files` (Adjuntar Archivos) - Opcional, para futuras mejoras.
    *   `Add Reactions` (Añadir Reacciones) - Esencial para el sistema de reportes.
    *   `View Channels` (Ver Canales) - Implícito.
    *   `Mention Everyone` (Mencionar @everyone, @here y todos los roles) - Usado con moderación.
4.  Copia la URL generada al final de la página y pégala en tu navegador. Selecciona el servidor al que deseas añadir el bot y autoriza.

### 6. Ejecutar el Bot

Finalmente, ejecuta el bot desde la terminal, asegurándote de estar en el directorio raíz del proyecto y con tu entorno virtual activado:

```bash
python main.py
```

Si todo está configurado correctamente, verás un mensaje en la consola indicando que el bot se ha conectado.

## 🛠️ Uso de Comandos

El prefijo por defecto del bot es `!flex `. También puedes mencionarlo (`@FlexBot `).

### Comandos para Usuarios

*   `!flex info`: Muestra los comandos básicos disponibles para usuarios.
*   `!flex report @usuario [razón detallada]`: Reporta a un usuario por comportamiento inadecuado.
    *   *Ejemplo:* `!flex report @UsuarioMolesto Ha estado enviando spam en #general`

### Comandos para Moderadores

Usa `!flex info2` para una lista completa en Discord. Aquí algunos destacados:

**Moderación Básica:**

*   `!flex kick @usuario [razón opcional]`: Expulsa a un usuario.
*   `!flex ban @usuario [razón opcional]`: Banea a un usuario.
*   `!flex unban [ID del usuario] [razón opcional]`: Desbanea a un usuario (necesitas su ID).
*   `!flex mute @usuario [duración] [razón opcional]`: Silencia a un usuario.
    *   *Duraciones:* `s` (segundos), `m` (minutos), `h` (horas), `d` (días). Ejemplo: `10m`, `2h`, `1d`.
*   `!flex unmute @usuario [razón opcional]`: Quita el silencio a un usuario.
*   `!flex warn @usuario [razón]`: Envía una advertencia formal al usuario.

**Gestión de Reportes:**

*   `!flex reports [pendiente|resuelto|descartado|todos]`: Muestra reportes según su estado. Por defecto, muestra `pendiente`.

**Información:**

*   `!flex userinfo [@usuario/ID]`: Muestra información detallada del usuario.
*   `!flex serverinfo`: Muestra información detallada del servidor.

**Utilidades del Canal:**

*   `!flex clear [cantidad]`: Elimina un número específico de mensajes (máx. 100).
*   `!flex slowmode [segundos]`: Establece el modo lento en el canal actual (0 para desactivar).

**Gestión de Hilos:**

*   `!flex designarhilocanal #canal`: Designa un canal para permitir la creación de hilos gestionados.
*   `!flex quitarhilocanal #canal`: Remueve la designación de un canal para hilos.
*   `!flex crearhilo "Nombre del Hilo" [duración opcional] [notificar si/no]`: Crea un hilo en un canal designado.
    *   *Ejemplo:* `!flex crearhilo "Discusión sobre el evento X" 2d si`
*   `!flex cerrarhilo [mensaje opcional]`: Cierra manualmente el hilo actual (debe ser ejecutado dentro del hilo).

**Encuestas y Votaciones:**

*   `!flex createpoll "Pregunta" "Opción 1" "Opción 2" ... "Opción N"`: Crea una encuesta con hasta 10 opciones.
    *   Requiere permisos de `Gestionar Mensajes`.
    *   *Ejemplo:* `!flex createpoll "¿Cuál es tu color favorito?" "Rojo" "Verde" "Azul"`
*   `!flex closepoll [ID_del_mensaje_de_la_encuesta]`: Cierra una encuesta activa y muestra los resultados.
    *   Requiere permisos de `Gestionar Mensajes`.
    *   *Ejemplo:* `!flex closepoll 123456789012345678`

## ⚙️ Configuración Automática

Al iniciarse o al usar ciertos comandos, FlexBot puede crear automáticamente:

*   **Rol `Muted`**: Si no existe, se crea con permisos para no poder enviar mensajes ni hablar en canales de voz. El bot intentará aplicar estos permisos a todos los canales existentes.
*   **Categoría `Moderación`**: Si no existe, se crea para organizar canales relacionados con la moderación.
*   **Canal `#reportes`**: Si no existe (dentro de la categoría `Moderación`), se crea para recibir los reportes de los usuarios. Solo los moderadores y el bot tendrán acceso.

Asegúrate de que el bot tenga los permisos `Manage Roles` y `Manage Channels` para estas funciones.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si deseas mejorar FlexBot:

1.  Realiza un Fork del proyecto.
2.  Crea una nueva rama para tu característica (`git checkout -b feature/NuevaCaracteristica`).
3.  Realiza tus cambios y haz commit (`git commit -m 'Añade NuevaCaracteristica'`).
4.  Sube tus cambios a la rama (`git push origin feature/NuevaCaracteristica`).
5.  Abre un Pull Request.

Por favor, asegúrate de que tu código siga las convenciones generales del proyecto y esté debidamente documentado.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 💬 Soporte y Contacto

Si encuentras algún error, tienes preguntas o sugerencias:

1.  Abre un "Issue" en este repositorio de GitHub.
2.  Revisa la documentación y los issues existentes.

---

⭐ ¡Si FlexBot te resulta útil, no olvides darle una estrella en GitHub! ⭐
Desarrollado por R4F405.
