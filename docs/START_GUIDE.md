# 🚀 Guia de Inicialização - HospiCast

## 📋 Pré-requisitos

### **1. Python 3.8+**
- ✅ Instalado e configurado
- ✅ Pip funcionando

### **2. Node.js 16+**
- ✅ Instalado e configurado
- ✅ NPM funcionando

### **3. Dependências**
- ✅ Backend: `pip install -r backend/requirements.txt`
- ✅ Frontend: `npm install` (no diretório frontend)

## 🎯 Métodos de Inicialização

### **Método 1: Script Python (Recomendado)**
```bash
python start_hospicast_windows.py
```

### **Método 2: Script PowerShell**
```powershell
.\start_hospicast.ps1
```

### **Método 3: Script Batch**
```cmd
start_hospicast.bat
```

### **Método 4: Manual (Terminais Separados)**

#### **Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

#### **Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## 🔧 Solução de Problemas

### **❌ Erro: "npm não encontrado"**
**Solução:**
1. Instale Node.js: https://nodejs.org/
2. Reinicie o terminal
3. Execute `npm --version` para verificar

### **❌ Erro: "python não encontrado"**
**Solução:**
1. Instale Python: https://python.org/
2. Marque "Add Python to PATH" durante instalação
3. Reinicie o terminal

### **❌ Erro: "No module named npm"**
**Solução:**
- Use os scripts corrigidos (`start_hospicast_windows.py`)
- Ou execute manualmente em terminais separados

### **❌ Erro: "Port already in use"**
**Solução:**
1. Feche outros processos usando as portas 8000/3000
2. Ou altere as portas nos scripts

### **❌ Erro: "Dependencies not found"**
**Solução:**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## 🌐 URLs de Acesso

- **Backend API**: http://127.0.0.1:8000
- **Documentação API**: http://127.0.0.1:8000/docs
- **Frontend**: http://localhost:3000

## 📊 Verificação de Funcionamento

### **1. Backend Funcionando**
- ✅ Acesse: http://127.0.0.1:8000
- ✅ Deve mostrar: `{"message": "HospiCast API funcionando!"}`

### **2. Frontend Funcionando**
- ✅ Acesse: http://localhost:3000
- ✅ Deve mostrar a interface do HospiCast

### **3. APIs de Dados Reais**
- ✅ Acesse: http://127.0.0.1:8000/real-data/data-sources/status
- ✅ Deve mostrar status das APIs externas

## 🎯 Próximos Passos

1. **Configure APIs Externas** (opcional):
   - Crie `backend/.env` com chave da OpenWeatherMap
   - Veja `REAL_DATA_INTEGRATION.md` para detalhes

2. **Explore o Sistema**:
   - Dashboard com dados reais
   - Previsões com Prophet
   - Alertas hospitalares
   - Métricas avançadas

3. **Teste as Funcionalidades**:
   - Selecione um hospital
   - Veja KPIs em tempo real
   - Analise previsões
   - Configure alertas

## 🆘 Suporte

### **Logs de Erro**
- Backend: Console do terminal
- Frontend: Console do navegador (F12)

### **Arquivos de Configuração**
- `backend/env.example` - Variáveis de ambiente
- `REAL_DATA_INTEGRATION.md` - Integração com APIs
- `INTEGRATION_SUMMARY.md` - Resumo completo

### **Scripts de Teste**
```bash
# Testar APIs de dados reais
python test_real_apis.py

# Testar Docker (se configurado)
docker-compose up --build
```

---

**🎉 HospiCast está pronto para uso!**
