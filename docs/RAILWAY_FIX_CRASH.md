# 🔧 Correção: Railway Crash - uvicorn not found

## ❌ Erro

```
/bin/bash: line 1: uvicorn: command not found
```

## ✅ Solução

O problema é que o Railway não está encontrando o `uvicorn`. Use `python -m uvicorn` em vez de apenas `uvicorn`.

### Opção 1: Configurar no Railway Dashboard (Mais Rápido)

1. **Acesse seu projeto no Railway**
2. **Clique no serviço** que está dando erro
3. Vá em **Settings**
4. Em **Start Command**, altere para:
   ```
   cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. **Salve** e aguarde o redeploy

### Opção 2: Usar Arquivos de Configuração (Já Corrigido)

Os arquivos `Procfile` e `railway.json` já foram corrigidos para usar `python -m uvicorn`.

**Se ainda não funcionar, verifique:**

1. **Build Command** no Railway:
   ```
   cd backend && pip install -r requirements.txt
   ```

2. **Start Command** no Railway:
   ```
   cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Root Directory**:
   ```
   backend
   ```

### Opção 3: Verificar Python Version

O Railway pode estar usando uma versão diferente do Python. Adicione `runtime.txt`:

1. Crie arquivo `backend/runtime.txt`:
   ```
   python-3.11
   ```

2. Faça commit e push:
   ```bash
   git add backend/runtime.txt
   git commit -m "fix: Especifica versão do Python"
   git push origin main
   ```

3. O Railway vai redeployar automaticamente

## 🔍 Verificação

Após corrigir, verifique os logs:

1. No Railway, clique em **View Logs**
2. Você deve ver:
   ```
   Installing dependencies...
   Starting application...
   INFO:     Started server process
   INFO:     Uvicorn running on http://0.0.0.0:PORT
   ```

## 📝 Checklist

- [ ] Start Command usa `python -m uvicorn` (não apenas `uvicorn`)
- [ ] Build Command instala requirements: `pip install -r requirements.txt`
- [ ] Root Directory está como `backend`
- [ ] Arquivo `runtime.txt` especifica Python 3.11
- [ ] Logs mostram "Uvicorn running"

## 🚀 Comandos Corretos

**Build Command:**
```bash
cd backend && pip install -r requirements.txt
```

**Start Command:**
```bash
cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

**OU** (se estiver na raiz):
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

---

*Última atualização: Janeiro 2025*

