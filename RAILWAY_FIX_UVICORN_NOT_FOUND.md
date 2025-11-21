# 🔧 Correção: uvicorn not found no Railway

## ❌ Erro

```
No module named uvicorn
```

## ✅ Solução

O problema é que o Start Command está usando um Python diferente do que instalou os pacotes. Vamos garantir que use o mesmo Python.

### Opção 1: Usar Script de Inicialização (Recomendado)

Já atualizei o `backend/start.sh` para:
- Verificar se uvicorn está instalado
- Instalar se necessário
- Usar `python3` explicitamente

**No Railway Dashboard, configure:**

**Custom Start Command:**
```
bash backend/start.sh
```

### Opção 2: Instalar no Pre-deploy e Usar Python3 no Start

**Pre-deploy Command:**
```
pip install --upgrade pip setuptools wheel && pip install -r backend/requirements.txt
```

**Custom Start Command:**
```
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Opção 3: Instalar Uvicorn Explicitamente no Pre-deploy

**Pre-deploy Command:**
```
pip install --upgrade pip setuptools wheel && pip install -r backend/requirements.txt && pip install uvicorn[standard]
```

**Custom Start Command:**
```
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 🚀 Configuração Recomendada no Railway

### Pre-deploy Command:
```
pip install --upgrade pip setuptools wheel && pip install -r backend/requirements.txt
```

### Custom Start Command:
```
bash backend/start.sh
```

**OU** (alternativa simples):
```
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 🔍 Verificação

Após configurar, você deve ver nos logs:

```
Iniciando HospiCast Backend...
Python 3.13.x
Iniciando servidor na porta 8000...
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 💡 Por que isso acontece?

O Railway pode usar diferentes instâncias do Python:
- Pre-deploy pode usar `/usr/bin/python3`
- Start Command pode usar `/mise/installs/python/3.13.9/bin/python3`

O script `start.sh` garante que usa o mesmo Python e instala uvicorn se necessário.

## 📝 Checklist

- [ ] Pre-deploy Command instala requirements.txt
- [ ] Start Command usa `python3` (não apenas `python`)
- [ ] Start Command usa `python3 -m uvicorn` (não apenas `uvicorn`)
- [ ] Logs mostram "Uvicorn running"
- [ ] Backend responde em `/`

---

*Última atualização: Janeiro 2025*

