
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    edificio VARCHAR(100) NOT NULL,
    capacidad INTEGER NOT NULL,
    equipamiento JSONB
);

CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    aula_id INTEGER REFERENCES rooms(id),
    usuario VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL
);

INSERT INTO rooms (nombre, edificio, capacidad, equipamiento)
VALUES
('Aula 101', 'Edificio A', 30, '["proyector", "pizarra"]'),
('Aula 202', 'Edificio B', 40, '["ordenadores", "proyector"]'),
('Laboratorio 1', 'Edificio C', 25, '["ordenadores", "pizarra digital"]');

SELECT * FROM rooms;
