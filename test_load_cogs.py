import asyncio
import os
import discord
from discord.ext import commands
import json
from dotenv import load_dotenv

# Cargar variables de entorno (aunque no se usará el token para este test)
load_dotenv()

# Configuración mínima del bot para cargar extensiones
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_all_extensions():
    """Intenta cargar todas las extensiones en el directorio cogs."""
    cogs_loaded_successfully = True
    print("Iniciando prueba de carga de cogs...\n")

    # Asegurarse de que data/reports.json y data/warnings.json existan y tengan contenido JSON válido
    # Esto es para prevenir errores si los tests se corren antes de que el bot los cree.
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    files_to_initialize = {
        os.path.join(data_dir, 'reports.json'): {},
        os.path.join(data_dir, 'warnings.json'): {"users": {}} # warnings.json espera una estructura específica
    }

    for file_path, default_content in files_to_initialize.items():
        if not os.path.exists(file_path):
            print(f"Creando archivo JSON de prueba: {file_path}")
            with open(file_path, 'w') as f:
                json.dump(default_content, f, indent=4)
        else:
            # Verificar si el archivo está vacío o corrupto
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    if not content.strip():
                        raise ValueError("Archivo vacío")
                    json.loads(content) # Intentar parsear
            except (ValueError, json.JSONDecodeError):
                print(f"Archivo {file_path} vacío o corrupto. Inicializando con contenido por defecto.")
                with open(file_path, 'w') as f:
                    json.dump(default_content, f, indent=4)


    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('__'):
            extension_name = f'cogs.{filename[:-3]}'
            try:
                print(f"Intentando cargar: {extension_name}")
                await bot.load_extension(extension_name)
                print(f"Cargado exitosamente: {extension_name}\n")
            except commands.errors.ExtensionAlreadyLoaded:
                print(f"Ya cargado: {extension_name}\n")
            except Exception as e:
                print(f"Error al cargar {extension_name}: {e}\n")
                cogs_loaded_successfully = False

    if cogs_loaded_successfully:
        print("¡Todos los cogs se han cargado (o intentado cargar) exitosamente!")
    else:
        print("Algunos cogs fallaron al cargar.")

    return cogs_loaded_successfully

async def main():
    await load_all_extensions()
    # No es necesario iniciar el bot con bot.start() para este test

if __name__ == "__main__":
    asyncio.run(main())
