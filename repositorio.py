import os
import json
from usuarios import cargar_usuarios, guardar_usuarios, crear_usuario

REPO_ROOT = "data/repositorio"

def inicializar_repositorio():
    """Crea la carpeta raíz del repositorio si no existe."""
    if not os.path.exists(REPO_ROOT):
        os.makedirs(REPO_ROOT)
        print("📁 Carpeta del repositorio creada correctamente.")

def crear_repositorio(usuario, ruta):
    """Crea un repositorio y asigna el usuario como administrador si no existe."""
    usuarios = cargar_usuarios()

    # Si el usuario no existe, lo crea automáticamente como administrador
    if usuario not in usuarios:
        print(f"⚠️ El usuario '{usuario}' no existe. Creándolo como administrador...")
        crear_usuario(usuario)
        usuarios = cargar_usuarios()
        usuarios[usuario]["admin"] = True
        guardar_usuarios(usuarios)

    # Crear la estructura de carpetas en la ruta elegida
    if not os.path.exists(ruta):
        os.makedirs(ruta)

    repo_path = os.path.join(ruta, usuario)
    temp_path = os.path.join(repo_path, "temporal")
    perm_path = os.path.join(repo_path, "permanente")

    os.makedirs(temp_path, exist_ok=True)
    os.makedirs(perm_path, exist_ok=True)

    usuarios[usuario]["repositorio"] = repo_path
    guardar_usuarios(usuarios)

    print(f"✅ Repositorio '{repo_path}' creado con éxito. '{usuario}' ahora es ADMINISTRADOR.")
    return True


def listar_archivos(usuario):
    """Lista los archivos en el repositorio del usuario y permite explorar subcarpetas."""
    usuarios = cargar_usuarios()
    
    if usuario not in usuarios or not usuarios[usuario]["repositorio"]:
        print(f"❌ El usuario '{usuario}' no tiene un repositorio asignado.")
        return
    
    repo_path = usuarios[usuario]["repositorio"]
    temp_path = os.path.join(repo_path, "temporal")
    perm_path = os.path.join(repo_path, "permanente")

    archivos_repo = os.listdir(repo_path)
    print(f"\n📂 Repositorio de {usuario}: {repo_path}")
    print("📂 Carpetas disponibles:", archivos_repo)

    # Verificar si la carpeta temporal tiene archivos sin subir
    archivos_temporales = os.listdir(temp_path)
    archivos_permanentes = os.listdir(perm_path)

    if archivos_temporales and not archivos_permanentes:
        print("⚠️ Hay archivos en 'temporal' que aún no han sido subidos con 'commit'.")

    # Preguntar al usuario qué carpeta quiere explorar
    while True:
        opcion = input("\n🔹 ¿Quieres ver archivos en 'temporal' o 'permanente'? (t/p, salir para omitir): ").strip().lower()
        if opcion == "t":
            mostrar_archivos(temp_path)
        elif opcion == "p":
            mostrar_archivos(perm_path)
        elif opcion == "salir":
            break
        else:
            print("❌ Opción no válida. Escribe 't' para 'temporal', 'p' para 'permanente' o 'salir' para salir.")

def mostrar_archivos(ruta):
    """Muestra los archivos dentro de una carpeta específica."""
    archivos = os.listdir(ruta)
    if archivos:
        print(f"\n📄 Archivos en {ruta}:")
        for archivo in archivos:
            print(f"   - {archivo}")
    else:
        print(f"\n📂 La carpeta '{ruta}' está vacía.")
