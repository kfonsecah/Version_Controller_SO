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
 🔹 user --admin <nombre> --new <nuevo>
 🔹 ls --user <actual> --owner <otro>
 🔹 commit --user <nombre>
 🔹 update --user <actual> --owner <otro>
 🔹 perm --user <nombre> --set <otro:read/write>
 🔹 help
 🔹 exit
══════════════════════════════════════════════════════
"""

def mostrar_banner():
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    print("🔹 SISTEMA DE CONTROL DE VERSIONES - Consola Interactiva 🔹")
    print("Escribe 'help' para ver los comandos disponibles.\n")

def mostrar_help():
    print(HELP_TEXT)

def procesar_comando(entrada):
    partes = entrada.strip().split()
    if not partes:
        return None, {}

    accion = partes[0].lower()
    args = {}
    i = 1
    while i < len(partes):
        if partes[i].startswith("--") and i + 1 < len(partes):
            clave = partes[i][2:]
            valor = partes[i + 1]
            args[clave] = valor
            i += 2
        else:
            i += 1
    return accion, args

def main():
    mostrar_banner()

    while True:
        entrada = input("> ").strip()
        if not entrada:
            continue

        accion, args = procesar_comando(entrada)

        if accion in ["exit", "salir"]:
            print("👋 Cerrando...")
            time.sleep(1)
            sys.exit()

        elif accion == "help":
            mostrar_help()

        elif accion == "repo" and "user" in args and "path" in args:
            crear_repositorio(args["user"], args["path"])

        elif accion == "user" and "admin" in args and "new" in args:
            crear_usuario_administrador(args["admin"], args["new"])

        elif accion == "ls" and "user" in args and "owner" in args:
            listar_archivos(args["user"], args["owner"])

        elif accion == "commit" and "user" in args:
            commit(args["user"])

        elif accion == "update" and "user" in args and "owner" in args:
            update(args["user"], args["owner"])

        elif accion == "perm" and "user" in args and "set" in args:
            try:
                objetivo, nivel = args["set"].split(":")
                asignar_permiso(args["user"], objetivo, nivel)
            except ValueError:
                print("❌ Usa el formato: --set otro:read o otro:write")

        else:
            print("❌ Comando no reconocido. Escribe 'help'.")

if __name__ == "__main__":
    main()
