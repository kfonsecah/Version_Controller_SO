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

def puede_actualizar_permanente(usuario_actual, propietario, permiso, usuario_raiz):
    return usuario_actual == usuario_raiz or permiso == "escritura"

def obtener_ultimo_backup(path_versions):
    """Obtiene el nombre del último backup basado en timestamp o None si no hay backups."""
    if not os.path.exists(path_versions):
        return None
    backups = [
        d for d in os.listdir(path_versions)
        if d.startswith("backup_") and os.path.isdir(os.path.join(path_versions, d))
    ]
    if not backups:
        return None
    backups.sort(reverse=True)
    return backups[0]  # Devuelve solo el nombre

def update(usuario_actual):
    usuarios = gestor_usuarios.cargar_usuarios()
    if not usuarios:
        return False, "❌ No hay usuarios definidos."

    repo_usuario_actual = usuarios.get(usuario_actual, {}).get("repositorio")
    if not repo_usuario_actual:
        return False, "❌ Usuario sin repositorio asignado."

    usuario_raiz = list(usuarios.keys())[0]
    mejor_candidato = None

    for propietario, datos in usuarios.items():
        repo_propietario = datos.get("repositorio")
        if not repo_propietario:
            continue

        # Determinar permiso de usuario_actual sobre este repo
        permiso = "escritura" if propietario == usuario_actual else usuarios[propietario].get("permisos", {}).get(usuario_actual)


        if permiso not in ("lectura", "escritura"):
            continue  # No tiene acceso, ignorar

        versions_path = os.path.join(repo_propietario, "versions")
        if not os.path.exists(versions_path):
            continue

        backups = [
            d for d in os.listdir(versions_path)
            if d.startswith("backup_") and os.path.isdir(os.path.join(versions_path, d))
        ]

        for backup in backups:
            try:
                fecha = datetime.strptime(backup.replace("backup_", ""), "%Y%m%d%H%M%S")
            except:
                continue

            if (not mejor_candidato) or (fecha > mejor_candidato["fecha"]):
                mejor_candidato = {
                    "propietario": propietario,
                    "repo": repo_propietario,
                    "permiso": permiso,
                    "backup": backup,
                    "fecha": fecha
                }

    if not mejor_candidato:
        return False, "❌ No se encontró ningún backup accesible."

    print(f"[DEBUG] Backup más reciente: {mejor_candidato['backup']} de '{mejor_candidato['propietario']}'")

    perm_path = os.path.join(mejor_candidato["repo"], "permanente")
    destino = os.path.join(
        repo_usuario_actual,
        "permanente" if mejor_candidato["permiso"] == "lectura" else "temporal"
    )



    if os.path.exists(destino):
        shutil.rmtree(destino)
    os.makedirs(destino)

    for archivo in os.listdir(perm_path):
        src = os.path.join(perm_path, archivo)
        dst = os.path.join(destino, archivo)
        copiar_con_sobrescritura(src, dst)

    return True, f"✅ Update realizado desde '{mejor_candidato['propietario']}' hacia '{usuario_actual}' en '{mejor_candidato['permiso']}' ({mejor_candidato['backup']})"

