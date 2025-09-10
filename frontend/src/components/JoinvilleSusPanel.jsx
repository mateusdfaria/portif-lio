import React, { useState, useEffect } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Tooltip,
  Legend,
  Filler
);

const JoinvilleSusPanel = ({ apiBaseUrl, isDarkMode }) => {
  const [hospitals, setHospitals] = useState([]);
  const [selectedHospital, setSelectedHospital] = useState(null);
  const [hospitalData, setHospitalData] = useState([]);
  const [hospitalKpis, setHospitalKpis] = useState(null);
  const [summary, setSummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

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
    sus: '#1e40af', // Cor específica para SUS
  };

  // Definir datas padrão (últimos 30 dias)
  useEffect(() => {
    const today = new Date();
    const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
    
    setEndDate(today.toISOString().split('T')[0]);
    setStartDate(thirtyDaysAgo.toISOString().split('T')[0]);
  }, []);

  // Carregar hospitais
  const loadHospitals = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/joinville-sus/hospitals`);
      if (response.ok) {
        const data = await response.json();
        setHospitals(data.hospitals || []);
      }
    } catch (error) {
      console.error('Erro ao carregar hospitais:', error);
    }
  };

  // Carregar dados do hospital selecionado
  const loadHospitalData = async () => {
    if (!selectedHospital || !startDate || !endDate) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch(
        `${apiBaseUrl}/joinville-sus/hospitals/${selectedHospital.cnes}/sus-data?start_date=${startDate}&end_date=${endDate}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setHospitalData(data.data || []);
      } else {
        setError('Erro ao carregar dados do hospital');
      }
    } catch (error) {
      setError('Erro ao carregar dados do hospital');
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  // Carregar KPIs do hospital
  const loadHospitalKpis = async () => {
    if (!selectedHospital || !startDate || !endDate) return;

    try {
      const response = await fetch(
        `${apiBaseUrl}/joinville-sus/hospitals/${selectedHospital.cnes}/sus-kpis?start_date=${startDate}&end_date=${endDate}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setHospitalKpis(data);
      }
    } catch (error) {
      console.error('Erro ao carregar KPIs:', error);
    }
  };

  // Carregar resumo geral
  const loadSummary = async () => {
    if (!startDate || !endDate) return;

    try {
      const response = await fetch(
        `${apiBaseUrl}/joinville-sus/summary?start_date=${startDate}&end_date=${endDate}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setSummary(data);
      }
    } catch (error) {
      console.error('Erro ao carregar resumo:', error);
    }
  };

  // Carregar alertas
  const loadAlerts = async () => {
    if (!startDate || !endDate) return;

    try {
      const response = await fetch(
        `${apiBaseUrl}/joinville-sus/alerts?start_date=${startDate}&end_date=${endDate}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts || []);
      }
    } catch (error) {
      console.error('Erro ao carregar alertas:', error);
    }
  };

  // Carregar dados quando hospital ou datas mudarem
  useEffect(() => {
    if (selectedHospital && startDate && endDate) {
      loadHospitalData();
      loadHospitalKpis();
    }
  }, [selectedHospital, startDate, endDate]);

  // Carregar dados gerais quando datas mudarem
  useEffect(() => {
    if (startDate && endDate) {
      loadSummary();
      loadAlerts();
    }
  }, [startDate, endDate]);

  // Carregar hospitais
  useEffect(() => {
    loadHospitals();
  }, []);

  // Preparar dados para gráficos
  const chartData = React.useMemo(() => {
    if (!hospitalData.length) return null;

    const labels = hospitalData.map(d => new Date(d.date).toLocaleDateString('pt-BR'));
    const occupancyRates = hospitalData.map(d => d.ocupacao_leitos * 100);
    const utiOccupancy = hospitalData.map(d => d.ocupacao_uti * 100);
    const emergencyOccupancy = hospitalData.map(d => d.ocupacao_emergencia * 100);
    const waitTimes = hospitalData.map(d => d.tempo_espera_medio);
    const admissions = hospitalData.map(d => d.admissoes_dia);
    const procedures = hospitalData.map(d => d.procedimentos_realizados);

    return {
      occupancy: {
        labels,
        datasets: [
          {
            label: 'Ocupação Geral (%)',
            data: occupancyRates,
            borderColor: theme.sus,
            backgroundColor: theme.sus + '20',
            fill: true,
            tension: 0.4,
          },
          {
            label: 'Ocupação UTI (%)',
            data: utiOccupancy,
            borderColor: theme.danger,
            backgroundColor: theme.danger + '20',
            fill: true,
            tension: 0.4,
          },
          {
            label: 'Ocupação Emergência (%)',
            data: emergencyOccupancy,
            borderColor: theme.warning,
            backgroundColor: theme.warning + '20',
            fill: true,
            tension: 0.4,
          },
        ],
      },
      activities: {
        labels,
        datasets: [
          {
            label: 'Admissões',
            data: admissions,
            backgroundColor: theme.success + '80',
            borderColor: theme.success,
            borderWidth: 1,
          },
          {
            label: 'Procedimentos',
            data: procedures,
            backgroundColor: theme.primary + '80',
            borderColor: theme.primary,
            borderWidth: 1,
          },
        ],
      },
      waitTime: {
        labels,
        datasets: [
          {
            label: 'Tempo de Espera (min)',
            data: waitTimes,
            backgroundColor: theme.warning + '80',
            borderColor: theme.warning,
            borderWidth: 1,
          },
        ],
      },
    };
  }, [hospitalData, theme]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: theme.text,
          font: { size: 12 }
        }
      },
      tooltip: {
        backgroundColor: isDarkMode ? 'rgba(17, 24, 39, 0.9)' : 'rgba(255, 255, 255, 0.9)',
        titleColor: theme.text,
        bodyColor: theme.text,
        borderColor: theme.border,
        borderWidth: 1,
      }
    },
    scales: {
      x: {
        grid: { color: theme.border },
        ticks: { color: theme.textSecondary }
      },
      y: {
        grid: { color: theme.border },
        ticks: { color: theme.textSecondary }
      }
    }
  };

  return (
    <div style={{
      maxWidth: '1400px',
      margin: '0 auto',
      padding: '2rem 1rem',
      color: theme.text,
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      {/* Header */}
      <div style={{
        background: theme.cardBg,
        borderRadius: '16px',
        padding: '2rem',
        boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
        border: `1px solid ${theme.border}`,
        marginBottom: '2rem'
      }}>
        <h1 style={{
          fontSize: '2rem',
          fontWeight: '700',
          color: theme.text,
          margin: '0 0 1rem 0',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          🏥 Hospitais Públicos de Joinville - SUS
        </h1>
        <p style={{
          fontSize: '1rem',
          color: theme.textSecondary,
          margin: 0
        }}>
          Dados reais dos hospitais públicos de Joinville via Sistema Único de Saúde
        </p>
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          background: theme.warning + '10',
          borderRadius: '8px',
          border: `1px solid ${theme.warning}30`
        }}>
          <div style={{ fontSize: '0.875rem', color: theme.textSecondary }}>
            <strong>Inclui:</strong> Hospital Municipal São José, Hospital Infantil Dr. Jeser Amarante Faria, Hospital Regional Hans Dieter Schmidt
          </div>
        </div>
        {summary && (
          <div style={{
            marginTop: '1rem',
            padding: '1rem',
            background: theme.sus + '10',
            borderRadius: '8px',
            border: `1px solid ${theme.sus}30`
          }}>
            <div style={{ fontSize: '0.875rem', color: theme.textSecondary }}>
              <strong>Total de Hospitais:</strong> {summary.hospitals_count} | 
              <strong> Capacidade Total:</strong> {summary.total_capacity} leitos | 
              <strong> Ocupação Média:</strong> {summary.avg_occupancy}%
            </div>
          </div>
        )}
      </div>

      {/* Filtros */}
      <div style={{
        background: theme.cardBg,
        borderRadius: '16px',
        padding: '2rem',
        boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
        border: `1px solid ${theme.border}`,
        marginBottom: '2rem'
      }}>
        <h2 style={{
          fontSize: '1.5rem',
          fontWeight: '600',
          color: theme.text,
          margin: '0 0 1.5rem 0'
        }}>
          🔍 Filtros
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1rem'
        }}>
          {/* Seleção de Hospital */}
          <div>
            <label style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: theme.textSecondary,
              marginBottom: '0.5rem'
            }}>
              Hospital
            </label>
            <select
              value={selectedHospital?.cnes || ''}
              onChange={(e) => {
                const hospital = hospitals.find(h => h.cnes === e.target.value);
                setSelectedHospital(hospital || null);
              }}
              style={{
                width: '100%',
                padding: '0.75rem',
                borderRadius: '8px',
                border: `1px solid ${theme.border}`,
                background: theme.bg,
                color: theme.text,
                fontSize: '0.875rem'
              }}
            >
              <option value="">Selecione um hospital...</option>
              {hospitals.map(hospital => (
                <option key={hospital.cnes} value={hospital.cnes}>
                  {hospital.nome.includes('Infantil') ? '👶 ' : '🏥 '}{hospital.nome} - {hospital.tipo_gestao}
                </option>
              ))}
            </select>
          </div>

          {/* Data Inicial */}
          <div>
            <label style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: theme.textSecondary,
              marginBottom: '0.5rem'
            }}>
              Data Inicial
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
                fontSize: '0.875rem'
              }}
            />
          </div>

          {/* Data Final */}
          <div>
            <label style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: theme.textSecondary,
              marginBottom: '0.5rem'
            }}>
              Data Final
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
                fontSize: '0.875rem'
              }}
            />
          </div>
        </div>

        {error && (
          <div style={{
            marginTop: '1rem',
            padding: '1rem',
            background: theme.danger + '10',
            borderRadius: '8px',
            border: `1px solid ${theme.danger}30`,
            color: theme.danger,
            fontSize: '0.875rem'
          }}>
            ❌ {error}
          </div>
        )}
      </div>

      {/* Resumo Geral */}
      {summary && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem',
          marginBottom: '2rem'
        }}>
          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '1.5rem',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`,
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '2rem',
              fontWeight: '700',
              color: theme.sus,
              marginBottom: '0.5rem'
            }}>
              {summary.hospitals_count}
            </div>
            <div style={{
              fontSize: '0.875rem',
              color: theme.textSecondary,
              fontWeight: '500'
            }}>
              Hospitais Públicos
            </div>
          </div>

          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '1.5rem',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`,
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '2rem',
              fontWeight: '700',
              color: theme.primary,
              marginBottom: '0.5rem'
            }}>
              {summary.total_capacity}
            </div>
            <div style={{
              fontSize: '0.875rem',
              color: theme.textSecondary,
              fontWeight: '500'
            }}>
              Leitos Totais
            </div>
          </div>

          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '1.5rem',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`,
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '2rem',
              fontWeight: '700',
              color: theme.warning,
              marginBottom: '0.5rem'
            }}>
              {summary.avg_occupancy}%
            </div>
            <div style={{
              fontSize: '0.875rem',
              color: theme.textSecondary,
              fontWeight: '500'
            }}>
              Ocupação Média
            </div>
          </div>

          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '1.5rem',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`,
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '2rem',
              fontWeight: '700',
              color: theme.success,
              marginBottom: '0.5rem'
            }}>
              {summary.total_admissions}
            </div>
            <div style={{
              fontSize: '0.875rem',
              color: theme.textSecondary,
              fontWeight: '500'
            }}>
              Total de Admissões
            </div>
          </div>
        </div>
      )}

      {/* KPIs do Hospital Selecionado */}
      {hospitalKpis && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem',
          marginBottom: '2rem'
        }}>
          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '1.5rem',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`,
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '2rem',
              fontWeight: '700',
              color: theme.sus,
              marginBottom: '0.5rem'
            }}>
              {hospitalKpis.kpis.avg_occupancy_rate}%
            </div>
            <div style={{
              fontSize: '0.875rem',
              color: theme.textSecondary,
              fontWeight: '500'
            }}>
              Ocupação Geral
            </div>
          </div>

          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '1.5rem',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`,
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '2rem',
              fontWeight: '700',
              color: theme.danger,
              marginBottom: '0.5rem'
            }}>
              {hospitalKpis.kpis.avg_uti_occupancy}%
            </div>
            <div style={{
              fontSize: '0.875rem',
              color: theme.textSecondary,
              fontWeight: '500'
            }}>
              Ocupação UTI
            </div>
          </div>

          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '1.5rem',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`,
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '2rem',
              fontWeight: '700',
              color: theme.warning,
              marginBottom: '0.5rem'
            }}>
              {hospitalKpis.kpis.avg_wait_time} min
            </div>
            <div style={{
              fontSize: '0.875rem',
              color: theme.textSecondary,
              fontWeight: '500'
            }}>
              Tempo de Espera
            </div>
          </div>

          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '1.5rem',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`,
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '2rem',
              fontWeight: '700',
              color: theme.primary,
              marginBottom: '0.5rem'
            }}>
              {hospitalKpis.kpis.total_procedures}
            </div>
            <div style={{
              fontSize: '0.875rem',
              color: theme.textSecondary,
              fontWeight: '500'
            }}>
              Procedimentos
            </div>
          </div>

          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '1.5rem',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`,
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '2rem',
              fontWeight: '700',
              color: theme.success,
              marginBottom: '0.5rem'
            }}>
              {hospitalKpis.kpis.procedure_rate}%
            </div>
            <div style={{
              fontSize: '0.875rem',
              color: theme.textSecondary,
              fontWeight: '500'
            }}>
              Taxa de Procedimentos
            </div>
          </div>

          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '1.5rem',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`,
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '2rem',
              fontWeight: '700',
              color: theme.text,
              marginBottom: '0.5rem'
            }}>
              {hospitalKpis.kpis.efficiency_rate}%
            </div>
            <div style={{
              fontSize: '0.875rem',
              color: theme.textSecondary,
              fontWeight: '500'
            }}>
              Taxa de Eficiência
            </div>
          </div>
        </div>
      )}

      {/* Gráficos */}
      {chartData && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: '2rem',
          marginBottom: '2rem'
        }}>
          {/* Gráfico de Ocupação */}
          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '2rem',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`
          }}>
            <h3 style={{
              fontSize: '1.25rem',
              fontWeight: '600',
              color: theme.text,
              margin: '0 0 1rem 0'
            }}>
              📊 Ocupação Hospitalar
            </h3>
            <div style={{ height: '300px' }}>
              <Line data={chartData.occupancy} options={chartOptions} />
            </div>
          </div>

          {/* Gráfico de Atividades */}
          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '2rem',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`
          }}>
            <h3 style={{
              fontSize: '1.25rem',
              fontWeight: '600',
              color: theme.text,
              margin: '0 0 1rem 0'
            }}>
              🏥 Atividades Hospitalares
            </h3>
            <div style={{ height: '300px' }}>
              <Bar data={chartData.activities} options={chartOptions} />
            </div>
          </div>

          {/* Gráfico de Tempo de Espera */}
          <div style={{
            background: theme.cardBg,
            borderRadius: '16px',
            padding: '2rem',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
            border: `1px solid ${theme.border}`
          }}>
            <h3 style={{
              fontSize: '1.25rem',
              fontWeight: '600',
              color: theme.text,
              margin: '0 0 1rem 0'
            }}>
              ⏱️ Tempo de Espera
            </h3>
            <div style={{ height: '300px' }}>
              <Bar data={chartData.waitTime} options={chartOptions} />
            </div>
          </div>
        </div>
      )}

      {/* Alertas */}
      {alerts.length > 0 && (
        <div style={{
          background: theme.cardBg,
          borderRadius: '16px',
          padding: '2rem',
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
          border: `1px solid ${theme.border}`,
          marginBottom: '2rem'
        }}>
          <h3 style={{
            fontSize: '1.25rem',
            fontWeight: '600',
            color: theme.text,
            margin: '0 0 1rem 0'
          }}>
            🚨 Alertas dos Hospitais SUS
          </h3>
          
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {alerts.slice(0, 10).map((alert, index) => (
              <div
                key={index}
                style={{
                  padding: '1rem',
                  background: alert.level === 'critical' ? theme.danger + '10' : theme.warning + '10',
                  borderRadius: '8px',
                  border: `1px solid ${alert.level === 'critical' ? theme.danger + '30' : theme.warning + '30'}`,
                  marginBottom: '0.5rem'
                }}
              >
                <div style={{
                  fontSize: '0.875rem',
                  fontWeight: '600',
                  color: alert.level === 'critical' ? theme.danger : theme.warning,
                  marginBottom: '0.25rem'
                }}>
                  {alert.level === 'critical' ? '🚨' : '⚠️'} {alert.hospital} - {alert.message}
                </div>
                <div style={{
                  fontSize: '0.75rem',
                  color: theme.textSecondary
                }}>
                  {new Date(alert.date).toLocaleDateString('pt-BR')} - {alert.type.replace('_', ' ').toUpperCase()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading && (
        <div style={{
          position: 'fixed',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: theme.cardBg,
          padding: '2rem',
          borderRadius: '16px',
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
          border: `1px solid ${theme.border}`,
          zIndex: 1000
        }}>
          <div style={{
            fontSize: '1rem',
            color: theme.text,
            textAlign: 'center'
          }}>
            🔄 Carregando dados SUS...
          </div>
        </div>
      )}
    </div>
  );
};

export default JoinvilleSusPanel;
