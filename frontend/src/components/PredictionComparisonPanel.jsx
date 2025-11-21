import React, { useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler
);

const PredictionComparisonPanel = ({ apiBaseUrl, isDarkMode }) => {
  const [seriesId, setSeriesId] = useState('');
  const [csvFile, setCsvFile] = useState(null);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [comparisonResult, setComparisonResult] = useState(null);

  const theme = {
    bg: isDarkMode ? '#0f172a' : '#ffffff',
    cardBg: isDarkMode ? '#1e293b' : '#f8fafc',
    text: isDarkMode ? '#e2e8f0' : '#1e293b',
    textSecondary: isDarkMode ? '#94a3b8' : '#64748b',
    border: isDarkMode ? '#334155' : '#e2e8f0',
    primary: '#3b82f6',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.name.endsWith('.csv')) {
      setCsvFile(file);
      setError('');
    } else {
      setError('Por favor, selecione um arquivo CSV');
      setCsvFile(null);
    }
  };

  const handleCompare = async () => {
    if (!seriesId.trim()) {
      setError('Por favor, informe o ID do modelo (series_id)');
      return;
    }

    if (!csvFile) {
      setError('Por favor, selecione um arquivo CSV com valores reais');
      return;
    }

    setLoading(true);
    setError('');
    setComparisonResult(null);

    try {
      const formData = new FormData();
      formData.append('file', csvFile);
      formData.append('series_id', seriesId);
      if (startDate) formData.append('start_date', startDate);
      if (endDate) formData.append('end_date', endDate);

      const response = await fetch(`${apiBaseUrl}/forecast/compare-predictions`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setComparisonResult(data);
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Erro desconhecido' }));
        setError(errorData.detail || `Erro HTTP ${response.status}`);
      }
    } catch (err) {
      setError(`Erro ao comparar: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getQualityColor = (quality) => {
    if (quality === 'excellent') return theme.success;
    if (quality === 'good') return '#3b82f6';
    if (quality === 'acceptable') return theme.warning;
    return theme.danger;
  };

  const getQualityLabel = (quality) => {
    const labels = {
      excellent: 'Excelente',
      good: 'Boa',
      acceptable: 'Aceitável',
      poor: 'Ruim',
    };
    return labels[quality] || quality;
  };

  const chartData = comparisonResult ? {
    labels: comparisonResult.comparison_data.map(d => new Date(d.ds).toLocaleDateString('pt-BR')),
    datasets: [
      {
        label: 'Valores Reais',
        data: comparisonResult.comparison_data.map(d => d.actual),
        borderColor: theme.success,
        backgroundColor: `${theme.success}20`,
        fill: false,
        tension: 0.1,
        pointRadius: 3,
      },
      {
        label: 'Previsões',
        data: comparisonResult.comparison_data.map(d => d.predicted),
        borderColor: theme.primary,
        backgroundColor: `${theme.primary}20`,
        fill: false,
        tension: 0.1,
        pointRadius: 3,
      },
      ...(comparisonResult.comparison_data[0]?.predicted_lower ? [{
        label: 'Limite Inferior',
        data: comparisonResult.comparison_data.map(d => d.predicted_lower),
        borderColor: `${theme.primary}40`,
        backgroundColor: `${theme.primary}10`,
        fill: '-1',
        tension: 0.1,
        pointRadius: 0,
        borderDash: [5, 5],
      }] : []),
      ...(comparisonResult.comparison_data[0]?.predicted_upper ? [{
        label: 'Limite Superior',
        data: comparisonResult.comparison_data.map(d => d.predicted_upper),
        borderColor: `${theme.primary}40`,
        backgroundColor: `${theme.primary}10`,
        fill: '-1',
        tension: 0.1,
        pointRadius: 0,
        borderDash: [5, 5],
      }] : []),
    ],
  } : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: theme.text,
        },
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      x: {
        ticks: {
          color: theme.textSecondary,
          maxRotation: 45,
          minRotation: 45,
        },
        grid: {
          color: theme.border,
        },
      },
      y: {
        ticks: {
          color: theme.textSecondary,
        },
        grid: {
          color: theme.border,
        },
      },
    },
  };

  return (
    <div style={{
      maxWidth: '1400px',
      margin: '0 auto',
      padding: '2rem 1rem',
      color: theme.text,
    }}>
      <h1 style={{
        fontSize: '2rem',
        fontWeight: '700',
        marginBottom: '2rem',
        color: theme.text,
      }}>
        📊 Comparação de Previsões
      </h1>

      {/* Formulário */}
      <div style={{
        background: theme.cardBg,
        borderRadius: '16px',
        padding: '2rem',
        marginBottom: '2rem',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        border: `1px solid ${theme.border}`,
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <label style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: theme.textSecondary,
              marginBottom: '0.5rem',
            }}>
              ID do Modelo (series_id)
            </label>
            <input
              type="text"
              value={seriesId}
              onChange={(e) => setSeriesId(e.target.value)}
              placeholder="Ex: demanda_hospitalar"
              style={{
                width: '100%',
                padding: '0.75rem',
                borderRadius: '8px',
                border: `1px solid ${theme.border}`,
                background: theme.bg,
                color: theme.text,
                fontSize: '1rem',
              }}
            />
          </div>

          <div>
            <label style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: theme.textSecondary,
              marginBottom: '0.5rem',
            }}>
              Arquivo CSV com Valores Reais (ds, y)
            </label>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              style={{
                width: '100%',
                padding: '0.75rem',
                borderRadius: '8px',
                border: `1px solid ${theme.border}`,
                background: theme.bg,
                color: theme.text,
                fontSize: '1rem',
              }}
            />
            {csvFile && (
              <p style={{ marginTop: '0.5rem', color: theme.success, fontSize: '0.875rem' }}>
                ✓ {csvFile.name}
              </p>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: '600',
                color: theme.textSecondary,
                marginBottom: '0.5rem',
              }}>
                Data Inicial (opcional)
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  border: `1px solid ${theme.border}`,
                  background: theme.bg,
                  color: theme.text,
                  fontSize: '1rem',
                }}
              />
            </div>
            <div>
              <label style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: '600',
                color: theme.textSecondary,
                marginBottom: '0.5rem',
              }}>
                Data Final (opcional)
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  border: `1px solid ${theme.border}`,
                  background: theme.bg,
                  color: theme.text,
                  fontSize: '1rem',
                }}
              />
            </div>
          </div>

          {error && (
            <div style={{
              padding: '1rem',
              borderRadius: '8px',
              background: `${theme.danger}20`,
              border: `1px solid ${theme.danger}`,
              color: theme.danger,
            }}>
              {error}
            </div>
          )}

          <button
            onClick={handleCompare}
            disabled={loading || !seriesId || !csvFile}
            style={{
              padding: '1rem 2rem',
              borderRadius: '8px',
              border: 'none',
              background: (loading || !seriesId || !csvFile) ? theme.border : theme.primary,
              color: '#ffffff',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: (loading || !seriesId || !csvFile) ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
            }}
          >
            {loading ? '🔄 Comparando...' : '📊 Comparar Previsões'}
          </button>
        </div>
      </div>

      {/* Resultados */}
      {comparisonResult && (
        <>
          {/* Métricas */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1rem',
            marginBottom: '2rem',
          }}>
            <div style={{
              background: theme.cardBg,
              borderRadius: '12px',
              padding: '1.5rem',
              border: `1px solid ${theme.border}`,
            }}>
              <div style={{ fontSize: '0.875rem', color: theme.textSecondary, marginBottom: '0.5rem' }}>
                Qualidade Geral
              </div>
              <div style={{
                fontSize: '1.5rem',
                fontWeight: '700',
                color: getQualityColor(comparisonResult.quality_assessment.overall),
              }}>
                {getQualityLabel(comparisonResult.quality_assessment.overall)}
              </div>
            </div>

            <div style={{
              background: theme.cardBg,
              borderRadius: '12px',
              padding: '1.5rem',
              border: `1px solid ${theme.border}`,
            }}>
              <div style={{ fontSize: '0.875rem', color: theme.textSecondary, marginBottom: '0.5rem' }}>
                MAPE (Erro Percentual Médio)
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: theme.text }}>
                {comparisonResult.metrics.mape.toFixed(2)}%
              </div>
            </div>

            <div style={{
              background: theme.cardBg,
              borderRadius: '12px',
              padding: '1.5rem',
              border: `1px solid ${theme.border}`,
            }}>
              <div style={{ fontSize: '0.875rem', color: theme.textSecondary, marginBottom: '0.5rem' }}>
                RMSE (Raiz do Erro Quadrático Médio)
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: theme.text }}>
                {comparisonResult.metrics.rmse.toFixed(2)}
              </div>
            </div>

            <div style={{
              background: theme.cardBg,
              borderRadius: '12px',
              padding: '1.5rem',
              border: `1px solid ${theme.border}`,
            }}>
              <div style={{ fontSize: '0.875rem', color: theme.textSecondary, marginBottom: '0.5rem' }}>
                R² (Coeficiente de Determinação)
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: '700', color: theme.text }}>
                {comparisonResult.metrics.r2.toFixed(3)}
              </div>
            </div>
          </div>

          {/* Gráfico */}
          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '2rem',
            marginBottom: '2rem',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`,
          }}>
            <h2 style={{
              fontSize: '1.25rem',
              fontWeight: '600',
              marginBottom: '1.5rem',
              color: theme.text,
            }}>
              Comparação: Valores Reais vs Previsões
            </h2>
            <div style={{ height: '400px' }}>
              {chartData && <Line data={chartData} options={chartOptions} />}
            </div>
          </div>

          {/* Tabela de Métricas Detalhadas */}
          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '2rem',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`,
          }}>
            <h2 style={{
              fontSize: '1.25rem',
              fontWeight: '600',
              marginBottom: '1.5rem',
              color: theme.text,
            }}>
              Métricas Detalhadas
            </h2>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1rem',
            }}>
              <div>
                <div style={{ fontSize: '0.875rem', color: theme.textSecondary }}>MAE</div>
                <div style={{ fontSize: '1.25rem', fontWeight: '600', color: theme.text }}>
                  {comparisonResult.metrics.mae.toFixed(2)}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.875rem', color: theme.textSecondary }}>sMAPE</div>
                <div style={{ fontSize: '1.25rem', fontWeight: '600', color: theme.text }}>
                  {comparisonResult.metrics.smape.toFixed(2)}%
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.875rem', color: theme.textSecondary }}>MASE</div>
                <div style={{ fontSize: '1.25rem', fontWeight: '600', color: theme.text }}>
                  {comparisonResult.metrics.mase.toFixed(2)}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.875rem', color: theme.textSecondary }}>Bias</div>
                <div style={{ fontSize: '1.25rem', fontWeight: '600', color: theme.text }}>
                  {comparisonResult.metrics.bias.toFixed(2)}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default PredictionComparisonPanel;

