import json
import os
import shutil

class GestorUsuarios:
    USUARIOS_FILE = "data/usuarios.json"

    def __init__(self):
        # No necesita inicialización especial
        pass

    def cargar_usuarios(self):
        if not os.path.exists(self.USUARIOS_FILE):
            return {}
        with open(self.USUARIOS_FILE, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
            return json.loads(contenido) if contenido else {}

    def guardar_usuarios(self, usuarios):
        with open(self.USUARIOS_FILE, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=4)

    def crear_usuario(self, nombre):
        usuarios = self.cargar_usuarios()
        if nombre in usuarios:
            print(f"⚠️ El usuario '{nombre}' ya existe.")
            return False
        usuarios[nombre] = {
            "repositorio": None,
            "admin": False,
            "permisos": {}
        }
        self.guardar_usuarios(usuarios)
        print(f"✅ Usuario '{nombre}' creado.")
        return True

    def crear_usuario_administrador(self, admin, nuevo_usuario):
        usuarios = self.cargar_usuarios()
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
        self.guardar_usuarios(usuarios)
        print(f"✅ Usuario '{nuevo_usuario}' creado por '{admin}'.")
        return True

    def crear_copia_repositorio(self, origen_path, destino_path):
        if not os.path.exists(origen_path):
            print(f"❌ Repositorio de origen '{origen_path}' no existe.")
            return False
        if os.path.exists(destino_path):
            print(f"⚠️ El repositorio destino '{destino_path}' ya existe. Se sobrescribirá.")
            shutil.rmtree(destino_path)
        shutil.copytree(origen_path, destino_path)
        print(f"✅ Copia del repositorio creada en '{destino_path}'.")
        return True

    def asignar_permiso(self, propietario, visitante, permiso):
        usuarios = self.cargar_usuarios()

        if propietario not in usuarios or visitante not in usuarios:
            print("❌ El usuario no existe.")
            return False

        if permiso not in ["lectura", "escritura"]:
            print("❌ Permiso inválido. Usa 'lectura' o 'escritura'.")
            return False

        repo_propietario = usuarios[propietario].get("repositorio")
        if not repo_propietario:
            print("❌ El propietario no tiene un repositorio asignado.")
            return False

        # Asignar permiso al visitante en el repositorio del propietario (repo raíz)
        usuarios[propietario].setdefault("permisos", {})[visitante] = permiso

        # Crear repositorio del visitante si no tiene uno
        repo_visitante = usuarios[visitante].get("repositorio")
        if not repo_visitante:
            ruta_base = os.path.dirname(repo_propietario)
            ruta_visitante = os.path.join(ruta_base, visitante)

            exito = self.crear_copia_repositorio(repo_propietario, ruta_visitante)
            if not exito:
                print("❌ No se pudo crear el repositorio para el visitante.")
                return False

            usuarios[visitante]["repositorio"] = ruta_visitante

        # Obtener los permisos definidos en el repo raíz
        permisos_raiz = usuarios[propietario].get("permisos", {}).copy()
        permisos_raiz[propietario] = "escritura"  # el repo raíz se da permiso a sí mismo (solo para replicar en otros)

        for usuario_destino in permisos_raiz:
            if usuario_destino not in usuarios:
                continue
            repo_destino = usuarios[usuario_destino].get("repositorio")
            if not repo_destino:
                continue

            for otro_usuario, nivel in permisos_raiz.items():
                if usuario_destino == otro_usuario:
                    continue  # No se asigna a sí mismo

                # El propietario (repo raíz) siempre tiene escritura en los otros
                if otro_usuario == propietario:
                    usuarios[usuario_destino].setdefault("permisos", {})[propietario] = "escritura"
                else:
                    usuarios[usuario_destino].setdefault("permisos", {})[otro_usuario] = nivel

        self.guardar_usuarios(usuarios)
        print(f"✅ '{propietario}' otorgó '{permiso}' a '{visitante}' y replicó todos los permisos dinámicamente.")
        return True

    def tiene_permiso(self, usuario_actual, propietario, tipo):
        usuarios = self.cargar_usuarios()
        if usuario_actual == propietario:
            return True
        permisos = usuarios.get(propietario, {}).get("permisos", {})
        nivel = permisos.get(usuario_actual)
        if tipo == "lectura":
            return nivel in ["lectura", "escritura"]
        if tipo == "escritura":
            return nivel == "escritura"
        return False
