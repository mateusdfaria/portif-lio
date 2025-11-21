import React, { useEffect, useMemo, useRef, useState } from 'react';
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
import html2canvas from 'html2canvas';
import { saveAs } from 'file-saver';
import JoinvilleSusPanel from './components/JoinvilleSusPanel';
import HospitalSessionPanel from './components/HospitalSessionPanel';
import PredictionComparisonPanel from './components/PredictionComparisonPanel';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler);

function App() {
  const defaultApiBase = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001';
  const [apiBaseUrl, setApiBaseUrl] = useState(defaultApiBase);
  const [seriesId, setSeriesId] = useState('demanda_hospitalar');
  const [csvFile, setCsvFile] = useState(null);
  const [horizon, setHorizon] = useState(14);
  const [selectedCity, setSelectedCity] = useState(null);
  const [citySearch, setCitySearch] = useState('');
  const [cityResults, setCityResults] = useState([]);
  const [showCityDropdown, setShowCityDropdown] = useState(false);
  const [forecast, setForecast] = useState([]);
  const [insights, setInsights] = useState(null);
  const [statusMsg, setStatusMsg] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [currentView, setCurrentView] = useState('forecast');
  const [hospitalSession, setHospitalSession] = useState(() => {
    if (typeof window === 'undefined') return null;
    const stored = window.localStorage.getItem('hospicastHospitalSession');
    return stored ? JSON.parse(stored) : null;
  });
  const [hospitalHistory, setHospitalHistory] = useState([]);
  const [historyRefreshSignal, setHistoryRefreshSignal] = useState(0);
  const chartRef = useRef(null);

  const canPredict = useMemo(() => Boolean(seriesId) && Number(horizon) > 0, [seriesId, horizon]);
  const meanYhat = useMemo(() => {
    if (!forecast || forecast.length === 0) return null;
    const vals = forecast.map(r => Number(r?.yhat ?? 0)).filter(v => Number.isFinite(v));
    if (!vals.length) return null;
    const sum = vals.reduce((a, b) => a + b, 0);
    return Math.round(sum / vals.length); // Retornar número inteiro
  }, [forecast]);

  const riskLevel = useMemo(() => {
    if (meanYhat == null) return 'desconhecido';
    if (meanYhat >= 90) return 'vermelho';
    if (meanYhat >= 70) return 'amarelo';
    return 'verde';
  }, [meanYhat]);

  useEffect(() => {
    if (hospitalSession?.display_name) {
      setStatusMsg(prev => prev || `🔐 Sessão ativa para ${hospitalSession.display_name}`);
    }
  }, [hospitalSession, setStatusMsg]);

  const searchCities = async (query) => {
    if (query.length < 2) {
      setCityResults([]);
      setShowCityDropdown(false);
      return;
    }

    try {
      const response = await fetch(`${apiBaseUrl}/cities/search?q=${encodeURIComponent(query)}&limit=10`);
      if (response.ok) {
        const cities = await response.json();
        setCityResults(cities);
        setShowCityDropdown(true);
      }
    } catch (error) {
      console.error('Erro ao buscar cidades:', error);
    }
  };

  const selectCity = (city) => {
    setSelectedCity(city);
    setCitySearch(city.nome);
    setShowCityDropdown(false);
  };

  const handleTrain = async () => {
    if (!csvFile) {
      setStatusMsg('❌ Por favor, selecione um arquivo CSV');
      return;
    }

    setStatusMsg('🔄 Treinando modelo...');
    const formData = new FormData();
    formData.append('file', csvFile);
    formData.append('series_id', seriesId);

    try {
      const res = await fetch(`${apiBaseUrl}/forecast/train-file`, {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const result = await res.json();
        setStatusMsg(`✅ Modelo treinado com sucesso! (ID: ${result.series_id})`);
      } else {
        let errorMsg = 'Erro desconhecido';
        try {
          const errorData = await res.json();
          errorMsg = errorData.detail || errorData.message || JSON.stringify(errorData);
        } catch {
          const errorText = await res.text();
          errorMsg = errorText || `HTTP ${res.status}: ${res.statusText}`;
        }
        setStatusMsg(`❌ Erro ao treinar: ${errorMsg}`);
      }
    } catch (error) {
      console.error('Erro ao treinar:', error);
      const errorMsg = error.message || 'Erro de conexão. Verifique se o backend está rodando.';
      setStatusMsg(`❌ Erro ao treinar: ${errorMsg}`);
    }
  };

  const handlePredict = async () => {
    if (!selectedCity) {
      setStatusMsg('❌ Por favor, selecione uma cidade');
      return;
    }

    setStatusMsg('🔄 Gerando previsão...');

    try {
      const response = await fetch(`${apiBaseUrl}/cities/${selectedCity.id}/coordinates`);
      if (!response.ok) {
        throw new Error('Erro ao obter coordenadas da cidade');
      }
      const coords = await response.json();

      const bodyPayload = {
        series_id: seriesId,
        horizon: Number(horizon),
        latitude: coords.latitude,
        longitude: coords.longitude,
      };

      if (hospitalSession?.hospital_id && hospitalSession?.token) {
        bodyPayload.hospital_id = hospitalSession.hospital_id;
        bodyPayload.session_token = hospitalSession.token;
      }

      const res = await fetch(`${apiBaseUrl}/forecast/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyPayload),
      });

      if (res.ok) {
        const data = await res.json();
        setForecast(data.forecast || []);
        setInsights(data.insights || null);
        setStatusMsg('✅ Previsão gerada com sucesso!');
        if (hospitalSession?.hospital_id) {
          setHistoryRefreshSignal((prev) => prev + 1);
        }
      } else {
        const error = await res.text();
        setStatusMsg(`❌ Erro ao prever: ${error}`);
        if (res.status === 401 && hospitalSession) {
          setHospitalSession(null);
          if (typeof window !== 'undefined') {
            window.localStorage.removeItem('hospicastHospitalSession');
          }
        }
      }
    } catch (error) {
      setStatusMsg(`❌ Erro ao prever: ${error.message}`);
    }
  };

  const downloadChart = async () => {
    if (!chartRef.current) return;
    
    try {
      const canvas = await html2canvas(chartRef.current);
      canvas.toBlob((blob) => {
        saveAs(blob, 'previsao-hospicast.png');
      });
    } catch (error) {
      console.error('Erro ao baixar gráfico:', error);
    }
  };

  const chartData = useMemo(() => {
    if (!forecast || forecast.length === 0) return null;

    return {
      labels: forecast.map(point => new Date(point.ds).toLocaleDateString('pt-BR')),
      datasets: [
        {
          label: 'Previsão',
          data: forecast.map(point => point.yhat),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true,
          tension: 0.4,
        },
        {
          label: 'Limite Superior',
          data: forecast.map(point => point.yhat_upper),
          borderColor: 'rgb(156, 163, 175)',
          backgroundColor: 'transparent',
          borderDash: [5, 5],
          fill: false,
        },
        {
          label: 'Limite Inferior',
          data: forecast.map(point => point.yhat_lower),
          borderColor: 'rgb(156, 163, 175)',
          backgroundColor: 'transparent',
          borderDash: [5, 5],
          fill: false,
        },
      ],
    };
  }, [forecast]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: isDarkMode ? '#e5e7eb' : '#374151',
          font: { size: 12 }
        }
      },
      tooltip: {
        backgroundColor: isDarkMode ? 'rgba(17, 24, 39, 0.9)' : 'rgba(255, 255, 255, 0.9)',
        titleColor: isDarkMode ? '#e5e7eb' : '#374151',
        bodyColor: isDarkMode ? '#e5e7eb' : '#374151',
        borderColor: isDarkMode ? '#374151' : '#e5e7eb',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            // Exibir números inteiros nos tooltips
            return context.dataset.label + ': ' + Math.round(context.parsed.y);
          }
        }
      }
    },
    scales: {
      x: {
        grid: { color: isDarkMode ? '#374151' : '#e5e7eb' },
        ticks: { color: isDarkMode ? '#9ca3af' : '#6b7280' }
      },
      y: {
        grid: { color: isDarkMode ? '#374151' : '#e5e7eb' },
        ticks: { 
          color: isDarkMode ? '#9ca3af' : '#6b7280',
          callback: function(value) {
            return Math.round(value); // Exibir números inteiros no eixo Y
          }
        }
      }
    }
  };

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
    gradient: isDarkMode 
      ? 'linear-gradient(135deg, #1e293b 0%, #334155 100%)'
      : 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
    shadow: isDarkMode 
      ? '0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.1)'
      : '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
  };

  return (
    <div style={{
      minHeight: '100vh',
      width: '100vw',
      margin: 0,
      padding: 0,
      background: isDarkMode 
        ? 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)'
        : 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0f9ff 100%)',
      color: theme.text,
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      transition: 'all 0.3s ease',
      overflowX: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        background: theme.gradient,
        padding: '2rem 0',
        boxShadow: theme.shadow,
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 1rem',
          position: 'relative',
          zIndex: 1,
          width: '100%',
          boxSizing: 'border-box'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem'
          }}>
            <div>
              <h1 style={{
                fontSize: '2.5rem',
                fontWeight: '800',
                color: '#ffffff',
                margin: '0 0 0.5rem 0',
                textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
              }}>
                🏥 HospiCast
              </h1>
              <p style={{
                fontSize: '1.125rem',
                color: 'rgba(255, 255, 255, 0.9)',
                margin: 0,
                fontWeight: '500'
              }}>
                HospiCast - Previsão e Monitoramento Hospitalar
              </p>
            </div>
            
            <div style={{
              display: 'flex',
              gap: '1rem',
              alignItems: 'center'
            }}>
              {/* Navegação */}
              <div style={{
                display: 'flex',
                background: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '12px',
                padding: '0.25rem',
                backdropFilter: 'blur(10px)'
              }}>
                <button
                  onClick={() => setCurrentView('forecast')}
                  style={{
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    border: 'none',
                    background: currentView === 'forecast' ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
                    color: '#ffffff',
                    fontSize: '0.875rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                  }}
                >
                  🔮 Previsão
                </button>
                <button
                  onClick={() => setCurrentView('joinville-sus')}
                  style={{
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    border: 'none',
                    background: currentView === 'joinville-sus' ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
                    color: '#ffffff',
                    fontSize: '0.875rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                  }}
                >
                  🏥 Monitoramento SUS
                </button>
                <button
                  onClick={() => setCurrentView('comparison')}
                  style={{
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    border: 'none',
                    background: currentView === 'comparison' ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
                    color: '#ffffff',
                    fontSize: '0.875rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                  }}
                >
                  📊 Comparar Previsões
                </button>
              </div>
            
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                style={{
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '12px',
                  padding: '0.75rem 1rem',
                  color: '#ffffff',
                  fontSize: '0.875rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  backdropFilter: 'blur(10px)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                {isDarkMode ? '☀️' : '🌙'} {isDarkMode ? 'Claro' : 'Escuro'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      {currentView === 'joinville-sus' ? (
        <JoinvilleSusPanel apiBaseUrl={apiBaseUrl} isDarkMode={isDarkMode} />
      ) : currentView === 'comparison' ? (
        <PredictionComparisonPanel apiBaseUrl={apiBaseUrl} isDarkMode={isDarkMode} />
      ) : (
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '2rem 1rem',
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '2rem',
          alignItems: 'start',
          width: '100%',
          boxSizing: 'border-box'
        }}>
          {/* Left Column - Controls */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '1.5rem'
          }}>
            <HospitalSessionPanel
              apiBaseUrl={apiBaseUrl}
              session={hospitalSession}
              onSessionChange={setHospitalSession}
              history={hospitalHistory}
              onHistoryChange={setHospitalHistory}
              setStatusMsg={setStatusMsg}
              refreshSignal={historyRefreshSignal}
            />
            {/* Configuration Card */}
            <div style={{
              background: theme.cardBg,
              borderRadius: '16px',
              padding: '2rem',
              boxShadow: theme.shadow,
              border: `1px solid ${theme.border}`,
              transition: 'all 0.3s ease'
            }}>
              <h2 style={{
                fontSize: '1.5rem',
                fontWeight: '700',
                color: theme.text,
                margin: '0 0 1.5rem 0',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                ⚙️ Configuração
              </h2>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '0.875rem',
                    fontWeight: '600',
                    color: theme.textSecondary,
                    marginBottom: '0.5rem'
                  }}>
                    URL da API
                  </label>
                  <input
                    type="text"
                    value={apiBaseUrl}
                    onChange={(e) => setApiBaseUrl(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      borderRadius: '8px',
                      border: `1px solid ${theme.border}`,
                      background: theme.bg,
                      color: theme.text,
                      fontSize: '0.875rem',
                      transition: 'all 0.3s ease'
                    }}
                  />
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '0.875rem',
                    fontWeight: '600',
                    color: theme.textSecondary,
                    marginBottom: '0.5rem'
                  }}>
                    ID da Série
                  </label>
                  <input
                    type="text"
                    value={seriesId}
                    onChange={(e) => setSeriesId(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      borderRadius: '8px',
                      border: `1px solid ${theme.border}`,
                      background: theme.bg,
                      color: theme.text,
                      fontSize: '0.875rem',
                      transition: 'all 0.3s ease'
                    }}
                  />
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '0.875rem',
                    fontWeight: '600',
                    color: theme.textSecondary,
                    marginBottom: '0.5rem'
                  }}>
                    Horizonte (dias)
                  </label>
                  <input
                    type="number"
                    value={horizon}
                    onChange={(e) => setHorizon(Number(e.target.value))}
                    min="1"
                    max="365"
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      borderRadius: '8px',
                      border: `1px solid ${theme.border}`,
                      background: theme.bg,
                      color: theme.text,
                      fontSize: '0.875rem',
                      transition: 'all 0.3s ease'
                    }}
                  />
                </div>
              </div>
            </div>

            {/* City Selection Card */}
            <div style={{
              background: theme.cardBg,
              borderRadius: '16px',
              padding: '2rem',
              boxShadow: theme.shadow,
              border: `1px solid ${theme.border}`,
              transition: 'all 0.3s ease'
            }}>
              <h2 style={{
                fontSize: '1.5rem',
                fontWeight: '700',
                color: theme.text,
                margin: '0 0 1.5rem 0',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                🏙️ Seleção de Cidade
              </h2>

              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  value={citySearch}
                  onChange={(e) => {
                    setCitySearch(e.target.value);
                    searchCities(e.target.value);
                  }}
                  onFocus={() => setShowCityDropdown(cityResults.length > 0)}
                  placeholder="Digite o nome da cidade..."
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    borderRadius: '8px',
                    border: `1px solid ${theme.border}`,
                    background: theme.bg,
                    color: theme.text,
                    fontSize: '0.875rem',
                    transition: 'all 0.3s ease'
                  }}
                />
                
                {showCityDropdown && cityResults.length > 0 && (
                  <div style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    right: 0,
                    background: theme.cardBg,
                    border: `1px solid ${theme.border}`,
                    borderRadius: '8px',
                    boxShadow: theme.shadow,
                    zIndex: 1000,
                    maxHeight: '200px',
                    overflowY: 'auto'
                  }}>
                    {cityResults.map((city) => (
                      <div
                        key={city.id}
                        onClick={() => selectCity(city)}
                        style={{
                          padding: '0.75rem',
                          cursor: 'pointer',
                          borderBottom: `1px solid ${theme.border}`,
                          transition: 'all 0.2s ease'
                        }}
                      >
                        <div style={{ fontWeight: '600', color: theme.text }}>
                          {city.nome}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: theme.textSecondary }}>
                          {city.estado} - {city.regiao}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {selectedCity && (
                <div style={{
                  marginTop: '1rem',
                  padding: '1rem',
                  background: theme.primary + '10',
                  borderRadius: '8px',
                  border: `1px solid ${theme.primary}30`
                }}>
                  <div style={{ fontWeight: '600', color: theme.text }}>
                    ✅ {selectedCity.nome}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: theme.textSecondary }}>
                    {selectedCity.estado} - {selectedCity.regiao}
                  </div>
                </div>
              )}
            </div>

            {/* File Upload Card */}
            <div style={{
              background: theme.cardBg,
              borderRadius: '16px',
              padding: '2rem',
              boxShadow: theme.shadow,
              border: `1px solid ${theme.border}`,
              transition: 'all 0.3s ease'
            }}>
              <h2 style={{
                fontSize: '1.5rem',
                fontWeight: '700',
                color: theme.text,
                margin: '0 0 1.5rem 0',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                📁 Upload de Dados
              </h2>

              <input
                type="file"
                accept=".csv"
                onChange={(e) => setCsvFile(e.target.files[0])}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  border: `2px dashed ${theme.border}`,
                  background: theme.bg,
                  color: theme.text,
                  fontSize: '0.875rem',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
              />

              {csvFile && (
                <div style={{
                  marginTop: '1rem',
                  padding: '1rem',
                  background: theme.success + '10',
                  borderRadius: '8px',
                  border: `1px solid ${theme.success}30`
                }}>
                  <div style={{ fontWeight: '600', color: theme.text }}>
                    ✅ {csvFile.name}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: theme.textSecondary }}>
                    {(csvFile.size / 1024).toFixed(1)} KB
                  </div>
                </div>
              )}
            </div>

            {/* Actions Card */}
            <div style={{
              background: theme.cardBg,
              borderRadius: '16px',
              padding: '2rem',
              boxShadow: theme.shadow,
              border: `1px solid ${theme.border}`,
              transition: 'all 0.3s ease'
            }}>
              <h2 style={{
                fontSize: '1.5rem',
                fontWeight: '700',
                color: theme.text,
                margin: '0 0 1.5rem 0',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                🚀 Ações
              </h2>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <button
                  onClick={handleTrain}
                  disabled={!csvFile}
                  style={{
                    width: '100%',
                    padding: '1rem',
                    borderRadius: '12px',
                    border: 'none',
                    background: csvFile ? theme.primary : theme.border,
                    color: csvFile ? '#ffffff' : theme.textSecondary,
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: csvFile ? 'pointer' : 'not-allowed',
                    transition: 'all 0.3s ease',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.5rem'
                  }}
                >
                  🎯 Treinar Modelo
                </button>

                <button
                  onClick={handlePredict}
                  disabled={!canPredict || !selectedCity}
                  style={{
                    width: '100%',
                    padding: '1rem',
                    borderRadius: '12px',
                    border: 'none',
                    background: (canPredict && selectedCity) ? theme.success : theme.border,
                    color: (canPredict && selectedCity) ? '#ffffff' : theme.textSecondary,
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: (canPredict && selectedCity) ? 'pointer' : 'not-allowed',
                    transition: 'all 0.3s ease',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.5rem'
                  }}
                >
                  🔮 Gerar Previsão
                </button>

                {forecast.length > 0 && (
                  <button
                    onClick={downloadChart}
                    style={{
                      width: '100%',
                      padding: '1rem',
                      borderRadius: '12px',
                      border: `1px solid ${theme.border}`,
                      background: theme.bg,
                      color: theme.text,
                      fontSize: '1rem',
                      fontWeight: '600',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem'
                    }}
                  >
                    📥 Baixar Gráfico
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Results */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '1.5rem'
          }}>
            {/* Status Card */}
            {statusMsg && (
              <div style={{
                background: theme.cardBg,
                borderRadius: '16px',
                padding: '1.5rem',
                boxShadow: theme.shadow,
                border: `1px solid ${theme.border}`,
                transition: 'all 0.3s ease'
              }}>
                <div style={{
                  fontSize: '1rem',
                  fontWeight: '600',
                  color: theme.text,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  {statusMsg}
                </div>
              </div>
            )}

            {/* Forecast Summary Card */}
            {forecast.length > 0 && (
              <div style={{
                background: theme.cardBg,
                borderRadius: '16px',
                padding: '2rem',
                boxShadow: theme.shadow,
                border: `1px solid ${theme.border}`,
                transition: 'all 0.3s ease'
              }}>
                <h2 style={{
                  fontSize: '1.5rem',
                  fontWeight: '700',
                  color: theme.text,
                  margin: '0 0 1.5rem 0',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  📊 Resumo da Previsão
                </h2>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                  gap: '1rem'
                }}>
                  <div style={{
                    padding: '1rem',
                    background: theme.primary + '10',
                    borderRadius: '12px',
                    border: `1px solid ${theme.primary}30`,
                    textAlign: 'center'
                  }}>
                    <div style={{
                      fontSize: '1.5rem',
                      fontWeight: '700',
                      color: theme.primary,
                      marginBottom: '0.25rem'
                    }}>
                      {meanYhat ? meanYhat : 'N/A'}
                    </div>
                    <div style={{
                      fontSize: '0.875rem',
                      color: theme.textSecondary,
                      fontWeight: '500'
                    }}>
                      Média Prevista
                    </div>
                  </div>

                  <div style={{
                    padding: '1rem',
                    background: riskLevel === 'verde' ? theme.success + '10' : 
                               riskLevel === 'amarelo' ? theme.warning + '10' : 
                               theme.danger + '10',
                    borderRadius: '12px',
                    border: `1px solid ${riskLevel === 'verde' ? theme.success + '30' : 
                                      riskLevel === 'amarelo' ? theme.warning + '30' : 
                                      theme.danger + '30'}`,
                    textAlign: 'center'
                  }}>
                    <div style={{
                      fontSize: '1.5rem',
                      fontWeight: '700',
                      color: riskLevel === 'verde' ? theme.success : 
                             riskLevel === 'amarelo' ? theme.warning : 
                             theme.danger,
                      marginBottom: '0.25rem'
                    }}>
                      {riskLevel === 'verde' ? '🟢' : riskLevel === 'amarelo' ? '🟡' : '🔴'}
                    </div>
                    <div style={{
                      fontSize: '0.875rem',
                      color: theme.textSecondary,
                      fontWeight: '500'
                    }}>
                      Nível de Risco
                    </div>
                  </div>

                  <div style={{
                    padding: '1rem',
                    background: theme.cardBg,
                    borderRadius: '12px',
                    border: `1px solid ${theme.border}`,
                    textAlign: 'center'
                  }}>
                    <div style={{
                      fontSize: '1.5rem',
                      fontWeight: '700',
                      color: theme.text,
                      marginBottom: '0.25rem'
                    }}>
                      {horizon}
                    </div>
                    <div style={{
                      fontSize: '0.875rem',
                      color: theme.textSecondary,
                      fontWeight: '500'
                    }}>
                      Dias Previstos
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Chart Card */}
            {chartData && (
              <div style={{
                background: theme.cardBg,
                borderRadius: '16px',
                padding: '2rem',
                boxShadow: theme.shadow,
                border: `1px solid ${theme.border}`,
                transition: 'all 0.3s ease'
              }}>
                <h2 style={{
                  fontSize: '1.5rem',
                  fontWeight: '700',
                  color: theme.text,
                  margin: '0 0 1.5rem 0',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  📈 Gráfico de Previsão
                </h2>

                <div ref={chartRef} style={{ height: '400px', width: '100%' }}>
                  <Line data={chartData} options={chartOptions} />
                </div>
              </div>
            )}

            {/* Insights Card */}
            {insights && insights.insights && insights.insights.length > 0 && (
              <div style={{
                background: theme.cardBg,
                borderRadius: '16px',
                padding: '2rem',
                boxShadow: theme.shadow,
                border: `1px solid ${theme.border}`,
                transition: 'all 0.3s ease'
              }}>
                <h2 style={{
                  fontSize: '1.5rem',
                  fontWeight: '700',
                  color: theme.text,
                  margin: '0 0 1.5rem 0',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  🧠 Insights Inteligentes
                </h2>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {insights.insights.map((insight, index) => (
                    <div
                      key={index}
                      style={{
                        padding: '1.5rem',
                        background: insight.impact === 'high' ? theme.danger + '05' :
                                   insight.impact === 'medium' ? theme.warning + '05' :
                                   theme.success + '05',
                        borderRadius: '12px',
                        border: `1px solid ${insight.impact === 'high' ? theme.danger + '20' :
                                          insight.impact === 'medium' ? theme.warning + '20' :
                                          theme.success + '20'}`,
                        transition: 'all 0.3s ease'
                      }}
                    >
                      <div style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '1rem'
                      }}>
                        <div style={{
                          fontSize: '1.5rem',
                          flexShrink: 0
                        }}>
                          {insight.type === 'heat_wave' ? '🌡️' :
                           insight.type === 'cold_period' ? '❄️' :
                           insight.type === 'heavy_rain' ? '🌧️' :
                           insight.type === 'holiday_bridge' ? '🌉' :
                           insight.type === 'extraordinary_event' ? '⚠️' :
                           insight.type === 'demand_peak' ? '📈' :
                           insight.type === 'capacity_alert' ? '🚨' :
                           '💡'}
                        </div>
                        <div style={{ flex: 1 }}>
                          <h4 style={{
                            fontSize: '1.125rem',
                            fontWeight: '600',
                            color: theme.text,
                            margin: '0 0 8px 0'
                          }}>
                            {insight.title}
                          </h4>
                          <p style={{
                            fontSize: '0.875rem',
                            color: theme.textSecondary,
                            margin: '0 0 8px 0',
                            lineHeight: '1.5'
                          }}>
                            {insight.message}
                          </p>
                          {insight.date && (
                            <div style={{
                              fontSize: '0.75rem',
                              color: theme.textSecondary,
                              fontWeight: '500'
                            }}>
                              📅 {insight.date}
                            </div>
                          )}
                          {insight.expected_increase && (
                            <div style={{
                              fontSize: '0.75rem',
                              color: theme.success,
                              fontWeight: '600',
                              background: theme.success + '10',
                              padding: '4px 8px',
                              borderRadius: '6px',
                              display: 'inline-block',
                              marginTop: '8px'
                            }}>
                              📊 {insight.expected_increase}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <div style={{
        background: theme.gradient,
        padding: '2rem 0',
        marginTop: '4rem',
        textAlign: 'center'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 1rem',
          width: '100%',
          boxSizing: 'border-box'
        }}>
          <p style={{
            color: 'rgba(255, 255, 255, 0.9)',
            fontSize: '0.875rem',
            margin: 0,
            fontWeight: '500'
          }}>
            🏥 HospiCast - Sistema Inteligente de Previsão Hospitalar
          </p>
          <p style={{
            color: 'rgba(255, 255, 255, 0.7)',
            fontSize: '0.75rem',
            margin: '0.5rem 0 0 0'
          }}>
            Powered by Prophet AI & Advanced Analytics
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;