# 🔧 Correção: requirements.txt not found no Railway

## ❌ Erro

```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

## ✅ Solução

O problema é que o Railway está procurando `requirements.txt` no lugar errado. O arquivo está em `backend/requirements.txt`.

### Configuração Correta no Railway Dashboard

1. **Acesse**: https://railway.app
2. **Seu projeto** → **Clique no serviço**
3. **Settings** → **Deploy**

Configure:

**Root Directory:**
```
backend
```

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Por que isso funciona?

Quando você define **Root Directory** como `backend`, o Railway já está dentro do diretório backend, então:
- `requirements.txt` → encontra `backend/requirements.txt`
- `main:app` → encontra `backend/main.py`

### Alternativa (sem Root Directory)

Se não quiser usar Root Directory, configure:

**Root Directory:**
```
(em branco ou .)
```

**Build Command:**
```
pip install -r backend/requirements.txt
```

**Start Command:**
```
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

## 📝 Configuração Recomendada

### Opção 1: Com Root Directory (Recomendado)

**Root Directory:** `backend`
**Build Command:** `pip install -r requirements.txt`
**Start Command:** `python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT`

### Opção 2: Sem Root Directory

**Root Directory:** (vazio)
**Build Command:** `pip install -r backend/requirements.txt`
**Start Command:** `python3 -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

## 🔍 Verificação

Após configurar, verifique os logs:

1. **View Logs** no Railway
2. Você deve ver:
   ```
   Collecting fastapi...
   Collecting uvicorn...
   Installing collected packages...
   Successfully installed...
   INFO:     Started server process
   INFO:     Uvicorn running on http://0.0.0.0:PORT
   ```

## ✅ Checklist

- [ ] Root Directory configurado corretamente
- [ ] Build Command aponta para o arquivo correto
- [ ] Start Command usa o caminho correto do módulo
- [ ] Logs mostram "Installing collected packages"
- [ ] Logs mostram "Uvicorn running"

---

*Última atualização: Janeiro 2025*

