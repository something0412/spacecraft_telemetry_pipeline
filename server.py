from fastapi import FastAPI
from pydantic import  BaseModel
from datetime import datetime
import sqlite3
from contextlib import asynccontextmanager

# Run: uvicorn server:app --reload

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

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

    # Close connection
    conn.close()

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
    packet_data = (packet.spacecraft_id, packet.timestamp.isoformat(), packet.temperature, packet.battery_voltage, packet.altitude, packet.attitude)
    conn = sqlite3.connect("telemetry.db")
    # cursor = conn.cursor()
    conn.execute("""
        INSERT INTO telemetry(spacecraft_id, timestamp, temperature, battery_voltage, altitude, attitude) 
            VALUES (?, ?, ?, ?, ?, ?)
    """, packet_data)
    conn.commit()
    conn.close()
    return {"status": "ok"}

#? receiving get request and return the response obj
# FastAPI automatically maps everthing after ? into the function arguments
@app.get('/telemetry')
def get_request(
    spacecraft_id: str | None = None, 
    start: datetime | None = None, 
    end: datetime | None = None,
    limit: int = 20,
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
    
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    conn = sqlite3.connect("telemetry.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(query, params)
    response = cursor.fetchall()
    conn.close()

    return {
        "status": "ok",
        "data": [dict(row) for row in response],
    }