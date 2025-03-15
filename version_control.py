import os
import shutil
from datetime import datetime
from usuarios import cargar_usuarios

def commit(usuario):
    """Mueve archivos de temporal a permanente"""
    usuarios = cargar_usuarios()
    repo_path = usuarios[usuario]["repositorio"]
    temp_path = os.path.join(repo_path, "temporal")
    perm_path = os.path.join(repo_path, "permanente")

    if not os.listdir(temp_path):
        print("⚠️ No hay archivos para hacer commit.")
        return

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_dir = os.path.join(perm_path, f"backup_{timestamp}")
    os.makedirs(backup_dir)

    for archivo in os.listdir(perm_path):
        shutil.move(os.path.join(perm_path, archivo), backup_dir)

    for archivo in os.listdir(temp_path):
        shutil.move(os.path.join(temp_path, archivo), perm_path)

    print("✅ Commit realizado con éxito.")

def update(usuario):
    """Copia archivos de permanente a temporal"""
    usuarios = cargar_usuarios()
    repo_path = usuarios[usuario]["repositorio"]
    temp_path = os.path.join(repo_path, "temporal")
    perm_path = os.path.join(repo_path, "permanente")

    shutil.rmtree(temp_path, ignore_errors=True)
    os.makedirs(temp_path)

    for archivo in os.listdir(perm_path):
        shutil.copy(os.path.join(perm_path, archivo), temp_path)

    print("✅ Update realizado con éxito.")
