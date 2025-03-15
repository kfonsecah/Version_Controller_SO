import os
import sys
import time
from usuarios import crear_usuario_administrador, asignar_permiso
from repositorio import crear_repositorio, listar_archivos
from version_control import commit, update

BANNER = """
███████╗ ██████╗███╗   ██╗██████╗ ███████╗██████╗ ███████╗███████╗
██╔════╝██╔════╝████╗  ██║██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝
█████╗  ██║     ██╔██╗ ██║██║  ██║█████╗  ██████╔╝███████╗█████╗  
██╔══╝  ██║     ██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗╚════██║██╔══╝  
███████╗╚██████╗██║ ╚████║██████╔╝███████╗██║  ██║███████║███████╗
╚══════╝ ╚═════╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝
"""

HELP_TEXT = """
══════════════════════════════════════════════════════
 📌 COMANDOS DISPONIBLES:
 ------------------------------------------------------
 🔹 crear_repositorio --usuario <nombre> --ruta <ruta>
     ➝ Crea un repositorio en una ubicación específica.

 🔹 crear_usuario --admin <nombre> --usuario <nuevo>
     ➝ Crea un usuario (solo administradores pueden hacerlo).

 🔹 listar --usuario <nombre>
     ➝ Lista los archivos en el repositorio del usuario.

 🔹 commit --usuario <nombre>
     ➝ Guarda cambios de la carpeta temporal a la permanente.

 🔹 update --usuario <nombre>
     ➝ Restaura archivos de la permanente a la temporal.

 🔹 asignar_permiso --usuario <nombre> --permiso <usuario:lectura/escritura>
     ➝ Asigna permisos a otro usuario.

 🔹 salir
     ➝ Cierra el sistema.
══════════════════════════════════════════════════════
"""

def mostrar_banner():
    """Limpia pantalla y muestra el banner."""
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    print("🔹 SISTEMA DE CONTROL DE VERSIONES - Consola Interactiva 🔹")
    print("Escribe 'help' para ver los comandos disponibles.\n")

def mostrar_help():
    """Muestra la lista de comandos disponibles."""
    print(HELP_TEXT)

def procesar_comando(entrada):
    """Convierte la entrada en un diccionario de argumentos correctamente."""
    partes = entrada.strip().split()

    if not partes:
        return None, {}

    accion = partes[0].lower()
    args = {}

    try:
        i = 1
        while i < len(partes):
            if partes[i].startswith("--") and i + 1 < len(partes):
                clave = partes[i][2:]  # Quita '--' del argumento
                valor = partes[i + 1]
                args[clave] = valor
                i += 2
            else:
                i += 1
    except IndexError:
        print("❌ Error en el formato del comando. Usa 'help' para ver los comandos disponibles.")
        return None, {}

    return accion, args

def main():
    mostrar_banner()

    while True:
        entrada = input("\n> ").strip()

        if not entrada:
            continue

        accion, args = procesar_comando(entrada)

        if not accion:
            continue

        if accion in ["salir", "exit"]:
            print("\nSaliendo del sistema... 👋")
            time.sleep(1)
            sys.exit()

        elif accion in ["help", "--help"]:
            mostrar_help()

        elif accion == "crear_repositorio" and "usuario" in args and "ruta" in args:
            crear_repositorio(args["usuario"], args["ruta"])

        elif accion == "crear_usuario" and "admin" in args and "usuario" in args:
            crear_usuario_administrador(args["admin"], args["usuario"])

        elif accion == "listar" and "usuario" in args:
            listar_archivos(args["usuario"])

        elif accion == "commit" and "usuario" in args:
            commit(args["usuario"])

        elif accion == "update" and "usuario" in args:
            update(args["usuario"])

        elif accion == "asignar_permiso" and "usuario" in args and "permiso" in args:
            try:
                objetivo, permiso = args["permiso"].split(":")
                asignar_permiso(args["usuario"], objetivo, permiso)
            except ValueError:
                print("❌ Error en el formato del permiso. Usa: --permiso usuario:lectura o usuario:escritura")

    else:
        print("❌ Comando no reconocido. Escribe 'help' para ver la lista de comandos.")

if __name__ == "__main__":
    main()
