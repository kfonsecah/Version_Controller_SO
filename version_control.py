import os
import shutil
from datetime import datetime
from usuarios import cargar_usuarios, tiene_permiso

def commit(usuario):
    usuarios = cargar_usuarios()
    repo_path = usuarios[usuario]["repositorio"]
    temp_path = os.path.join(repo_path, "temporal")
    perm_path = os.path.join(repo_path, "permanente")

    if not os.path.exists(temp_path) or not os.listdir(temp_path):
        print("⚠️ No hay archivos en 'temporal'.")
        return

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_dir = os.path.join(perm_path, f"backup_{timestamp}")
    os.makedirs(backup_dir)

    # Copiar archivos de permanente al backup
    for archivo in os.listdir(perm_path):
        src = os.path.join(perm_path, archivo)
        dst = os.path.join(backup_dir, archivo)
        if os.path.isfile(src):
            shutil.copy(src, dst)

    # Mover archivos de temporal a permanente
    for archivo in os.listdir(temp_path):
        shutil.move(os.path.join(temp_path, archivo), perm_path)

    print("✅ Commit realizado. Backup guardado en:", backup_dir)

def update(usuario_actual, propietario):
    usuarios = cargar_usuarios()

    if not tiene_permiso(usuario_actual, propietario, "lectura"):
        print("❌ No tienes permiso para hacer update.")
        return

    repo_path = usuarios[propietario]["repositorio"]
    perm_path = os.path.join(repo_path, "permanente")
    destino = os.path.join(repo_path, f"temporal_{usuario_actual}" if usuario_actual != propietario else "temporal")

    if os.path.exists(destino):
        shutil.rmtree(destino)
    os.makedirs(destino)

    for archivo in os.listdir(perm_path):
        ruta = os.path.join(perm_path, archivo)
        if os.path.isfile(ruta):
            shutil.copy(ruta, destino)

    print(f"✅ Update realizado desde '{propietario}' hacia '{usuario_actual}'.")
