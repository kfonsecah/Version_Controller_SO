import json
import os

USUARIOS_FILE = "data/usuarios.json"

def cargar_usuarios():
    """Carga los usuarios desde el archivo JSON"""
    if not os.path.exists(USUARIOS_FILE):
        return {}
    with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
        contenido = f.read().strip()
        return json.loads(contenido) if contenido else {}

def guardar_usuarios(usuarios):
    """Guarda los usuarios en el archivo JSON"""
    with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=4)

def crear_usuario(nombre):
    """Crea un nuevo usuario"""
    usuarios = cargar_usuarios()
    if nombre in usuarios:
        print(f"⚠️ El usuario '{nombre}' ya existe.")
        return False
    usuarios[nombre] = {"permisos": {}, "repositorio": None, "admin": False}
    guardar_usuarios(usuarios)
    print(f"✅ Usuario '{nombre}' creado.")
    return True

def crear_usuario_administrador(admin, nuevo_usuario):
    """Crea un nuevo usuario solo si el creador tiene permisos de administrador."""
    usuarios = cargar_usuarios()

    if admin not in usuarios or not usuarios[admin].get("admin", False):
        print("❌ No tienes permisos de administrador para crear usuarios.")
        return False

    if nuevo_usuario in usuarios:
        print(f"⚠️ El usuario '{nuevo_usuario}' ya existe.")
        return False

    usuarios[nuevo_usuario] = {"permisos": {}, "repositorio": None}
    guardar_usuarios(usuarios)
    print(f"✅ Usuario '{nuevo_usuario}' creado por '{admin}'.")
    return True

def asignar_permiso(usuario, objetivo, permiso):
    """Asigna permisos a otro usuario."""
    usuarios = cargar_usuarios()

    if usuario not in usuarios:
        print(f"❌ El usuario '{usuario}' no existe.")
        return False

    if objetivo not in usuarios:
        print(f"❌ El usuario '{objetivo}' no existe y no se le pueden asignar permisos.")
        return False

    if permiso not in ["lectura", "escritura"]:
        print("❌ Tipo de permiso no válido. Usa 'lectura' o 'escritura'.")
        return False

    usuarios[usuario]["permisos"][objetivo] = permiso
    guardar_usuarios(usuarios)
    
    print(f"✅ Permiso '{permiso}' otorgado a '{objetivo}' por '{usuario}'.")
    return True

