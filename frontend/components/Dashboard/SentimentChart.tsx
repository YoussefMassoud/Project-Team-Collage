"use client";
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, ChartOptions, ChartData } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

interface SentimentData {
  Positive?: number;
  Negative?: number;
  Neutral?: number;
}

interface SentimentChartProps {
  data: SentimentData;
}

export default function SentimentChart({ data }: SentimentChartProps) {

  if (!data) return null;

  const chartData: ChartData<'doughnut'> = {
    labels: ['😊 Positive', '😢 Negative', '😐 Neutral'],
    datasets: [
      {
        data: [data.Positive || 0, data.Negative || 0, data.Neutral || 0],
        backgroundColor: [
          'rgba(16, 185, 129, 0.9)',
          'rgba(244, 63, 94, 0.9)',
          'rgba(139, 92, 246, 0.9)',
        ],
        borderColor: [
          'rgba(16, 185, 129, 1)',
          'rgba(244, 63, 94, 1)',
          'rgba(139, 92, 246, 1)',
        ],
        borderWidth: 3,
        hoverOffset: 15,
        hoverBorderWidth: 4,
        hoverBorderColor: [
          'rgba(16, 185, 129, 1)',
          'rgba(244, 63, 94, 1)',
          'rgba(139, 92, 246, 1)',
        ],
      },
    ],
  };

  const options: ChartOptions<'doughnut'> = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '65%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#fff',
          font: {
            size: 13,
            weight: 'bold' as const,
            family: "'Inter', sans-serif"
          },
          padding: 15,
          usePointStyle: true,
          pointStyle: 'circle',
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1,
        padding: 12,
        displayColors: true,
        callbacks: {
          label: function (context) {
            const label = context.label || '';
            const value = context.parsed || 0;
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
            return `${label}: ${value} (${percentage}%)`;
          }
        }
      }
    },
    animation: {
      animateRotate: true,
      animateScale: true,
      duration: 1000,
      easing: 'easeInOutQuart' as const
    }
  };

  return (
    <div style={{
      height: '280px',
      width: '100%',
      position: 'relative',
      filter: 'drop-shadow(0 0 20px rgba(124, 58, 237, 0.3))'
    }}>
      <Doughnut data={chartData} options={options} />
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        textAlign: 'center',
        pointerEvents: 'none',
        marginTop: '-15px'
      }}>
        <div style={{
          fontSize: '2rem',
          fontWeight: 'bold',
          background: 'linear-gradient(135deg, #10b981, #8b5cf6)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          {(data.Positive || 0) + (data.Negative || 0) + (data.Neutral || 0)}
        </div>
        <div style={{
          fontSize: '0.75rem',
          color: '#888',
          marginTop: '5px'
        }}>
          Total Comments
        </div>
      </div>
    </div>
  );
}