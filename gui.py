import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import time
from usuarios import cargar_usuarios, crear_usuario_administrador, asignar_permiso
from repositorio import crear_repositorio
from version_control import commit, update

class GitGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Control de Versiones - GitHub Desktop Style")
        self.geometry("1080x640")
        self.usuario_actual = tk.StringVar()
        self.repo_actual = tk.StringVar()
        self.usuarios = cargar_usuarios()

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

        asignar_permiso(desde, hacia, tipo)
        messagebox.showinfo("Permiso asignado", f"{desde} dio permiso '{tipo}' a {hacia}.")

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

        # --- NUEVO BLOQUE PARA CREAR USUARIOS ---
        ttk.Separator(self.sidebar).pack(pady=10, fill='x')
        ttk.Label(self.sidebar, text="➕ Crear nuevo usuario").pack()
        self.entry_nuevo_user = ttk.Entry(self.sidebar)
        self.entry_nuevo_user.pack(padx=10, fill='x')
        ttk.Button(self.sidebar, text="Crear usuario", command=self._crear_usuario_app).pack(padx=10, pady=5, fill='x')

    def _build_main_content(self):
        frame_btns = ttk.Frame(self.content)
        frame_btns.pack(fill='x', pady=10)

        ttk.Button(frame_btns, text="🔃 Update", command=self._update).pack(side='left', padx=5)
        ttk.Button(frame_btns, text="💾 Commit", command=self._commit).pack(side='left', padx=5)
        ttk.Button(frame_btns, text="📦 Ver Backups", command=self._ver_backups).pack(side='left', padx=5)

        frame_archivos = ttk.Frame(self.content)
        frame_archivos.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Label(frame_archivos, text="📂 Temporal").grid(row=0, column=0)
        ttk.Label(frame_archivos, text="📂 Permanente").grid(row=0, column=1)

        self.tree_temp = ttk.Treeview(frame_archivos, columns=("nombre"), show="headings")
        self.tree_perm = ttk.Treeview(frame_archivos, columns=("nombre"), show="headings")
        self.tree_temp.heading("nombre", text="Archivo")
        self.tree_perm.heading("nombre", text="Archivo")

        self.tree_temp.grid(row=1, column=0, sticky="nsew", padx=5)
        self.tree_perm.grid(row=1, column=1, sticky="nsew", padx=5)

        frame_archivos.grid_rowconfigure(1, weight=1)
        frame_archivos.grid_columnconfigure(0, weight=1)
        frame_archivos.grid_columnconfigure(1, weight=1)

    def _on_user_selected(self, event=None):
        usuario = self.combo_usuario.get()
        self.usuario_actual.set(usuario)
        self._recargar_repos(usuario)

    def _recargar_repos(self, usuario):
        self.list_repos.delete(0, tk.END)
        self.usuarios = cargar_usuarios()

        # Repositorio propio
        repo_path = self.usuarios.get(usuario, {}).get("repositorio")
        if repo_path:
            self.list_repos.insert(tk.END, repo_path)

        # Repos donde OTROS le dieron permiso a este usuario
        for otro_user, data in self.usuarios.items():
            if otro_user == usuario:
                continue
            permisos = data.get("permisos", {})
            if usuario in permisos:
                repo_otro = data.get("repositorio")
                if repo_otro:
                    self.list_repos.insert(tk.END, repo_otro)

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
        usuarios = cargar_usuarios()
        if nuevo in usuarios:
            return messagebox.showerror("Error", "Ese usuario ya existe.")
        
        from usuarios import crear_usuario
        crear_usuario(nuevo)
        self.usuarios = cargar_usuarios()
        self.combo_usuario['values'] = list(self.usuarios.keys())
        self.perm_user['values'] = list(self.usuarios.keys())
        messagebox.showinfo("Éxito", f"Usuario '{nuevo}' creado.")

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

        for tree, path in [(self.tree_temp, temp), (self.tree_perm, perm)]:
            if os.path.exists(path):
                for nombre in os.listdir(path):
                    tree.insert('', tk.END, values=(nombre,))

    def _commit(self):
        user = self.usuario_actual.get()
        if not user:
            return
        repo = self.repo_actual.get()
        if not repo:
            return

        # Guardar backup
        perm_path = os.path.join(repo, "permanente")
        backup_root = os.path.join(repo, "versions")
        os.makedirs(backup_root, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_root, f"backup_{timestamp}")
        os.makedirs(backup_path)

        for archivo in os.listdir(perm_path):
            src = os.path.join(perm_path, archivo)
            dst = os.path.join(backup_path, archivo)
            if os.path.isfile(src):
                with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
                    fdst.write(fsrc.read())

        # Hacer commit real
        commit(user)
        self._mostrar_archivos()
        messagebox.showinfo("Commit", "Commit completado y versión guardada.")

    def _update(self):
        user = self.usuario_actual.get()
        if not user:
            return
        update(user, user)
        self._mostrar_archivos()

    def _ver_backups(self):
        repo = self.repo_actual.get()
        backup_dir = os.path.join(repo, "versions")
        if not os.path.exists(backup_dir):
            return messagebox.showinfo("Backups", "No hay versiones disponibles.")
        
        backups = os.listdir(backup_dir)
        if not backups:
            return messagebox.showinfo("Backups", "No hay versiones guardadas.")

        win = tk.Toplevel(self)
        win.title("Backups disponibles")
        lista = tk.Listbox(win, width=60)
        lista.pack(padx=10, pady=10)
        for b in backups:
            lista.insert(tk.END, b)
        
        ttk.Button(win, text="Cerrar", command=win.destroy).pack(pady=5)
        



if __name__ == "__main__":
    app = GitGUI()
    app.mainloop()
