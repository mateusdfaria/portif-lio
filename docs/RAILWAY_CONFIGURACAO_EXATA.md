# ✅ Configuração Exata para Railway Dashboard

## 📸 Baseado na Tela que Você Mostrou

Vejo que você está na tela de configuração do Railway. Configure exatamente assim:

### 1. Pre-deploy Command

**Altere de:**
```
pip install -r requirements.txt
```

**Para:**
```
pip install -r backend/requirements.txt
```

**OU** (se preferir):
```
cd backend && pip install -r requirements.txt
```

### 2. Custom Start Command

**Altere de:**
```
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Para:**
```
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 🎯 Configuração Final Completa

### Pre-deploy Command:
```
pip install -r backend/requirements.txt
```

### Custom Start Command:
```
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 📝 Passos

1. **Cole os comandos acima** nos campos corretos
2. **Clique em Save** (ou equivalente)
3. **Aguarde o redeploy automático** ou clique em **Redeploy**
4. **Verifique os logs** para confirmar que funcionou

## 🔍 O que Deve Aparecer nos Logs

Após configurar corretamente, você deve ver:

```
Collecting fastapi...
Collecting uvicorn...
Installing collected packages...
Successfully installed fastapi uvicorn...
🚀 Iniciando HospiCast Backend...
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:PORT
```

## ✅ Por que essas mudanças?

1. **Pre-deploy**: Precisa do caminho completo `backend/requirements.txt` porque está executando da raiz
2. **Start Command**: Usa `python3 -m uvicorn` para garantir que o Python encontre o módulo instalado

---

*Última atualização: Janeiro 2025*

