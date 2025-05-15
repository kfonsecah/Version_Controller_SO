import json
import os

USUARIOS_FILE = "data/usuarios.json"

def cargar_usuarios():
    if not os.path.exists(USUARIOS_FILE):
        return {}
    with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
        contenido = f.read().strip()
        return json.loads(contenido) if contenido else {}

def guardar_usuarios(usuarios):
    with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=4)

def crear_usuario(nombre):
    usuarios = cargar_usuarios()
    if nombre in usuarios:
        print(f"⚠️ El usuario '{nombre}' ya existe.")
        return False
    usuarios[nombre] = {
        "repositorio": None,
        "admin": False,
        "permisos": {}  # ejemplo: {"usuarioA": "lectura", "usuarioB": "escritura"}
    }
    guardar_usuarios(usuarios)
    print(f"✅ Usuario '{nombre}' creado.")
    return True

def crear_usuario_administrador(admin, nuevo_usuario):
    usuarios = cargar_usuarios()
    if not usuarios.get(admin, {}).get("admin", False):
        print("❌ No tienes permisos de administrador.")
        return False
    if nuevo_usuario in usuarios:
        print("⚠️ El usuario ya existe.")
        return False
    usuarios[nuevo_usuario] = {
        "repositorio": None,
        "admin": False,
        "permisos": {}
    }
    guardar_usuarios(usuarios)
    print(f"✅ Usuario '{nuevo_usuario}' creado por '{admin}'.")
    return True

def asignar_permiso(usuario, objetivo, permiso):
    usuarios = cargar_usuarios()
    if usuario not in usuarios or objetivo not in usuarios:
        print("❌ Usuario no válido.")
        return False
    if permiso not in ["lectura", "escritura"]:
        print("❌ Permiso no válido. Usa 'lectura' o 'escritura'")
        return False
    usuarios[usuario]["permisos"][objetivo] = permiso
    guardar_usuarios(usuarios)
    print(f"✅ '{usuario}' ahora tiene permiso '{permiso}' sobre '{objetivo}'.")
    return True

def tiene_permiso(usuario_actual, propietario, tipo):
    """
    Verifica si el usuario_actual tiene permiso 'lectura' o 'escritura' sobre el repositorio del propietario.
    """
    usuarios = cargar_usuarios()
    if usuario_actual == propietario:
        return True  # siempre tiene acceso total a su propio repo
    permisos = usuarios.get(usuario_actual, {}).get("permisos", {})
    nivel = permisos.get(propietario)
    if tipo == "lectura":
        return nivel in ["lectura", "escritura"]
    if tipo == "escritura":
        return nivel == "escritura"
    return False
