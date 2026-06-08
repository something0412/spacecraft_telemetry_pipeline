//todo -- This is where the frontend fetch data

export interface TelemetryPacket {
  id: number;
  spacecraft_id: string;
  timestamp: string;
  temperature: number;
  battery_voltage: number;
  altitude: number;
  attitude: number;
}

export async function fetchTelemetry(): Promise<TelemetryPacket[]> {
    let packets: TelemetryPacket[] = []
    try{
        const response = await fetch("http://localhost:8000/telemetry")
        const data = await response.json()
        packets = data.data
    } catch (err){
        console.log(err)
    }
    return packets
}