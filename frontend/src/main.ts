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
      `Alt: ${latest.altitude}m | ` +
      `Att: ${latest.attitude}°`
  }
  updateCharts(data)
}

poll()
setInterval(poll, 2000)