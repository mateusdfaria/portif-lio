import React, { useMemo, useState } from 'react';

function App() {
  const [apiBaseUrl, setApiBaseUrl] = useState('http://localhost:8000');
  const [seriesId, setSeriesId] = useState('demanda_hospitalar');
  const [csvFile, setCsvFile] = useState(null);
  const [horizon, setHorizon] = useState(14);
  const [forecast, setForecast] = useState([]);
  const [statusMsg, setStatusMsg] = useState('');

  const canPredict = useMemo(() => Boolean(seriesId) && Number(horizon) > 0, [seriesId, horizon]);

  async function handleTrainCsv(e) {
    e.preventDefault();
    if (!csvFile || !seriesId) {
      setStatusMsg('Selecione um arquivo CSV e informe a série.');
      return;
    }
    try {
      setStatusMsg('Enviando e treinando modelo...');
      const form = new FormData();
      form.append('series_id', seriesId);
      form.append('file', csvFile);
      const res = await fetch(`${apiBaseUrl}/forecast/train-file`, {
        method: 'POST',
        body: form,
      });
      if (!res.ok) throw new Error(await res.text());
      setStatusMsg('Modelo treinado com sucesso.');
    } catch (err) {
      setStatusMsg(`Erro ao treinar: ${err}`);
    }
  }

  async function handlePredict(e) {
    e.preventDefault();
    if (!canPredict) return;
    try {
      setStatusMsg('Calculando previsão...');
      const res = await fetch(`${apiBaseUrl}/forecast/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ series_id: seriesId, horizon: Number(horizon) }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setForecast(data.forecast || []);
      setStatusMsg('Previsão concluída.');
    } catch (err) {
      setStatusMsg(`Erro ao prever: ${err}`);
    }
  }

  return (
    <div style={{ maxWidth: 920, margin: '0 auto', padding: 24, fontFamily: 'Inter, system-ui, Arial' }}>
      <h1>HospiCast - Frontend</h1>
      <p>Treine um modelo Prophet com CSV (colunas ds,y) e gere previsões.</p>

      <section style={{ marginTop: 24 }}>
        <h3>Configuração</h3>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <label>
            API Base URL
            <input style={{ marginLeft: 8 }} value={apiBaseUrl} onChange={(e) => setApiBaseUrl(e.target.value)} />
          </label>
          <label>
            Série (ID)
            <input style={{ marginLeft: 8 }} value={seriesId} onChange={(e) => setSeriesId(e.target.value)} />
          </label>
        </div>
      </section>

      <section style={{ marginTop: 24 }}>
        <h3>Treino (CSV)</h3>
        <form onSubmit={handleTrainCsv}>
          <input type="file" accept=".csv" onChange={(e) => setCsvFile(e.target.files?.[0] || null)} />
          <button type="submit" style={{ marginLeft: 12 }}>Treinar</button>
        </form>
      </section>

      <section style={{ marginTop: 24 }}>
        <h3>Previsão</h3>
        <form onSubmit={handlePredict}>
          <label>
            Horizonte (dias)
            <input type="number" min={1} max={365} style={{ marginLeft: 8 }} value={horizon} onChange={(e) => setHorizon(e.target.value)} />
          </label>
          <button type="submit" style={{ marginLeft: 12 }} disabled={!canPredict}>Prever</button>
        </form>
      </section>

      {statusMsg && (
        <div style={{ marginTop: 16, color: '#444' }}>{statusMsg}</div>
      )}

      {forecast?.length > 0 && (
        <section style={{ marginTop: 24 }}>
          <h3>Resultado</h3>
          {/* Gráfico simples (SVG) para yhat */}
          <SimpleLineChart data={forecast} width={880} height={220} margin={24} />
          <div style={{ overflowX: 'auto' }}>
            <table style={{ borderCollapse: 'collapse', width: '100%' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd', padding: 8 }}>Data</th>
                  <th style={{ textAlign: 'right', borderBottom: '1px solid #ddd', padding: 8 }}>yhat</th>
                  <th style={{ textAlign: 'right', borderBottom: '1px solid #ddd', padding: 8 }}>yhat_lower</th>
                  <th style={{ textAlign: 'right', borderBottom: '1px solid #ddd', padding: 8 }}>yhat_upper</th>
                </tr>
              </thead>
              <tbody>
                {forecast.map((row, idx) => (
                  <tr key={idx}>
                    <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8 }}>{row.ds}</td>
                    <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8, textAlign: 'right' }}>{row.yhat?.toFixed?.(2) ?? row.yhat}</td>
                    <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8, textAlign: 'right' }}>{row.yhat_lower != null ? Number(row.yhat_lower).toFixed(2) : '-'}</td>
                    <td style={{ borderBottom: '1px solid #f0f0f0', padding: 8, textAlign: 'right' }}>{row.yhat_upper != null ? Number(row.yhat_upper).toFixed(2) : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}

function SimpleLineChart({ data, width = 600, height = 200, margin = 20 }) {
  const values = data.map((d) => Number(d.yhat));
  const xs = data.map((d, i) => i);
  const minY = Math.min(...values);
  const maxY = Math.max(...values);
  const rangeY = maxY - minY || 1;
  const innerW = width - margin * 2;
  const innerH = height - margin * 2;

  const points = values.map((v, i) => {
    const x = margin + (i / Math.max(xs.length - 1, 1)) * innerW;
    const y = margin + innerH - ((v - minY) / rangeY) * innerH;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg width={width} height={height} style={{ background: '#fafafa', border: '1px solid #eee', marginBottom: 16 }}>
      <polyline fill="none" stroke="#2563eb" strokeWidth="2" points={points} />
    </svg>
  );
}

export default App;
