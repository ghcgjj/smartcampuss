
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import psycopg2
import psycopg2.extras
import os

app = FastAPI(title="SmartCampus API")

# Permitir la comunicación con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de la base de datos
DB_HOST = os.getenv("DB_HOST", "database")
DB_NAME = os.getenv("DB_NAME", "smartcampus")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )


# Modelo de aula
class Room(BaseModel):
    nombre: str
    edificio: str
    capacidad: int
    equipamiento: List[str]


# Modelo de reserva
class Booking(BaseModel):
    aula_id: int
    usuario: str
    fecha: str
    hora_inicio: str
    hora_fin: str


# Comprobar el estado del backend y la base de datos
@app.get("/health")
def health():
    try:
        conn = get_connection()
        conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection error: {str(e)}"
        )


# Consultar todas las aulas
@app.get("/rooms")
def get_rooms():
    try:
        conn = get_connection()
        cur = conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )

        cur.execute("SELECT * FROM rooms ORDER BY id")
        rooms = cur.fetchall()

        cur.close()
        conn.close()

        return [dict(room) for room in rooms]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Consultar un aula por su ID
@app.get("/rooms/{room_id}")
def get_room(room_id: int):
    conn = get_connection()
    cur = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    cur.execute("SELECT * FROM rooms WHERE id = %s", (room_id,))
    room = cur.fetchone()

    cur.close()
    conn.close()

    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    return dict(room)


# Crear un aula
@app.post("/rooms")
def create_room(room: Room):
    conn = get_connection()
    cur = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    cur.execute(
        """
        INSERT INTO rooms (nombre, edificio, capacidad, equipamiento)
        VALUES (%s, %s, %s, %s)
        RETURNING *
        """,
        (
            room.nombre,
            room.edificio,
            room.capacidad,
            psycopg2.extras.Json(room.equipamiento)
        )
    )

    new_room = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    return dict(new_room)


# Consultar todas las reservas
@app.get("/bookings")
def get_bookings():
    conn = get_connection()
    cur = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    cur.execute(
        """
        SELECT bookings.*, rooms.nombre AS aula_nombre
        FROM bookings
        JOIN rooms ON bookings.aula_id = rooms.id
        ORDER BY bookings.id
        """
    )

    bookings = cur.fetchall()

    cur.close()
    conn.close()

    return [dict(booking) for booking in bookings]


# Crear una reserva
@app.post("/bookings")
def create_booking(booking: Booking):
    conn = get_connection()
    cur = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    cur.execute(
        """
        INSERT INTO bookings
        (aula_id, usuario, fecha, hora_inicio, hora_fin)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            booking.aula_id,
            booking.usuario,
            booking.fecha,
            booking.hora_inicio,
            booking.hora_fin
        )
    )

    new_booking = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    return dict(new_booking)
