import os
import shutil
from datetime import datetime
from usuarios import GestorUsuarios
import hashlib

gestor_usuarios = GestorUsuarios()

def hash_archivo(ruta):
    """Devuelve el hash SHA-256 de un archivo para comparar contenido."""
    h = hashlib.sha256()
    try:
        with open(ruta, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        print(f"[ERROR] No se pudo leer {ruta}: {e}")
        return None

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

def necesita_update(usuario_actual):
    """Determina si el usuario debe hacer update antes de hacer commit, revisando permanente y temporal."""
    usuarios = gestor_usuarios.cargar_usuarios()
    repo_usuario = usuarios.get(usuario_actual, {}).get("repositorio")
    if not repo_usuario:
        return False

    # 🔍 Construir conjunto de hashes del usuario desde permanente y temporal
    hash_usuario = {}
    for carpeta in ["permanente", "temporal"]:
        ruta = os.path.join(repo_usuario, carpeta)
        if os.path.exists(ruta):
            for archivo in os.listdir(ruta):
                abs_path = os.path.join(ruta, archivo)
                if os.path.isfile(abs_path):
                    hash_usuario[archivo] = hash_archivo(abs_path)

    for propietario, datos in usuarios.items():
        if propietario == usuario_actual:
            continue

        repo_otro = datos.get("repositorio")
        if not repo_otro:
            continue

        permiso = datos.get("permisos", {}).get(usuario_actual)
        if permiso not in ("lectura", "escritura"):
            continue

        perm_path_otro = os.path.join(repo_otro, "permanente")
        if not os.path.exists(perm_path_otro):
            continue

        for archivo in os.listdir(perm_path_otro):
            ruta_otro = os.path.join(perm_path_otro, archivo)
            if not os.path.isfile(ruta_otro):
                continue
            hash_otro = hash_archivo(ruta_otro)
            hash_usr = hash_usuario.get(archivo)
            if hash_usr is None or hash_usr != hash_otro:
                return True  # Hay un archivo nuevo o con contenido diferente

    return False

def commit(usuario):
    usuarios = gestor_usuarios.cargar_usuarios()
    repo_usuario = usuarios.get(usuario, {}).get("repositorio")
    if not repo_usuario:
        return False, "❌ El usuario no tiene un repositorio asignado."

    # Buscar a qué usuario pertenece realmente ese repositorio
    propietario = None
    for user, data in usuarios.items():
        if data.get("repositorio") == repo_usuario:
            propietario = user
            break

    if not propietario:
        return False, "❌ No se encontró el propietario del repositorio."

    # Verificar permiso de escritura
    if not gestor_usuarios.tiene_permiso(usuario, propietario, "escritura"):
        return False, "❌ No tienes permiso de escritura para hacer commit en este repositorio."

    # Verificar si necesita update
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

        return True, "✅ Commit realizado correctamente."

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

    archivos_usuario = set()
    perm_path_usuario = os.path.join(repo_usuario_actual, "permanente")
    if os.path.exists(perm_path_usuario):
        archivos_usuario = set(os.listdir(perm_path_usuario))

    for propietario, datos in usuarios.items():
        repo_propietario = datos.get("repositorio")
        if not repo_propietario or repo_propietario == repo_usuario_actual:
            continue

        permiso = "escritura" if propietario == usuario_actual else usuarios[propietario].get("permisos", {}).get(usuario_actual)
        if permiso not in ("lectura", "escritura"):
            continue

        perm_path_otro = os.path.join(repo_propietario, "permanente")
        if not os.path.exists(perm_path_otro):
            continue

        archivos_otro = set(os.listdir(perm_path_otro))
        nuevos_archivos = archivos_otro - archivos_usuario

        if nuevos_archivos:
            mejor_candidato = {
                "propietario": propietario,
                "repo": repo_propietario,
                "permiso": permiso,
                "nuevos": nuevos_archivos
            }
            break  # Si encontramos uno que tenga archivos que no tengo, actualizamos de inmediato

    if not mejor_candidato:
        return False, "✅ Ya tienes la versión más actualizada (basado en carpetas permanentes)."

    # Copiar solo archivos nuevos desde perm_path del otro repo
    perm_path_fuente = os.path.join(mejor_candidato["repo"], "permanente")
    destino = os.path.join(
        repo_usuario_actual,
        "permanente" if mejor_candidato["permiso"] == "lectura" else "temporal"
    )

    os.makedirs(destino, exist_ok=True)  # No borramos, solo creamos si no existe

    for archivo in mejor_candidato["nuevos"]:
        src = os.path.join(perm_path_fuente, archivo)
        dst = os.path.join(destino, archivo)
        copiar_con_sobrescritura(src, dst)

    return True, f"✅ Update completado. Tu repositorio ha quedado en la versión más reciente."

