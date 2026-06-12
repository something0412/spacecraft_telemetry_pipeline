import { fetchTelemetry } from "./api";
import { updateCharts } from "./charts";

async function poll(){
  const data = await fetchTelemetry()
  const latest = data[0]
  if (latest) {
    document.getElementById('latest')!.textContent =
      `${latest.spacecraft_id} | ${latest.timestamp} | ` +
      `Temp: ${latest.temperature}°C | ` +
      `Voltage: ${latest.battery_voltage}V | ` +
      `Alt: ${latest.altitude}km | ` +
      `Att: ${latest.attitude}°`

    if (latest.is_anomaly){
      document.getElementById('alert')!.textContent = 
        `${latest.spacecraft_id} | ${latest.timestamp} | ` +
        `Temp: ${latest.temperature}°C | ` +
        `Voltage: ${latest.battery_voltage}V | ` +
        `Alt: ${latest.altitude}km | ` +
        `Att: ${latest.attitude}°`

      document.getElementById('alert')!.style.display = ''
    } else{
      document.getElementById('alert')!.style.display = 'none'
    }
  }
  updateCharts(data)
}

poll()
setInterval(poll, 2000)