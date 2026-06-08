import { Chart } from 'chart.js/auto'
import type { TelemetryPacket } from './api'

// temperature
const tempChart = new Chart(
    document.getElementById('temp-chart') as HTMLCanvasElement,
    {
        type: 'line',
        data: {
            labels: [],     // timestamps go  here
            datasets: [{
                label: 'Temperature (°C)',
                data: [],   // values go  here
                borderColor: 'orange',
            }]
        }
    }
)

// battery voltage
const voltChart = new Chart(
    document.getElementById('voltage-chart') as HTMLCanvasElement,
    {
        type: 'line',
        data: {
            labels: [],     // timestamps go  here
            datasets: [{
                label: 'Battery Voltage (V)',
                data: [],   // values go  here
                borderColor: 'blue',
            }]
        }
    }
)

// altitude
const altChart = new Chart(
    document.getElementById('altitude-chart') as HTMLCanvasElement,
    {
        type: 'line',
        data: {
            labels: [],     // timestamps go  here
            datasets: [{
                label: 'Altitude (m)',
                data: [],   // values go  here
                borderColor: 'pink',
            }]
        }
    }
)

// attitude
const attChart = new Chart(
    document.getElementById('attitude-chart') as HTMLCanvasElement,
    {
        type: 'line',
        data: {
            labels: [],     // timestamps go  here
            datasets: [{
                label: 'Attitude (°)',
                data: [],   // values go  here
                borderColor: 'purple',
            }]
        }
    }
)

export function updateCharts(packets: TelemetryPacket[]): void{
    let charts: Chart[] = [tempChart, voltChart, altChart, attChart]
    let newLabels: string[] = []
    let newData: number[][] = Array.from({length: charts.length}, ()=>[])
    for (const packet of packets){
        newLabels.push(packet.timestamp);
        newData[0].push(packet.temperature);
        newData[1].push(packet.battery_voltage);
        newData[2].push(packet.altitude);
        newData[3].push(packet.attitude);
    }
    for (let i=0; i<charts.length; i++){
        charts[i].data.labels = [...newLabels].reverse();
        charts[i].data.datasets[0].data = [...newData[i]].reverse();
        charts[i].update()
    }
}