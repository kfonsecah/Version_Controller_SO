import os
import shutil
from datetime import datetime
from usuarios import cargar_usuarios, tiene_permiso

def copiar_con_sobrescritura(src, dst):
    if os.path.exists(dst):
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        else:
            os.remove(dst)
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)

def commit(usuario):
    usuarios = cargar_usuarios()
    repo_path = usuarios[usuario].get("repositorio")

    if not repo_path:
        print("❌ El usuario no tiene un repositorio asignado.")
        return

    temp_path = os.path.join(repo_path, "temporal")
    perm_path = os.path.join(repo_path, "permanente")

    if not os.path.exists(temp_path) or not os.listdir(temp_path):
        print("⚠️ No hay archivos en 'temporal'.")
        return

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    versions_dir = os.path.join(repo_path, "versions")
    os.makedirs(versions_dir, exist_ok=True)
    backup_dir = os.path.join(versions_dir, f"backup_{timestamp}")
    os.makedirs(backup_dir)

    # Copiar archivos y carpetas de permanente al backup
    for archivo in os.listdir(perm_path):
        src = os.path.join(perm_path, archivo)
        dst = os.path.join(backup_dir, archivo)
        copiar_con_sobrescritura(src, dst)

    # Mover archivos de temporal a permanente
    for archivo in os.listdir(temp_path):
        src = os.path.join(temp_path, archivo)
        dst = os.path.join(perm_path, archivo)
        copiar_con_sobrescritura(src, dst)

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
        destino_final = os.path.join(destino, archivo)
        copiar_con_sobrescritura(ruta, destino_final)

    print(f"✅ Update realizado desde '{propietario}' hacia '{usuario_actual}'.")
