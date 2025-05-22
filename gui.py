import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
from usuarios import GestorUsuarios
from repositorio import crear_repositorio
from version_control import commit, update
import shutil

class GitGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Control de Versiones - Sistemas Operativos")
        self.geometry("1080x640")
        self.usuario_actual = tk.StringVar()
        self.repo_actual = tk.StringVar()
        self.gestor_usuarios = GestorUsuarios()
        self.usuarios = self.gestor_usuarios.cargar_usuarios()

        self._build_layout()

    def _build_permisos_tab(self):
        frame = ttk.LabelFrame(self.sidebar, text="🔑 Asignar permisos")
        frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(frame, text="Usuario destino:").pack(anchor='w')
        self.perm_user = ttk.Combobox(frame, state="readonly")
        self.perm_user['values'] = list(self.usuarios.keys())
        self.perm_user.pack(fill='x', pady=2)

        ttk.Label(frame, text="Tipo de permiso:").pack(anchor='w')
        self.perm_tipo = ttk.Combobox(frame, state="readonly")
        self.perm_tipo['values'] = ["lectura", "escritura"]
        self.perm_tipo.pack(fill='x', pady=2)

        ttk.Button(frame, text="Asignar permiso", command=self._asignar_permiso_app).pack(fill='x', pady=5)
        
    def _obtener_propietario_raiz(self, ruta_repo_actual, usuario):
    # Recorremos todos los usuarios
        for posible_propietario, datos in self.usuarios.items():
            ruta_repo_propietario = datos.get("repositorio")
            if not ruta_repo_propietario:
                continue

            # El propietario original es quien tiene una ruta distinta pero ha otorgado permisos a este usuario
            permisos = datos.get("permisos", {})
            if ruta_repo_propietario != ruta_repo_actual and usuario in permisos:
                return posible_propietario
        return usuario  # Si no se encontró otro, asumimos que él es el propietario

    def _crear_archivo_temporal(self):
        temp_path, _ = self._get_paths()
        if not temp_path:
            return

        usuario = self.usuario_actual.get()
        ruta_repo = self.repo_actual.get()

        # Verificar permisos de escritura
        propietario = self._obtener_propietario_raiz(ruta_repo, usuario)
        if not self.gestor_usuarios.tiene_permiso(usuario, propietario, "escritura"):
            return messagebox.showerror("Permiso denegado", "No tienes permiso de escritura para este repositorio.")

        nuevo_nombre = simpledialog.askstring("Nuevo archivo", "Nombre del archivo:")
        if not nuevo_nombre:
            return

        ruta_base = temp_path
        seleccion = self.tree_temp.selection()

        if seleccion:
            nodo = seleccion[0]
            texto = self.tree_temp.item(nodo, "text")
            if texto.startswith("📁"):
                nombres = []
                while nodo:
                    nombres.insert(0, self.tree_temp.item(nodo, "text").replace("📁 ", "").replace("📄 ", ""))
                    nodo = self.tree_temp.parent(nodo)
                ruta_base = os.path.join(temp_path, *nombres)

        ruta = os.path.join(ruta_base, nuevo_nombre)
        if os.path.exists(ruta):
            return messagebox.showerror("Error", "Ya existe un archivo con ese nombre.")
        try:
            with open(ruta, "w") as f:
                f.write("")  # Archivo vacío
            self._mostrar_archivos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el archivo: {e}")



    def _renombrar_archivo_temporal(self, event):
        item = self.tree_temp.identify_row(event.y)
        if not item:
            return

        usuario = self.usuario_actual.get()
        ruta_repo = self.repo_actual.get()

        # Verificar que el usuario tiene permisos de escritura
        propietario = self._obtener_propietario_raiz(ruta_repo, usuario)
        if not self.gestor_usuarios.tiene_permiso(usuario, propietario, "escritura"):
            return messagebox.showerror("Permiso denegado", "No tienes permiso de escritura para este repositorio.")

        antiguo = self.tree_temp.item(item, "text").replace("📄 ", "").replace("📁 ", "")
        temp_path, _ = self._get_paths()
        ruta_antigua = os.path.join(temp_path, antiguo)

        nuevo = simpledialog.askstring("Renombrar archivo", "Nuevo nombre:", initialvalue=antiguo)
        if not nuevo:
            return

        ruta_nueva = os.path.join(temp_path, nuevo)
        try:
            os.rename(ruta_antigua, ruta_nueva)
            self._mostrar_archivos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo renombrar: {e}")
    
    def _crear_carpeta_temporal(self):
        temp_path, _ = self._get_paths()
        if not temp_path:
            return

        usuario = self.usuario_actual.get()
        ruta_repo = self.repo_actual.get()
        propietario = self._obtener_propietario_raiz(ruta_repo, usuario)
        if not self.gestor_usuarios.tiene_permiso(usuario, propietario, "escritura"):
            return messagebox.showerror("Permiso denegado", "No tienes permiso de escritura para este repositorio.")

        nueva_carpeta = simpledialog.askstring("Crear carpeta", "Nombre de la nueva carpeta:")
        if not nueva_carpeta:
            return

        ruta = os.path.join(temp_path, nueva_carpeta)
        if os.path.exists(ruta):
            return messagebox.showerror("Error", "Ya existe una carpeta con ese nombre.")

        try:
            os.makedirs(ruta)
            self._mostrar_archivos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la carpeta: {e}")
            
    def _eliminar_archivo_perm(self, event=None):
        item = self.tree_perm.focus()
        if not item:
            return messagebox.showwarning("Sin selección", "Seleccione un archivo o carpeta para eliminar.")

        nombre = self.tree_perm.item(item, "text").replace("📄 ", "").replace("📁 ", "")
        _, perm_path = self._get_paths()
        ruta = os.path.join(perm_path, nombre)

        if not os.path.exists(ruta):
            return messagebox.showerror("Error", "El archivo o carpeta no existe.")

        # Verificación de permisos de escritura
        usuario = self.usuario_actual.get()
        ruta_repo = self.repo_actual.get()
        propietario = self._obtener_propietario_raiz(ruta_repo, usuario)

        if not self.gestor_usuarios.tiene_permiso(usuario, propietario, "escritura"):
            return messagebox.showerror("Permiso denegado", "No tienes permiso de escritura para eliminar este archivo o carpeta.")

        confirmar = messagebox.askyesno("Confirmar eliminación", f"¿Deseas eliminar '{nombre}' permanentemente?")
        if not confirmar:
            return

        try:
            if os.path.isdir(ruta):
                shutil.rmtree(ruta)
            else:
                os.remove(ruta)
            messagebox.showinfo("Eliminado", f"'{nombre}' se eliminó correctamente.")
            self._mostrar_archivos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {e}")



    def _build_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ttk.Frame(self, width=250)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.content = ttk.Frame(self)
        self.content.grid(row=0, column=1, sticky="nsew")

        self._build_sidebar()
        self._build_main_content()
        self._build_permisos_tab()

    def _asignar_permiso_app(self):
        desde = self.usuario_actual.get()
        hacia = self.perm_user.get()
        tipo = self.perm_tipo.get()

        if not (desde and hacia and tipo):
            return messagebox.showerror("Error", "Todos los campos son obligatorios.")

        if desde == hacia:
            return messagebox.showerror("Error", "No puedes asignarte permisos a ti mismo.")

        self.gestor_usuarios.asignar_permiso(desde, hacia, tipo)
        messagebox.showinfo("Permiso asignado", f"{desde} dio permiso '{tipo}' a {hacia}.")

        # Recargar repositorios tras asignar permiso, para actualizar la lista
        self._recargar_repos(desde)

    def _build_sidebar(self):
        
        ttk.Label(self.sidebar, text="👤 Usuario activo").pack(pady=(10, 0))
        self.combo_usuario = ttk.Combobox(self.sidebar, state="readonly")
        self.combo_usuario['values'] = list(self.usuarios.keys())
        self.combo_usuario.pack(padx=10, fill='x')
        self.combo_usuario.bind("<<ComboboxSelected>>", self._on_user_selected)

        ttk.Label(self.sidebar, text="📁 Repositorios").pack(pady=(20, 0))
        self.list_repos = tk.Listbox(self.sidebar, height=10)
        self.list_repos.pack(padx=10, pady=5, fill='both', expand=True)
        scroll_x = tk.Scrollbar(self.sidebar, orient='horizontal', command=self.list_repos.xview)
        self.list_repos.config(xscrollcommand=scroll_x.set)
        scroll_x.pack(fill='x', padx=10)

        self.list_repos.bind("<<ListboxSelect>>", self._on_repo_selected)

        ttk.Button(self.sidebar, text="➕ Crear nuevo repo", command=self._crear_nuevo_repositorio).pack(pady=(10, 5), padx=10, fill='x')

        ttk.Separator(self.sidebar).pack(pady=10, fill='x')
        ttk.Label(self.sidebar, text="➕ Crear nuevo usuario").pack()
        self.entry_nuevo_user = ttk.Entry(self.sidebar)
        self.entry_nuevo_user.bind("<Return>", lambda event: self._crear_usuario_app())
        self.entry_nuevo_user.pack(padx=10, fill='x')
        ttk.Button(self.sidebar, text="Crear usuario", command=self._crear_usuario_app).pack(padx=10, pady=5, fill='x')

    def _build_main_content(self):
        frame_btns = ttk.Frame(self.content)
        frame_btns.pack(fill='x', pady=10)

        frame_archivos = ttk.Frame(self.content)
        frame_archivos.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Label(frame_archivos, text="📂 Temporal").grid(row=0, column=0)
        ttk.Label(frame_archivos, text="📂 Permanente").grid(row=0, column=1)

        self.tree_temp = ttk.Treeview(frame_archivos)
        self.tree_perm = ttk.Treeview(frame_archivos)

        self.tree_temp.heading("#0", text="📂 Temporal")
        self.tree_perm.heading("#0", text="📂 Permanente")

        self.tree_temp.grid(row=1, column=0, sticky="nsew", padx=5)
        self.tree_perm.grid(row=1, column=1, sticky="nsew", padx=5)
        self.tree_temp.bind("<Double-Button-1>", self._renombrar_archivo_temporal)

        frame_archivos.grid_rowconfigure(1, weight=1)
        frame_archivos.grid_columnconfigure(0, weight=1)
        frame_archivos.grid_columnconfigure(1, weight=1)

        ttk.Button(frame_archivos, text="➕ Crear archivo en Temporal", command=self._crear_archivo_temporal).grid(row=2, column=0, pady=5)
        ttk.Button(frame_archivos, text="📁 Crear carpeta en Temporal", command=self._crear_carpeta_temporal).grid(row=3, column=0, pady=5)
        ttk.Button(frame_btns, text="🔃 Update", command=self._update).pack(side='left', padx=5)
        ttk.Button(frame_btns, text="💾 Commit", command=self._commit).pack(side='left', padx=5)
        ttk.Button(frame_btns, text="📦 Ver Backups", command=self._ver_backups).pack(side='left', padx=5)
        ttk.Button(frame_btns, text="🗑️ Eliminar del Permanente", command=self._eliminar_archivo_perm).pack(side='left', padx=5)


    def _on_user_selected(self, event=None):
        usuario = self.combo_usuario.get()
        self.usuario_actual.set(usuario)
        self._recargar_repos(usuario)

    def _recargar_repos(self, usuario):
        self.list_repos.delete(0, tk.END)
        self.usuarios = self.gestor_usuarios.cargar_usuarios()

        # Lista para evitar rutas duplicadas
        rutas_agregadas = set()

        # Agregar repositorio propio del usuario activo
        repo_propio = self.usuarios.get(usuario, {}).get("repositorio")
        if repo_propio and repo_propio not in rutas_agregadas:
            self.list_repos.insert(tk.END, repo_propio)
            rutas_agregadas.add(repo_propio)

        # Agregar repositorios asignados por otros usuarios (las copias individuales del visitante)
        for otro_user, data in self.usuarios.items():
            if otro_user == usuario:
                continue
            permisos = data.get("permisos", {})
            if usuario in permisos:
                repo_visitante = self.usuarios.get(usuario, {}).get("repositorio")
                if repo_visitante and repo_visitante not in rutas_agregadas:
                    self.list_repos.insert(tk.END, repo_visitante)
                    rutas_agregadas.add(repo_visitante)

    def _on_repo_selected(self, event=None):
        seleccion = self.list_repos.curselection()
        if seleccion:
            path = self.list_repos.get(seleccion[0])
            self.repo_actual.set(path)
            self._mostrar_archivos()

    def _crear_nuevo_repositorio(self):
        usuario = self.usuario_actual.get()
        if not usuario:
            return messagebox.showerror("Error", "Seleccione un usuario activo")
        path = filedialog.askdirectory(title="Selecciona carpeta para el repositorio")
        if not path:
            return
        crear_repositorio(usuario, path)
        self._recargar_repos(usuario)
        self.repo_actual.set(path)
        self._mostrar_archivos()
        messagebox.showinfo("Éxito", "Repositorio creado correctamente")
        

    def _crear_usuario_app(self):
        nuevo = self.entry_nuevo_user.get().strip()
        if not nuevo:
            return messagebox.showerror("Error", "Debes escribir un nombre.")
        usuarios = self.gestor_usuarios.cargar_usuarios()
        if nuevo in usuarios:
            return messagebox.showerror("Error", "Ese usuario ya existe.")

        self.gestor_usuarios.crear_usuario(nuevo)
        self.usuarios = self.gestor_usuarios.cargar_usuarios()
        self.combo_usuario['values'] = list(self.usuarios.keys())
        self.perm_user['values'] = list(self.usuarios.keys())
        messagebox.showinfo("Éxito", f"Usuario '{nuevo}' creado.")
        self.entry_nuevo_user.delete(0, tk.END)

    def _get_paths(self):
        base = self.repo_actual.get()
        if not base:
            return None, None
        temp = os.path.join(base, "temporal")
        perm = os.path.join(base, "permanente")
        return temp, perm

    def _mostrar_archivos(self):
        temp, perm = self._get_paths()
        if not temp or not perm:
            return

        self.tree_temp.delete(*self.tree_temp.get_children())
        self.tree_perm.delete(*self.tree_perm.get_children())

        def agregar_elementos(tree, path, padre=""):
            if not os.path.exists(path):
                return
            for nombre in os.listdir(path):
                ruta = os.path.join(path, nombre)
                if os.path.isdir(ruta):
                    nodo = tree.insert(padre, "end", text=f"📁 {nombre}", open=False)
                    agregar_elementos(tree, ruta, nodo)
                else:
                    tree.insert(padre, "end", text=f"📄 {nombre}")

        agregar_elementos(self.tree_temp, temp)
        agregar_elementos(self.tree_perm, perm)

    def _commit(self):
        user = self.usuario_actual.get()
        if not user:
            messagebox.showerror("Error", "No hay usuario activo seleccionado.")
            return

        exito, mensaje = commit(user)
        self._mostrar_archivos()

        if exito:
            messagebox.showinfo("Commit", mensaje)
        else:
            messagebox.showerror("Error", mensaje)

    def _update(self):
        user1 = self.usuario_actual.get()
        if not user1:
            return
        success, message = update(user1)  # solo 1 argumento
        self._mostrar_archivos()
        if success:
            messagebox.showinfo("Update", message)
        else:
            messagebox.showerror("Error", message)

    def _ver_backups(self):
        repo = self.repo_actual.get()
        versions_dir = os.path.join(repo, "versions")
        if not os.path.exists(versions_dir):
            return messagebox.showinfo("Backups", "No hay versiones disponibles.")

        backups = sorted(
            [d for d in os.listdir(versions_dir) if d.startswith("backup_") and os.path.isdir(os.path.join(versions_dir, d))],
            reverse=True
        )
        if not backups:
            return messagebox.showinfo("Backups", "No hay versiones guardadas.")

        win = tk.Toplevel(self)
        win.title("Backups disponibles")
        lista = tk.Listbox(win, width=60)
        lista.pack(padx=10, pady=10)
        for b in backups:
            lista.insert(tk.END, b)

        def abrir_backup(event):
            seleccion = lista.curselection()
            if not seleccion:
                return
            backup_nombre = lista.get(seleccion[0])
            backup_path = os.path.join(versions_dir, backup_nombre)
            self._mostrar_archivos_backup(backup_path)

        lista.bind("<Double-Button-1>", abrir_backup)
        ttk.Button(win, text="Cerrar", command=win.destroy).pack(pady=5)

    def _mostrar_archivos_backup(self, backup_path):
        ventana = tk.Toplevel(self)
        ventana.title(f"Archivos en {os.path.basename(backup_path)}")

        lista = tk.Listbox(ventana, width=60)
        lista.pack(padx=10, pady=10, fill='both', expand=True)
        archivos = os.listdir(backup_path)
        for archivo in archivos:
            lista.insert(tk.END, archivo)

        def restaurar_archivo():
            seleccion = lista.curselection()
            if not seleccion:
                return messagebox.showwarning("Sin selección", "Seleccione un archivo o carpeta.")
            nombre = lista.get(seleccion[0])
            src = os.path.join(backup_path, nombre)
            dst = os.path.join(self.repo_actual.get(), "permanente", nombre)

            if os.path.exists(dst):
                respuesta = messagebox.askyesno("Sobrescribir", f"Ya existe '{nombre}'. ¿Desea reemplazarlo?")
                if not respuesta:
                    return
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)

            try:
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                messagebox.showinfo("Restaurado", f"'{nombre}' restaurado correctamente.")
                self._mostrar_archivos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo restaurar: {e}")

        def restaurar_todo():
            respuesta = messagebox.askyesno("Confirmar", "¿Deseas restaurar todos los archivos del backup?")
            if not respuesta:
                return
            perm_path = os.path.join(self.repo_actual.get(), "permanente")
            for nombre in os.listdir(backup_path):
                src = os.path.join(backup_path, nombre)
                dst = os.path.join(perm_path, nombre)
                try:
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo restaurar: {e}")
                    return
            messagebox.showinfo("Restaurado", "Todos los archivos fueron restaurados.")
            self._mostrar_archivos()

        ttk.Button(ventana, text="Restaurar archivo seleccionado", command=restaurar_archivo).pack(fill='x', padx=10, pady=5)
        ttk.Button(ventana, text="Restaurar TODO el backup", command=restaurar_todo).pack(fill='x', padx=10, pady=5)
        ttk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=5)

if __name__ == "__main__":
    app = GitGUI()
    app.mainloop()
