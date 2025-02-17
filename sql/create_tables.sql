-- Crear tabla jugadores
CREATE TABLE IF NOT EXISTS jugadores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    ranking INT DEFAULT 0
);

-- Crear tabla partidos
CREATE TABLE IF NOT EXISTS partidos (
    id SERIAL PRIMARY KEY,
    jugador1_id INT REFERENCES jugadores(id),
    jugador2_id INT REFERENCES jugadores(id),
    resultado VARCHAR(10),
    fecha DATE
);