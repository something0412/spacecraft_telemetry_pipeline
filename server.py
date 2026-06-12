from fastapi import FastAPI
from pydantic import  BaseModel
from datetime import datetime
import sqlite3
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Run: uvicorn server:app --reload

@asynccontextmanager    # This tells FastAPI to run everything standing before "yeild" before start serving. Everthing standing after yield should be run when the server is called to shut down (mostly use for closing files/db)
async def lifespan(app: FastAPI):   # Purpose of this is to check if the ground system is ready to start serving
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_methods=['*'],
    allow_headers=['*'],
)

#todo -- Pydantic model goes here - This class is for auto-checking (ability from FastAPI) the incoming data packet
class TelemetryPacket(BaseModel):
    spacecraft_id: str
    timestamp: datetime
    temperature: float
    battery_voltage: float
    altitude: float
    attitude: float

#todo -- Database setup goes here
def init_db():
    # Open a connect
    conn = sqlite3.connect("telemetry.db")

    # Create table
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry(
            id INTEGER PRIMARY KEY, 
            spacecraft_id TEXT, 
            timestamp TEXT, 
            temperature REAL, 
            battery_voltage REAL,
            altitude REAL, 
            attitude REAL
        )"""
    )
    conn.commit()

    try:
        cursor.execute("PRAGMA table_info(telemetry)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'is_anomaly' not in columns:
            cursor.execute("ALTER TABLE telemetry ADD COLUMN is_anomaly INTEGER DEFAULT 0")
            conn.commit()
    except sqlite3.OperationalError as err:
        print(f"Error at init_db(): {err}")

    # Close connection
    conn.close()

#todo -- Check anomaly (if the values are in bounds ~ safe)
def check_anomaly(packet: TelemetryPacket) -> bool:
    bounds = {
        'temperature': (-40.0,  85.0),
        'battery_voltage': (22.0,  29.5),
        'altitude': (400.0, 420.0),
        'attitude': (-180.0, 180.0),
    }

    for key, value in packet:
        if key not in bounds:
            continue
        if value < bounds[key][0] or value > bounds[key][1]:
            return True
    return False

#todo -- Endpoints go here
'''
1. Receive a JSON body and parse it into your TelemetryPacket Pydantic model
2. Open a connection to the SQLite database
3. Insert the packet's fields into the telemetry table
4. Return HTTP 201 with a confirmation message

'''

#? receiving packet from sc_simulator
@app.post('/telemetry', status_code=201)
def post_request(packet: TelemetryPacket):
    anomaly = check_anomaly(packet)
    packet_data = (packet.spacecraft_id, packet.timestamp.isoformat(), packet.temperature, packet.battery_voltage, packet.altitude, packet.attitude, anomaly)
    conn = sqlite3.connect("telemetry.db")
    # cursor = conn.cursor()
    conn.execute("""
        INSERT INTO telemetry(spacecraft_id, timestamp, temperature, battery_voltage, altitude, attitude, is_anomaly) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
    """, packet_data)
    conn.commit()
    conn.close()
    return {"status": "ok", "is_anomaly": anomaly}

#? receiving get request and return the response obj
# FastAPI automatically maps everthing after ? into the function arguments
@app.get('/telemetry')
def get_request(
    spacecraft_id: str | None = None, 
    start: datetime | None = None, 
    end: datetime | None = None,
    order: str = 'DESC',
    limit: int = 15,
):
    conditions = []
    params = []

    if spacecraft_id:
        conditions.append("LOWER(spacecraft_id) = LOWER(?)")
        params.append(spacecraft_id)
    if start:
        conditions.append("timestamp >= ?")
        params.append(start.isoformat())
    if end:
        conditions.append("timestamp <= ?")
        params.append(end.isoformat())

    query = "SELECT * FROM telemetry"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    if order:
        allowed_orders = ['ASC','DESC']
        if order.upper() in allowed_orders:
            query += f" ORDER BY timestamp {order.upper()}, id {order.upper()}"
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    conn = sqlite3.connect("telemetry.db")
    # Allow return dict-like object instead of tuples (one tuple for each row)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(query, params)
    response = cursor.fetchall()
    conn.close()

    return {
        "status": "ok",
        "data": [dict(row) for row in response],
    }