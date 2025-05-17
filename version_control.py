import os
import shutil
from datetime import datetime
from usuarios import GestorUsuarios

gestor_usuarios = GestorUsuarios()

def copiar_con_sobrescritura(src, dst):
    """Copia un archivo o carpeta de src a dst, sobrescribiendo dst si existe."""
    if os.path.exists(dst):
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        else:
            os.remove(dst)
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)

def obtener_ultimo_backup(path_versions):
    """Obtiene el nombre del último backup basado en timestamp o None si no hay backups."""
    if not os.path.exists(path_versions):
        return None
    backups = [d for d in os.listdir(path_versions)
               if d.startswith("backup_") and os.path.isdir(os.path.join(path_versions, d))]
    if not backups:
        return None
    backups.sort(reverse=True)
    return backups[0]

def necesita_update(usuario):
    """Determina si el usuario debe hacer update antes de commit."""
    usuarios = gestor_usuarios.cargar_usuarios()
    repo_usuario = usuarios.get(usuario, {}).get("repositorio")
    if not repo_usuario:
        return False

    propietario = None
    for user, data in usuarios.items():
        if data.get("repositorio") == repo_usuario:
            propietario = user
            break

    if propietario is None:
        return False

    repo_propietario = usuarios[propietario]["repositorio"]
    versiones_propietario = os.path.join(repo_propietario, "versions")
    versiones_usuario = os.path.join(repo_usuario, "versions")

    ultimo_backup_prop = obtener_ultimo_backup(versiones_propietario)
    ultimo_backup_usr = obtener_ultimo_backup(versiones_usuario)

    if ultimo_backup_prop is None:
        return False
    if ultimo_backup_usr is None:
        return True
    return ultimo_backup_usr < ultimo_backup_prop

def commit(usuario):
    usuarios = gestor_usuarios.cargar_usuarios()
    repo_usuario = usuarios.get(usuario, {}).get("repositorio")
    if not repo_usuario:
        return False, "❌ El usuario no tiene un repositorio asignado."

    propietario = None
    for user, data in usuarios.items():
        if data.get("repositorio") == repo_usuario:
            propietario = user
            break

    if propietario is None:
        return False, "❌ No se encontró el propietario del repositorio."

    if not gestor_usuarios.tiene_permiso(usuario, propietario, "escritura"):
        return False, "❌ No tienes permiso de escritura para hacer commit en este repositorio."

    if necesita_update(usuario):
        return False, "⚠️ Debes hacer update antes de poder hacer commit."

    temp_path = os.path.join(repo_usuario, "temporal")
    perm_path = os.path.join(repo_usuario, "permanente")

    if not os.path.exists(temp_path) or not os.listdir(temp_path):
        return False, "⚠️ No hay archivos en 'temporal'."

    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        versions_dir = os.path.join(repo_usuario, "versions")
        os.makedirs(versions_dir, exist_ok=True)
        backup_dir = os.path.join(versions_dir, f"backup_{timestamp}")
        os.makedirs(backup_dir)

        for archivo in os.listdir(perm_path):
            src = os.path.join(perm_path, archivo)
            dst = os.path.join(backup_dir, archivo)
            copiar_con_sobrescritura(src, dst)

        for archivo in os.listdir(temp_path):
            src = os.path.join(temp_path, archivo)
            dst = os.path.join(perm_path, archivo)
            copiar_con_sobrescritura(src, dst)

        shutil.rmtree(temp_path)
        os.makedirs(temp_path)

        return True, f"✅ Commit realizado. Backup guardado en: {backup_dir}"

    except Exception as e:
        return False, f"❌ Error durante commit: {e}"

# Función auxiliar para obtener todos los repositorios accesibles para un usuario
def obtener_repositorios_accesibles(usuario):
    usuarios = gestor_usuarios.cargar_usuarios()
    repos = []

    # Repositorio propio
    repo_propio = usuarios.get(usuario, {}).get("repositorio")
    if repo_propio:
        repos.append((usuario, repo_propio))

    # Repositorios de otros usuarios que otorgaron permiso
    for otro_user, data in usuarios.items():
        if otro_user == usuario:
            continue
        permisos = data.get("permisos", {})
        nivel = permisos.get(usuario)
        if nivel in ["lectura", "escritura"]:
            repo_otro = data.get("repositorio")
            if repo_otro:
                repos.append((otro_user, repo_otro))

    return repos

# Función auxiliar para obtener el repositorio con backup más reciente
def obtener_repositorio_mas_reciente(repos):
    ultimo_backup_global = None
    repo_mas_reciente = None
    propietario_mas_reciente = None

    for propietario, repo_path in repos:
        versions_dir = os.path.join(repo_path, "versions")
        ultimo_backup = obtener_ultimo_backup(versions_dir)
        if ultimo_backup is None:
            continue
        if (ultimo_backup_global is None) or (ultimo_backup > ultimo_backup_global):
            ultimo_backup_global = ultimo_backup
            repo_mas_reciente = repo_path
            propietario_mas_reciente = propietario

    return propietario_mas_reciente, repo_mas_reciente

def update(usuario_actual):
    usuarios = gestor_usuarios.cargar_usuarios()
    repo_usuario_actual = usuarios.get(usuario_actual, {}).get("repositorio")
    if not repo_usuario_actual:
        return False, "❌ Usuario sin repositorio asignado."

    candidatos = []

    # Buscar todos los repositorios a los que usuario_actual tiene acceso
    for propietario, datos in usuarios.items():
        repo_propietario = datos.get("repositorio")
        if not repo_propietario:
            continue

        # Si es el mismo usuario, siempre incluir su repo
        if propietario == usuario_actual:
            pass
        else:
            # Si no es el mismo, verificar si propietario le dio permiso a usuario_actual
            permisos = datos.get("permisos", {})
            permiso_usuario = permisos.get(usuario_actual)
            if permiso_usuario not in ("lectura", "escritura"):
                continue  # No tiene permiso para leer este repo, no lo consideramos

        # Obtener último backup de ese repositorio
        versions_path = os.path.join(repo_propietario, "versions")
        ultimo_backup = obtener_ultimo_backup(versions_path)
        if not ultimo_backup:
            continue  # Sin backups, ignorar

        # Agregar candidato (propietario, ruta repo, timestamp backup)
        candidatos.append((propietario, repo_propietario, ultimo_backup))

    if not candidatos:
        return False, "❌ No hay repositorios accesibles con backups para actualizar."

    # Ordenar candidatos por timestamp de backup más reciente primero (cadena ordenable lexicográficamente)
    candidatos.sort(key=lambda x: x[2], reverse=True)

    mejor_propietario, repo_fuente, mejor_backup = candidatos[0]

    # Ruta permanente del repositorio fuente
    perm_path = os.path.join(repo_fuente, "permanente")

    # Carpeta temporal destino del usuario actual
    temporal_destino = os.path.join(repo_usuario_actual, f"temporal_{usuario_actual}" if usuario_actual != mejor_propietario else "temporal")

    # Limpiar temporal destino antes de copiar
    if os.path.exists(temporal_destino):
        shutil.rmtree(temporal_destino)
    os.makedirs(temporal_destino)

    # Copiar archivos permanentes al temporal destino
    for archivo in os.listdir(perm_path):
        src = os.path.join(perm_path, archivo)
        dst = os.path.join(temporal_destino, archivo)
        copiar_con_sobrescritura(src, dst)

    return True, f"✅ Update realizado desde '{mejor_propietario}' hacia '{usuario_actual}'."
