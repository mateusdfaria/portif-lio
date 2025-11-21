import { useEffect, useState } from 'react';

const initialRegister = {
  display_name: '',
  cnes: '',
  city: '',
  state: '',
  contact_email: '',
  password: '',
};

const initialLogin = {
  identifier: '',
  password: '',
};

export default function HospitalSessionPanel({
  apiBaseUrl,
  session,
  onSessionChange,
  history,
  onHistoryChange,
  setStatusMsg,
  refreshSignal,
}) {
  const [mode, setMode] = useState('landing');
  const [registerForm, setRegisterForm] = useState(initialRegister);
  const [loginForm, setLoginForm] = useState(initialLogin);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (session?.hospital_id && session?.token) {
      fetchHistory();
      setMode('dashboard');
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.hospital_id, session?.token, refreshSignal]);

  const fetchHistory = async () => {
    if (!session?.hospital_id || !session?.token) return;
    try {
      const response = await fetch(
        `${apiBaseUrl}/hospital-access/${session.hospital_id}/forecasts`,
        {
          headers: { 'X-Hospital-Token': session.token },
        },
      );
      if (!response.ok) throw new Error('Não foi possível carregar histórico');
      const data = await response.json();
      onHistoryChange(data.forecasts || []);
    } catch (error) {
      console.error(error);
      setStatusMsg(`❌ ${error.message}`);
    }
  };

  const handleRegister = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${apiBaseUrl}/hospital-access/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registerForm),
      });
      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || 'Falha ao cadastrar hospital');
      }
      const data = await response.json();
      setStatusMsg(`✅ Hospital cadastrado! Guarde o código: ${data.short_code}`);
      setRegisterForm(initialRegister);
      setMode('login');
    } catch (error) {
      setStatusMsg(`❌ ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${apiBaseUrl}/hospital-access/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm),
      });
      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || 'Falha ao autenticar hospital');
      }
      const data = await response.json();
      onSessionChange(data);
      localStorage.setItem('hospicastHospitalSession', JSON.stringify(data));
      setStatusMsg(`✅ Sessão iniciada para ${data.display_name}`);
      setMode('dashboard');
      setLoginForm(initialLogin);
    } catch (error) {
      setStatusMsg(`❌ ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    onSessionChange(null);
    localStorage.removeItem('hospicastHospitalSession');
    onHistoryChange([]);
    setMode('landing');
  };

  const renderLanding = () => (
    <div style={cardStyle}>
      <h2 style={cardTitle}>Hospitais</h2>
      <p style={cardText}>Escolha como deseja prosseguir:</p>
      <div style={{ display: 'flex', gap: '1rem', flexDirection: 'column' }}>
        <button style={primaryButton} onClick={() => setMode('register')}>
          ➕ Cadastrar novo hospital
        </button>
        <button style={secondaryButton} onClick={() => setMode('login')}>
          🔑 Usar hospital existente
        </button>
      </div>
    </div>
  );

  const renderRegister = () => (
    <div style={cardStyle}>
      <h2 style={cardTitle}>Cadastro de Hospital</h2>
      <div style={formGrid}>
        <label style={labelStyle}>
          Nome da instituição
          <input
            style={inputStyle}
            value={registerForm.display_name}
            onChange={(e) => setRegisterForm({ ...registerForm, display_name: e.target.value })}
          />
        </label>
        <label style={labelStyle}>
          CNES (opcional)
          <input
            style={inputStyle}
            value={registerForm.cnes}
            onChange={(e) => setRegisterForm({ ...registerForm, cnes: e.target.value })}
          />
        </label>
        <label style={labelStyle}>
          Cidade
          <input
            style={inputStyle}
            value={registerForm.city}
            onChange={(e) => setRegisterForm({ ...registerForm, city: e.target.value })}
          />
        </label>
        <label style={labelStyle}>
          Estado (UF)
          <input
            style={inputStyle}
            value={registerForm.state}
            onChange={(e) => setRegisterForm({ ...registerForm, state: e.target.value })}
            maxLength={2}
          />
        </label>
        <label style={labelStyle}>
          E-mail de contato
          <input
            style={inputStyle}
            value={registerForm.contact_email}
            onChange={(e) => setRegisterForm({ ...registerForm, contact_email: e.target.value })}
          />
        </label>
        <label style={labelStyle}>
          Senha (mín. 6 caracteres)
          <input
            style={inputStyle}
            type="password"
            value={registerForm.password}
            onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
          />
        </label>
      </div>
      <div style={actionRow}>
        <button style={secondaryButton} onClick={() => setMode('landing')}>
          Voltar
        </button>
        <button style={primaryButton} onClick={handleRegister} disabled={isLoading}>
          {isLoading ? 'Cadastrando...' : 'Salvar cadastro'}
        </button>
      </div>
    </div>
  );

  const renderLogin = () => (
    <div style={cardStyle}>
      <h2 style={cardTitle}>Acessar hospital existente</h2>
      <p style={cardText}>Use o ID ou código fornecido no cadastro.</p>
      <div style={formGrid}>
        <label style={labelStyle}>
          Código ou ID
          <input
            style={inputStyle}
            value={loginForm.identifier}
            onChange={(e) => setLoginForm({ ...loginForm, identifier: e.target.value })}
          />
        </label>
        <label style={labelStyle}>
          Senha
          <input
            style={inputStyle}
            type="password"
            value={loginForm.password}
            onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
          />
        </label>
      </div>
      <div style={actionRow}>
        <button style={secondaryButton} onClick={() => setMode('landing')}>
          Voltar
        </button>
        <button style={primaryButton} onClick={handleLogin} disabled={isLoading}>
          {isLoading ? 'Entrando...' : 'Entrar'}
        </button>
      </div>
    </div>
  );

  const renderDashboard = () => (
    <div style={cardStyle}>
      <h2 style={cardTitle}>Instituição autenticada</h2>
      <p style={cardText}>
        {session.display_name} • Código: <strong>{session.short_code}</strong>
      </p>
      <div style={actionRow}>
        <button style={primaryButton} onClick={fetchHistory}>
          Atualizar histórico
        </button>
        <button style={secondaryButton} onClick={handleLogout}>
          Encerrar sessão
        </button>
      </div>
      <div style={{ marginTop: '1.5rem' }}>
        <h3 style={{ marginBottom: '0.75rem' }}>Previsões recentes</h3>
        {history.length === 0 ? (
          <p style={cardText}>Nenhuma previsão salva ainda.</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {history.map((item) => (
              <li key={item.forecast_id} style={historyItem}>
                <div>
                  <strong>{item.series_id}</strong> • horizonte {item.horizon} dias
                  <div style={{ fontSize: '0.85rem', color: '#64748b' }}>
                    {new Date(item.created_at).toLocaleString('pt-BR')}
                  </div>
                </div>
                <div style={{ fontSize: '0.9rem' }}>
                  Média prevista: {item.average_yhat ? Math.round(item.average_yhat) : '--'}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );

  if (session && mode !== 'dashboard') {
    return renderDashboard();
  }

  if (mode === 'register') return renderRegister();
  if (mode === 'login') return renderLogin();
  if (mode === 'dashboard') return renderDashboard();
  return renderLanding();
}

const cardStyle = {
  background: '#f8fafc',
  borderRadius: '16px',
  padding: '1.5rem',
  boxShadow: '0 10px 25px -5px rgba(15, 23, 42, 0.2)',
  border: '1px solid #e2e8f0',
};

const cardTitle = {
  margin: '0 0 0.5rem 0',
  fontSize: '1.25rem',
  fontWeight: 700,
  color: '#0f172a',
};

const cardText = {
  margin: '0 0 1rem 0',
  color: '#475569',
  fontSize: '0.95rem',
};

const formGrid = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
  gap: '1rem',
  marginBottom: '1.25rem',
};

const labelStyle = {
  display: 'flex',
  flexDirection: 'column',
  fontSize: '0.85rem',
  color: '#475569',
  fontWeight: 600,
  gap: '0.35rem',
};

const inputStyle = {
  borderRadius: '8px',
  border: '1px solid #cbd5f5',
  padding: '0.6rem',
  fontSize: '0.95rem',
  color: '#0f172a',
};

const actionRow = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  gap: '1rem',
  flexWrap: 'wrap',
};

const primaryButton = {
  background: '#2563eb',
  color: '#fff',
  border: 'none',
  borderRadius: '10px',
  padding: '0.75rem 1.5rem',
  fontSize: '0.95rem',
  fontWeight: 600,
  cursor: 'pointer',
  boxShadow: '0 10px 15px -3px rgba(37, 99, 235, 0.4)',
};

const secondaryButton = {
  background: '#e2e8f0',
  color: '#0f172a',
  border: 'none',
  borderRadius: '10px',
  padding: '0.75rem 1.5rem',
  fontSize: '0.95rem',
  fontWeight: 600,
  cursor: 'pointer',
};

const historyItem = {
  padding: '0.75rem',
  borderRadius: '12px',
  border: '1px solid #e2e8f0',
  background: '#fff',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
};

