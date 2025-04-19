# 🤖 Bot de Moderación para Discord

Un bot de Discord potente y fácil de usar, diseñado para ayudar en la moderación de servidores con múltiples funcionalidades.

## ✨ Características

### 📋 Sistema de Reportes
- Permite a los usuarios reportar comportamiento inadecuado
- Canal dedicado para la gestión de reportes
- Sistema de seguimiento y estado de reportes
- Acciones rápidas mediante reacciones

### 🛡️ Comandos de Moderación
- Silenciar usuarios
- Expulsar miembros
- Banear usuarios
- Sistema de anti-spam automático
- Gestión de roles y permisos

### 📊 Comandos de Información
- Información detallada de usuarios
- Estadísticas del servidor
- Sistema de ayuda dividido por niveles de acceso

## 🚀 Comandos Disponibles

### Comandos para Usuarios
```
!flex info    - Muestra los comandos disponibles para usuarios
!flex report  - Reporta a un usuario por comportamiento inadecuado
```

### Comandos para Moderadores
```
!flex info2      - Muestra los comandos de moderación
!flex kick       - Expulsa a un usuario
!flex ban        - Banea a un usuario
!flex unban      - Desbanea a un usuario
!flex mute       - Silencia a un usuario
!flex unmute     - Remueve el silencio de un usuario
!flex userinfo   - Muestra información detallada de un usuario
!flex serverinfo - Muestra información del servidor
!flex reports    - Gestiona los reportes
```

## 📥 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/TuUsuario/Bot_Discord_Moderacion_comandos.git
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## 🔑 Configuración del Bot en Discord

1. Ve a [Discord Developer Portal](https://discord.com/developers/applications)
2. Haz clic en "New Application" y dale un nombre a tu aplicación
3. En el menú lateral, selecciona "Bot"
4. Haz clic en "Add Bot" y confirma
5. Bajo el nombre del bot, encontrarás el botón "Reset Token" - haz clic y copia el token
6. En la sección "Privileged Gateway Intents", activa:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
7. Para invitar el bot a tu servidor:
   - Ve a la sección "OAuth2" > "URL Generator"
   - Selecciona los scopes: `bot` y `applications.commands`
   - Selecciona los permisos necesarios listados en la sección "🔐 Permisos Necesarios"
   - Usa la URL generada para invitar el bot a tu servidor

## ⚙️ Configuración del Archivo .env

1. Modifica el archivo `.env.example` en la raíz del proyecto y dejalo como `.env`
2. Añade tu token:
```env
DISCORD_TOKEN=tu_token_aqui
```

3. Ejecuta el bot:
```bash
python main.py
```

## 🔧 Configuración

El bot creará automáticamente:
- Canal de reportes
- Rol de silenciado
- Categoría de moderación

## 🛡️ Sistema de Reportes

### Cómo Reportar
1. Usa el comando `!flex report @usuario razón`
2. El reporte se enviará al canal de moderación
3. Los moderadores pueden:
   - ✅ Marcar como resuelto
   - ❌ Descartar reporte
   - 🔨 Tomar acciones de moderación

### Anti-Spam
- Detecta automáticamente spam (5 mensajes en 3 segundos)
- Silencia temporalmente a usuarios que spamean
- Los moderadores están exentos del sistema

## 📝 Gestión de Reportes

Los moderadores pueden ver los reportes usando:
```
!flex reports          - Muestra reportes pendientes
!flex reports resuelto - Muestra reportes resueltos
!flex reports todos    - Muestra todos los reportes
```

## 🔐 Permisos Necesarios

El bot necesita los siguientes permisos:
- Gestionar mensajes
- Gestionar roles
- Expulsar miembros
- Banear miembros
- Ver canales
- Enviar mensajes
- Gestionar canales
- Añadir reacciones

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:
1. Haz fork del proyecto
2. Crea una rama para tu característica
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙋‍♂️ Soporte

Si tienes preguntas o necesitas ayuda:
1. Abre un issue en GitHub
2. Revisa la documentación
3. Contacta con los mantenedores

## 🌟 Créditos

Desarrollado por R4F405

---
⭐ Si te gusta este proyecto, ¡no olvides darle una estrella en GitHub! 
