import os
from usuarios import cargar_usuarios, guardar_usuarios, crear_usuario, tiene_permiso

REPO_ROOT = "data/repositorio"

def inicializar_repositorio():
    if not os.path.exists(REPO_ROOT):
        os.makedirs(REPO_ROOT)
        print("📁 Carpeta raíz del repositorio creada.")

def crear_repositorio(usuario, ruta):
    usuarios = cargar_usuarios()

    if usuario not in usuarios:
        print(f"⚠️ Usuario '{usuario}' no existe. Creándolo como administrador...")
        crear_usuario(usuario)
        usuarios = cargar_usuarios()
        usuarios[usuario]["admin"] = True
        guardar_usuarios(usuarios)

    ruta = os.path.abspath(ruta.strip().replace('"', ''))

    if not ruta.endswith(usuario):
        repo_path = os.path.join(ruta, usuario)
    else:
        repo_path = ruta

    temp_path = os.path.join(repo_path, "temporal")
    perm_path = os.path.join(repo_path, "permanente")

    try:
        os.makedirs(temp_path, exist_ok=True)
        os.makedirs(perm_path, exist_ok=True)
    except OSError as e:
        print(f"❌ Error creando estructura del repositorio: {e}")
        return False

    usuarios[usuario]["repositorio"] = repo_path
    guardar_usuarios(usuarios)
    print(f"✅ Repositorio '{repo_path}' creado correctamente.")
    return True

def listar_archivos(usuario_actual, propietario):
    usuarios = cargar_usuarios()
    if propietario not in usuarios or not usuarios[propietario]["repositorio"]:
        print("❌ El usuario no tiene repositorio.")
        return

    if not tiene_permiso(usuario_actual, propietario, "lectura"):
        print("❌ No tienes permiso para ver este repositorio.")
        return

    repo_path = usuarios[propietario]["repositorio"]
    temp_path = os.path.join(repo_path, f"temporal_{usuario_actual}" if usuario_actual != propietario else "temporal")
    perm_path = os.path.join(repo_path, "permanente")

    print(f"\n📂 Repositorio de {propietario}: {repo_path}")
    print("📂 Carpetas: temporal / permanente")

    archivos_temporales = os.listdir(temp_path) if os.path.exists(temp_path) else []
    archivos_permanentes = os.listdir(perm_path)

    if archivos_temporales and not archivos_permanentes:
        print("⚠️ Hay archivos en 'temporal' que aún no han sido subidos con 'commit'.")

    while True:
        opcion = input("¿Ver 't'emporal, 'p'ermanente o 'salir'? ").lower()
        if opcion == "t":
            mostrar_archivos(temp_path)
        elif opcion == "p":
            mostrar_archivos(perm_path)
        elif opcion == "salir":
            break
        else:
            print("Comando inválido.")

def mostrar_archivos(ruta):
    if not os.path.exists(ruta):
        print(f"📂 La carpeta '{ruta}' no existe.")
        return
    archivos = os.listdir(ruta)
    if archivos:
        print(f"\n📄 Archivos en {ruta}:")
        for archivo in archivos:
            print(f" - {archivo}")
    else:
        print(f"📂 La carpeta '{ruta}' está vacía.")
