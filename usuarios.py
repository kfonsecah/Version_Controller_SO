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

def asignar_permiso(propietario, visitante, permiso):
    usuarios = cargar_usuarios()

    if propietario not in usuarios or visitante not in usuarios:
        print("❌ El usuario no existe.")
        return False

    if permiso not in ["lectura", "escritura"]:
        print("❌ Permiso inválido. Usa 'lectura' o 'escritura'.")
        return False

    if not usuarios[propietario].get("repositorio"):
        print("❌ Solo el propietario de un repositorio puede asignar permisos.")
        return False

    usuarios[propietario].setdefault("permisos", {})[visitante] = permiso
    guardar_usuarios(usuarios)
    print(f"✅ '{propietario}' otorgó '{permiso}' a '{visitante}'.")
    return True



def tiene_permiso(usuario_actual, propietario, tipo):
    usuarios = cargar_usuarios()
    if usuario_actual == propietario:
        return True
    permisos = usuarios.get(propietario, {}).get("permisos", {})
    nivel = permisos.get(usuario_actual)
    if tipo == "lectura":
        return nivel in ["lectura", "escritura"]
    if tipo == "escritura":
        return nivel == "escritura"
    return False

