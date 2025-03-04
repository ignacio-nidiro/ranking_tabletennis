import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database
from PIL import Image, ImageTk
import pandas as pd
import os
from datetime import datetime

class TenisMesaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Ranking - Club de Tenis de Mesa")
        self.db = Database(dbname="tenis_mesa", user="postgres", password="postgres")

        # Configurar estilos
        self.configure_styles()

        # Cargar la imagen
        self.load_image()

        # Interfaz gráfica
        self.label = tk.Label(root, text="JOGA PONG - Gestor de Ranking", font=("Arial", 16, "bold"), fg="#333")
        self.label.pack(pady=10)

        # Mostrar la imagen en el menú
        self.image_label = tk.Label(root, image=self.image_tk)
        self.image_label.pack(pady=10)

        # Botones con estilos modernos
        self.add_player_button = ttk.Button(root, text="Agregar Jugador", command=self.show_add_player_window, style="Accent.TButton")
        self.add_player_button.pack(pady=5)

        self.record_match_button = ttk.Button(root, text="Registrar Partido", command=self.record_match, style="Accent.TButton")
        self.record_match_button.pack(pady=5)

        self.view_rankings_button = ttk.Button(root, text="Ver Rankings", command=self.show_rankings, style="Accent.TButton")
        self.view_rankings_button.pack(pady=5)

        self.view_matches_button = ttk.Button(root, text="Ver Historial de Partidos", command=self.show_matches, style="Accent.TButton")
        self.view_matches_button.pack(pady=5)

        self.export_button = ttk.Button(root, text="Exportar a Excel", command=self.export_to_excel, style="Accent.TButton")
        self.export_button.pack(pady=5)

    def configure_styles(self):
        # Configurar estilos modernos
        style = ttk.Style()
        style.theme_use("clam")  # Usar un tema moderno
        style.configure("TButton", font=("Arial", 10), padding=5)
        style.configure("Accent.TButton", background="#4CAF50", foreground="white", font=("Arial", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#45a049")])

    def load_image(self):
        # Cargar la imagen desde un archivo
        try:
            image = Image.open("jp_logo.jpg")  # Cambia "jp_logo.jpg" por la ruta de tu imagen
            image = image.resize((200, 200))  # Redimensionar la imagen si es necesario
            self.image_tk = ImageTk.PhotoImage(image)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")
            self.image_tk = None

    def show_add_player_window(self):
        # Crear una nueva ventana para agregar un jugador
        add_player_window = tk.Toplevel(self.root)
        add_player_window.title("Agregar Jugador")

        # Campos para ingresar los datos del jugador
        tk.Label(add_player_window, text="Nombre:").grid(row=0, column=0, padx=10, pady=10)
        self.nombre_entry = tk.Entry(add_player_window)
        self.nombre_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(add_player_window, text="Apellido:").grid(row=1, column=0, padx=10, pady=10)
        self.apellido_entry = tk.Entry(add_player_window)
        self.apellido_entry.grid(row=1, column=1, padx=10, pady=10)

        # Botón para agregar el jugador
        ttk.Button(add_player_window, text="Agregar", command=lambda: self.add_player(add_player_window), style="Accent.TButton").grid(row=3, column=0, columnspan=2, pady=10)

    def add_player(self, add_player_window):
        # Obtener los datos del formulario
        nombre = self.nombre_entry.get()
        apellido = self.apellido_entry.get()

        if not nombre or not apellido:
            messagebox.showerror("Error", "Nombre y Apellido son obligatorios")
            return

        try:
            # Insertar el jugador en la base de datos
            self.db.execute_query(
                "INSERT INTO jugadores (nombre, apellido, ranking) VALUES (%s, %s, %s)",
                (nombre, apellido, 1000)  # Ranking inicial de 1000
            )
            messagebox.showinfo("Éxito", "Jugador agregado correctamente")
            add_player_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el jugador: {e}")

    def record_match(self):
        # Crear una nueva ventana para registrar partidos
        match_window = tk.Toplevel(self.root)
        match_window.title("Registrar Partido")

        # Obtener la lista de jugadores
        jugadores = self.db.fetch_all("SELECT id, nombre, apellido FROM jugadores")
        jugadores_list = [f"{nombre} {apellido}" for id, nombre, apellido in jugadores]

        # Combobox para seleccionar el jugador 1
        tk.Label(match_window, text="Jugador 1:").grid(row=0, column=0, padx=10, pady=10)
        self.jugador1_combobox = ttk.Combobox(match_window, values=jugadores_list)
        self.jugador1_combobox.grid(row=0, column=1, padx=10, pady=10)

        # Combobox para seleccionar el jugador 2
        tk.Label(match_window, text="Jugador 2:").grid(row=1, column=0, padx=10, pady=10)
        self.jugador2_combobox = ttk.Combobox(match_window, values=jugadores_list)
        self.jugador2_combobox.grid(row=1, column=1, padx=10, pady=10)

        # Campo para ingresar el resultado
        tk.Label(match_window, text="Resultado (ej: 3-1):").grid(row=2, column=0, padx=10, pady=10)
        self.resultado_entry = tk.Entry(match_window)
        self.resultado_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(match_window, text="Fecha (ej. 2025-02-26):").grid(row=3, column=0, padx=10, pady=10)
        self.fecha_entry = tk.Entry(match_window)
        self.fecha_entry.grid(row=3, column=1, padx=10, pady=10)

        # Botón para registrar el partido
        ttk.Button(match_window, text="Registrar", command=lambda: self.registrar_partido(match_window), style="Accent.TButton").grid(row=4, column=0, columnspan=2, pady=10)

    def registrar_partido(self, match_window):
        # Obtener los datos del formulario
        jugador1 = self.jugador1_combobox.get()
        jugador2 = self.jugador2_combobox.get()
        resultado = self.resultado_entry.get()
        fecha = self.fecha_entry.get()

        if not jugador1 or not jugador2 or not resultado:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        # Validar el formato del resultado
        try:
            sets_jugador1, sets_jugador2 = map(int, resultado.split("-"))
        except ValueError:
            messagebox.showerror("Error", "El resultado debe estar en formato '3-1'")
            return

        # Extraer los nombres y apellidos de los jugadores
        jugador1_nombre, jugador1_apellido = jugador1.split(" ")
        jugador2_nombre, jugador2_apellido = jugador2.split(" ")

        try:
            # Obtener los IDs de los jugadores
            jugador1_id = self.db.fetch_all(
                "SELECT id FROM jugadores WHERE nombre = %s AND apellido = %s",
                (jugador1_nombre, jugador1_apellido)
            )[0][0]
            jugador2_id = self.db.fetch_all(
                "SELECT id FROM jugadores WHERE nombre = %s AND apellido = %s",
                (jugador2_nombre, jugador2_apellido)
            )[0][0]

            # Obtener los rankings actuales de los jugadores
            jugador1_ranking = self.db.fetch_all("SELECT ranking FROM jugadores WHERE id = %s", (jugador1_id,))[0][0]
            jugador2_ranking = self.db.fetch_all("SELECT ranking FROM jugadores WHERE id = %s", (jugador2_id,))[0][0]

            # Calcular nuevos rankings
            nuevo_ranking1, nuevo_ranking2 = self.calcular_elo(jugador1_ranking, jugador2_ranking, resultado)

            # Calcular puntos ganados o perdidos
            puntos_jugador1 = nuevo_ranking1 - jugador1_ranking
            puntos_jugador2 = nuevo_ranking2 - jugador2_ranking

            # Determinar el ganador
            ganador = jugador1_id if sets_jugador1 > sets_jugador2 else jugador2_id

            # Actualizar los rankings en la base de datos
            self.db.execute_query("UPDATE jugadores SET ranking = %s WHERE id = %s", (nuevo_ranking1, jugador1_id))
            self.db.execute_query("UPDATE jugadores SET ranking = %s WHERE id = %s", (nuevo_ranking2, jugador2_id))

            # Registrar el partido en la base de datos
            self.db.execute_query(
                "INSERT INTO partidos (jugador1_id, jugador2_id, resultado, fecha, ganador_id, puntos_jugador1, puntos_jugador2) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (jugador1_id, jugador2_id, resultado, fecha, ganador, puntos_jugador1, puntos_jugador2)
            )
            messagebox.showinfo("Éxito", "Partido registrado y rankings actualizados")
            match_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el partido: {e}")

    def calcular_elo(self, ranking1, ranking2, resultado):
        # Factor K (puedes ajustarlo según el nivel del jugador)
        K = 32

        # Calcular la probabilidad esperada
        probabilidad1 = 1 / (1 + 10 ** ((ranking2 - ranking1) / 400))
        probabilidad2 = 1 / (1 + 10 ** ((ranking1 - ranking2) / 400))

        # Determinar el resultado (1 si gana el jugador1, 0 si gana el jugador2)
        sets_jugador1, sets_jugador2 = map(int, resultado.split("-"))
        if sets_jugador1 > sets_jugador2:
            resultado1, resultado2 = 1, 0
        elif sets_jugador2 == sets_jugador1:
            messagebox.showerror("Error", "Un partido no puede terminar en empate!")
            return ranking1, ranking2
        else:
            resultado1, resultado2 = 0, 1

        # Calcular nuevos rankings
        points_added1 = K * (resultado1 - probabilidad1)
        points_added2 = K * (resultado2 - probabilidad2)

        print(f'Ranking 1 + {points_added1}')
        print(f'Ranking 2 + {points_added2}')

        nuevo_ranking1 = ranking1 + points_added1
        nuevo_ranking2 = ranking2 + points_added2

        return round(nuevo_ranking1), round(nuevo_ranking2)

    def show_rankings(self):
        # Crear una nueva ventana para mostrar los rankings
        rankings_window = tk.Toplevel(self.root)
        rankings_window.title("Rankings de Jugadores")

        # Crear un Treeview para mostrar la tabla
        columns = ("#", "Nombre", "Apellido", "Ranking")
        self.tree = ttk.Treeview(rankings_window, columns=columns, show="headings")
        self.tree.heading("#", text="#")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Apellido", text="Apellido")
        self.tree.heading("Ranking", text="Ranking")

        # Ajustar el ancho de las columnas
        self.tree.column("#", width=50, anchor="center")
        self.tree.column("Nombre", width=150, anchor="w")
        self.tree.column("Apellido", width=150, anchor="w")
        self.tree.column("Ranking", width=100, anchor="center")

        # Obtener los rankings de la base de datos
        rankings = self.db.fetch_all("SELECT nombre, apellido, ranking FROM jugadores ORDER BY ranking DESC")

        # Insertar los datos en la tabla
        for i, (nombre, apellido, ranking) in enumerate(rankings, start=1):
            self.tree.insert("", "end", values=(i, nombre, apellido, ranking))

        # Añadir la tabla a la ventana
        self.tree.pack(fill="both", expand=True)

    def show_matches(self):
        # Crear una nueva ventana para mostrar el historial de partidos
        matches_window = tk.Toplevel(self.root)
        matches_window.title("Historial de Partidos")

        # Crear un Treeview para mostrar la tabla
        columns = ("#", "Jugador 1", "Jugador 2", "Resultado", "ID_Ganador", "Ganador", "Puntos Jugador 1", "Puntos Jugador 2", "Fecha")
        self.matches_tree = ttk.Treeview(matches_window, columns=columns, show="headings")
        self.matches_tree.heading("#", text="#")
        self.matches_tree.heading("Jugador 1", text="Jugador 1")
        self.matches_tree.heading("Jugador 2", text="Jugador 2")
        self.matches_tree.heading("Resultado", text="Resultado")
        self.matches_tree.heading("ID_Ganador", text="ID_Ganador")
        self.matches_tree.heading("Ganador", text="Ganador")
        self.matches_tree.heading("Puntos Jugador 1", text="Puntos Jugador 1")
        self.matches_tree.heading("Puntos Jugador 2", text="Puntos Jugador 2")
        self.matches_tree.heading("Fecha", text="Fecha")

        # Ajustar el ancho de las columnas
        self.matches_tree.column("#", width=50, anchor="center")
        self.matches_tree.column("Jugador 1", width=150, anchor="w")
        self.matches_tree.column("Jugador 2", width=150, anchor="w")
        self.matches_tree.column("Resultado", width=100, anchor="center")
        self.matches_tree.column("ID_Ganador", width=50, anchor="w")
        self.matches_tree.column("Ganador", width=150, anchor="w")
        self.matches_tree.column("Puntos Jugador 1", width=100, anchor="center")
        self.matches_tree.column("Puntos Jugador 2", width=100, anchor="center")
        self.matches_tree.column("Fecha", width=150, anchor="center")

        # Obtener el historial de partidos de la base de datos
        partidos = self.db.fetch_all("""
            SELECT p.id, j1.nombre || ' ' || j1.apellido AS jugador1, 
                   j2.nombre || ' ' || j2.apellido AS jugador2, p.resultado, p.ganador_id, j3.nombre || ' ' || j3.apellido,
                   p.puntos_jugador1, p.puntos_jugador2, p.fecha
            FROM partidos p
            JOIN jugadores j1 ON p.jugador1_id = j1.id
            JOIN jugadores j2 ON p.jugador2_id = j2.id
            JOIN jugadores j3 on p.ganador_id = j3.id
            ORDER BY p.fecha DESC
        """)

        # Insertar los datos en la tabla
        for i, (id, jugador1, jugador2, resultado, id_ganador, ganador, puntos_jugador1, puntos_jugador2, fecha) in enumerate(partidos, start=1):
            self.matches_tree.insert("", "end", values=(i, jugador1, jugador2, resultado, id_ganador, ganador, puntos_jugador1, puntos_jugador2, fecha))

        # Añadir la tabla a la ventana
        self.matches_tree.pack(fill="both", expand=True)

    def export_to_excel(self):
        # Crear la carpeta si no existe
        export_folder = os.path.join(os.path.expanduser("~"), "Documents", "Ranking_JogaPong")
        os.makedirs(export_folder, exist_ok=True)

        # Nombre del archivo con la fecha y hora actual
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(export_folder, f"ranking_{now}.xlsx")

        # Obtener los datos de la base de datos
        rankings = self.db.fetch_all("SELECT nombre, apellido, ranking FROM jugadores ORDER BY ranking DESC")
        partidos = self.db.fetch_all("""
            SELECT p.id, j1.nombre || ' ' || j1.apellido AS jugador1, 
                   j2.nombre || ' ' || j2.apellido AS jugador2, p.resultado, p.ganador_id, j3.nombre || ' ' || j3.apellido,
                   p.puntos_jugador1, p.puntos_jugador2, p.fecha
            FROM partidos p
            JOIN jugadores j1 ON p.jugador1_id = j1.id
            JOIN jugadores j2 ON p.jugador2_id = j2.id
            JOIN jugadores j3 on p.ganador_id = j3.id
            ORDER BY p.fecha DESC
        """)

        # Crear un DataFrame de pandas
        df_rankings = pd.DataFrame(rankings, columns=["Nombre", "Apellido", "Ranking"])
        df_partidos = pd.DataFrame(partidos, columns=["ID", "Jugador 1", "Jugador 2", "Resultado", "ID_Ganador", "Ganador", "Puntos Jugador 1", "Puntos Jugador 2", "Fecha"])

        # Exportar a Excel
        with pd.ExcelWriter(file_path) as writer:
            df_rankings.to_excel(writer, sheet_name="Rankings", index=False)
            df_partidos.to_excel(writer, sheet_name="Partidos", index=False)

        messagebox.showinfo("Éxito", f"Datos exportados a {file_path}")

    def __del__(self):
        self.db.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = TenisMesaApp(root)
    root.mainloop()