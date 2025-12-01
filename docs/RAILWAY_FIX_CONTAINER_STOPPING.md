# 🔧 Correção: Container Parando no Railway

## ❌ Problema

O container inicia, mas para imediatamente após instalar dependências.

## ✅ Solução

O Railway pode estar executando o Pre-deploy Command mesmo com Dockerfile. Configure corretamente:

### Configuração no Railway Dashboard

1. **Settings** → **Deploy**
2. **Remova completamente**:
   - Pre-deploy Command: (deixe completamente vazio)
   - Custom Start Command: (deixe completamente vazio)
3. **Salve**

O Railway deve usar apenas o `Dockerfile` agora.

### Verificar se está usando Dockerfile

Nos logs, você deve ver:
```
Step 1/10 : FROM python:3.11-slim
Step 2/10 : WORKDIR /app
...
```

Se não ver "Step", o Railway não está usando o Dockerfile.

### Forçar uso do Dockerfile

Se o Railway não detectar automaticamente:

1. **Settings** → **Service**
2. Procure **"Docker"** ou **"Container"** 
3. Ative se houver opção
4. Ou configure **Buildpack** como **"Docker"**

## 🔍 Verificação dos Logs

Após configurar corretamente, você deve ver:

```
Step 1/10 : FROM python:3.11-slim
Step 2/10 : WORKDIR /app
Step 3/10 : RUN apt-get update...
Step 4/10 : COPY backend/requirements.txt...
Step 5/10 : RUN pip install...
Successfully installed...
Step 6/10 : COPY backend/ /app/
Step 7/10 : CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Importante**: O container deve continuar rodando, não parar!

## 🐛 Se o Container Continuar Parando

### Verificar Health Check

O Railway pode estar matando o container se o health check falhar. Verifique:

1. **Settings** → **Service**
2. Procure **Health Check** ou **Healthcheck**
3. Configure para: `/` (rota raiz)
4. Timeout: `30s`

### Verificar Porta

O Railway pode estar usando uma porta diferente. O Dockerfile já está configurado para usar `$PORT` automaticamente.

## 📝 Checklist

- [ ] Pre-deploy Command está vazio
- [ ] Custom Start Command está vazio
- [ ] Logs mostram "Step" (usando Dockerfile)
- [ ] Logs mostram Python 3.11.x
- [ ] Logs mostram "Uvicorn running"
- [ ] Container não para (fica rodando)

---

*Última atualização: Janeiro 2025*

