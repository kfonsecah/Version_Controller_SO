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
 🔹 repo --user <nombre> --path <ruta>
     ➝ Crea un repositorio en una ubicación específica.

 🔹 user --admin <nombre> --new <nuevo>
     ➝ Crea un usuario (solo administradores pueden hacerlo).

 🔹 ls --user <nombre>
     ➝ Lista los archivos en el repositorio del usuario.

 🔹 commit --user <nombre>
     ➝ Guarda cambios de la carpeta temporal a la permanente.

 🔹 update --user <nombre>
     ➝ Restaura archivos de la permanente a la temporal.

 🔹 perm --user <nombre> --set <usuario:read/write>
     ➝ Asigna permisos a otro usuario.

 🔹 exit
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

        if accion in ["exit", "salir"]:
            print("\nSaliendo del sistema... 👋")
            time.sleep(1)
            sys.exit()

        elif accion in ["help", "--help"]:
            mostrar_help()

        elif accion in ["repo"] and "user" in args and "path" in args:
            crear_repositorio(args["user"], args["path"])

        elif accion in ["user"] and "admin" in args and "new" in args:
            crear_usuario_administrador(args["admin"], args["new"])

        elif accion in ["ls"] and "user" in args:
            listar_archivos(args["user"])

        elif accion in ["commit"] and "user" in args:
            commit(args["user"])

        elif accion in ["update"] and "user" in args:
            update(args["user"])

        elif accion in ["perm"] and "user" in args and "set" in args:
            try:
                objetivo, permiso = args["set"].split(":")
                asignar_permiso(args["user"], objetivo, permiso)
            except ValueError:
                print("❌ Formato incorrecto. Usa '--set usuario:read' o '--set usuario:write'")

        else:
            print("❌ Comando no reconocido. Escribe 'help' para ver la lista de comandos.")

if __name__ == "__main__":
    main()
