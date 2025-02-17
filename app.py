import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class TenisMesaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Ranking - Club de Tenis de Mesa")
        self.db = Database(dbname="tenis_mesa", user="postgres", password="postgres")

        # Interfaz gráfica
        self.label = tk.Label(root, text="Bienvenido al Club de Tenis de Mesa")
        self.label.pack()

        self.add_player_button = tk.Button(root, text="Agregar Jugador", command=self.show_add_player_window)
        self.add_player_button.pack()

        self.record_match_button = tk.Button(root, text="Registrar Partido", command=self.record_match)
        self.record_match_button.pack()

        self.view_rankings_button = tk.Button(root, text="Ver Rankings", command=self.show_rankings)
        self.view_rankings_button.pack()

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
        tk.Button(add_player_window, text="Agregar", command=lambda: self.add_player(add_player_window)).grid(row=3, column=0, columnspan=2, pady=10)

    def add_player(self, add_player_window):
        # Obtener los datos del formulario
        nombre = self.nombre_entry.get()
        apellido = self.apellido_entry.get()

        if not nombre or not apellido:
            messagebox.showerror("Error", "Nombre y Apellido son obligatorios")
            return

        # Insertar el jugador en la base de datos
        self.db.execute_query(
            "INSERT INTO jugadores (nombre, apellido, ranking) VALUES (%s, %s, %s)",
            (nombre, apellido, 1000)  # Ranking inicial de 1000
        )
        messagebox.showinfo("Éxito", "Jugador agregado correctamente")
        add_player_window.destroy()

    def record_match(self):
        # Crear una nueva ventana para registrar partidos
        match_window = tk.Toplevel(self.root)
        match_window.title("Registrar Partido")

        # Obtener la lista de jugadores
        jugadores = self.db.fetch_all("SELECT nombre, apellido FROM jugadores")
        jugadores_list = [f"{nombre} {apellido}" for nombre, apellido in jugadores]

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

        # Botón para registrar el partido
        tk.Button(match_window, text="Registrar", command=lambda: self.registrar_partido(match_window)).grid(row=3, column=0, columnspan=2, pady=10)

    def registrar_partido(self, match_window):
        # Obtener los datos del formulario
        jugador1 = self.jugador1_combobox.get()
        jugador2 = self.jugador2_combobox.get()
        resultado = self.resultado_entry.get()

        if not jugador1 or not jugador2 or not resultado:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        # Extraer los IDs de los jugadores
        jugador1_name, jugador1_lastname = jugador1.split(" ")
        jugador2_name, jugador2_lastname = jugador2.split(" ")

        jugador1_id = self.db.fetch_all(
            f"SELECT id FROM jugadores WHERE nombre = '{jugador1_name}' and apellido = '{jugador1_lastname}'")[0]
        jugador2_id = self.db.fetch_all(
            f"SELECT id FROM jugadores WHERE nombre = '{jugador2_name}' and apellido = '{jugador2_lastname}'")[0]

        # Obtener los rankings actuales de los jugadores
        jugador1_ranking = self.db.fetch_all("SELECT ranking FROM jugadores WHERE id = %s", (jugador1_id,))[0][0]
        jugador2_ranking = self.db.fetch_all("SELECT ranking FROM jugadores WHERE id = %s", (jugador2_id,))[0][0]

        # Calcular nuevos rankings
        nuevo_ranking1, nuevo_ranking2 = self.calcular_elo(jugador1_ranking, jugador2_ranking, resultado)

        # Actualizar los rankings en la base de datos
        self.db.execute_query("UPDATE jugadores SET ranking = %s WHERE id = %s", (nuevo_ranking1, jugador1_id))
        self.db.execute_query("UPDATE jugadores SET ranking = %s WHERE id = %s", (nuevo_ranking2, jugador2_id))

        # Registrar el partido en la base de datos
        self.db.execute_query(
            "INSERT INTO partidos (jugador1_id, jugador2_id, resultado) VALUES (%s, %s, %s)",
            (jugador1_id, jugador2_id, resultado)
        )
        messagebox.showinfo("Éxito", "Partido registrado y rankings actualizados")
        match_window.destroy()

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

    def __del__(self):
        self.db.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = TenisMesaApp(root)
    root.mainloop()