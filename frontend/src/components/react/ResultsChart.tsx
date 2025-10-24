import { useEffect, useRef } from 'react';
import { Chart, registerables } from 'chart.js';
import type { CalculationResult } from '../../types/dhondt';

// Register Chart.js components
Chart.register(...registerables);

interface Props {
  result: CalculationResult;
}

export default function ResultsChart({ result }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Destroy existing chart if it exists
    if (chartRef.current) {
      chartRef.current.destroy();
    }

    // Create new chart
    const ctx = canvasRef.current.getContext('2d');
    if (ctx) {
      chartRef.current = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: result.results.map(r => r.name),
          datasets: [{
            label: 'Escaños Asignados',
            data: result.results.map(r => r.seats),
            backgroundColor: [
              'rgba(102, 126, 234, 0.8)',
              'rgba(118, 75, 162, 0.8)',
              'rgba(237, 100, 166, 0.8)',
              'rgba(255, 154, 158, 0.8)',
              'rgba(250, 208, 196, 0.8)',
              'rgba(185, 251, 192, 0.8)',
              'rgba(130, 204, 221, 0.8)',
              'rgba(138, 155, 255, 0.8)',
              'rgba(255, 199, 95, 0.8)',
              'rgba(255, 107, 129, 0.8)'
            ],
            borderColor: [
              'rgba(102, 126, 234, 1)',
              'rgba(118, 75, 162, 1)',
              'rgba(237, 100, 166, 1)',
              'rgba(255, 154, 158, 1)',
              'rgba(250, 208, 196, 1)',
              'rgba(185, 251, 192, 1)',
              'rgba(130, 204, 221, 1)',
              'rgba(138, 155, 255, 1)',
              'rgba(255, 199, 95, 1)',
              'rgba(255, 107, 129, 1)'
            ],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            title: {
              display: true,
              text: 'Distribución de Escaños',
              font: {
                size: 18
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          }
        }
      });
    }

    // Cleanup on unmount
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [result]);

  return (
    <div className="chart-container">
      <canvas ref={canvasRef} id="resultsChart"></canvas>
    </div>
  );
}
