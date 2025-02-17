import tkinter as tk
from tkinter import messagebox
from database import Database

class TenisMesaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Ranking - Club de Tenis de Mesa")
        self.db = Database(dbname="tenis_mesa", user="postgres", password="postgres")

        # Interfaz gráfica
        self.label = tk.Label(root, text="Bienvenido al Club de Tenis de Mesa")
        self.label.pack()

        self.add_player_button = tk.Button(root, text="Agregar Jugador", command=self.add_player)
        self.add_player_button.pack()

        self.record_match_button = tk.Button(root, text="Registrar Partido", command=self.record_match)
        self.record_match_button.pack()

        self.view_rankings_button = tk.Button(root, text="Ver Rankings", command=self.view_rankings)
        self.view_rankings_button.pack()

    def add_player(self):
        # Lógica para agregar un jugador
        nombre = "Jugador Ejemplo"  # Puedes usar un cuadro de diálogo para ingresar el nombre
        apellido = "Apellido Ejemplo"
        self.db.execute_query(
            "INSERT INTO jugadores (nombre, apellido, ranking) VALUES (%s, %s, %s)",
            (nombre, apellido, 1000)  # Ranking inicial de 1000
        )
        messagebox.showinfo("Éxito", "Jugador agregado correctamente")

    def record_match(self):
        # Lógica para registrar un partido
        jugador1_id = simpledialog.askinteger("Registrar Partido", "ID del Jugador 1:")
        jugador2_id = simpledialog.askinteger("Registrar Partido", "ID del Jugador 2:")
        resultado = simpledialog.askstring("Registrar Partido", "Resultado (ej: 3-1):")

        # Obtener los rankings actuales de los jugadores
        jugador1 = self.db.fetch_all("SELECT ranking FROM jugadores WHERE id = %s", (jugador1_id,))[0]
        jugador2 = self.db.fetch_all("SELECT ranking FROM jugadores WHERE id = %s", (jugador2_id,))[0]

        # Calcular nuevos rankings
        nuevo_ranking1, nuevo_ranking2 = self.calcular_elo(jugador1[0], jugador2[0], resultado)

        # Actualizar los rankings en la base de datos
        self.db.execute_query("UPDATE jugadores SET ranking = %s WHERE id = %s", (nuevo_ranking1, jugador1_id))
        self.db.execute_query("UPDATE jugadores SET ranking = %s WHERE id = %s", (nuevo_ranking2, jugador2_id))

        # Registrar el partido en la base de datos
        self.db.execute_query(
            "INSERT INTO partidos (jugador1_id, jugador2_id, resultado) VALUES (%s, %s, %s)",
            (jugador1_id, jugador2_id, resultado)
        )
        messagebox.showinfo("Éxito", "Partido registrado y rankings actualizados")

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
        nuevo_ranking1 = ranking1 + K * (resultado1 - probabilidad1)
        nuevo_ranking2 = ranking2 + K * (resultado2 - probabilidad2)

        return round(nuevo_ranking1), round(nuevo_ranking2)

    def view_rankings(self):
        # Lógica para ver los rankings
        rankings = self.db.fetch_all("SELECT nombre, apellido, ranking FROM jugadores ORDER BY ranking DESC")
        for jugador in rankings:
            print(jugador)  # Puedes mostrar esto en la interfaz gráfica

    def __del__(self):
        self.db.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = TenisMesaApp(root)
    root.mainloop()