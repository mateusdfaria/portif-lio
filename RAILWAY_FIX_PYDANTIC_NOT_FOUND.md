# 🔧 Correção: pydantic not found no Railway

## ❌ Erro

```
ModuleNotFoundError: No module named 'pydantic'
```

## ✅ Solução

O problema é que as dependências instaladas no Pre-deploy Command não estão disponíveis quando o Start Command roda. O Railway pode usar ambientes Python diferentes.

### Solução: Instalar Dependências no Start Command

Atualizei o `backend/start.sh` para:
- Verificar se pydantic está instalado
- Instalar todas as dependências se necessário
- Garantir que usa o mesmo Python

### Configuração no Railway Dashboard

**Pre-deploy Command:**
```
pip install --upgrade pip setuptools wheel && pip install -r backend/requirements.txt
```

**Custom Start Command:**
```
bash backend/start.sh
```

O script agora:
1. Detecta o Python correto
2. Verifica se pydantic está instalado
3. Instala dependências se necessário
4. Inicia o servidor

## 🚀 Alternativa Simples

Se o script não funcionar, use este comando direto:

**Custom Start Command:**
```
cd backend && pip install -r requirements.txt && python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

Isso garante que as dependências sejam instaladas antes de iniciar.

## 🔍 Verificação

Após configurar, você deve ver nos logs:

```
Iniciando HospiCast Backend...
Usando Python: /usr/bin/python3
Python 3.13.9
Instalando dependências...
Collecting pydantic...
Successfully installed pydantic...
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8080
```

## 💡 Por que isso acontece?

O Railway pode usar diferentes instâncias do Python:
- Pre-deploy pode instalar em `/usr/lib/python3.13/site-packages`
- Start Command pode usar `/mise/installs/python/3.13.9/lib/python3.13/site-packages`

O script `start.sh` garante que instala no mesmo Python que vai usar para rodar.

## 📝 Checklist

- [ ] Pre-deploy Command instala requirements.txt
- [ ] Start Command usa `bash backend/start.sh` ou instala dependências
- [ ] Logs mostram "Successfully installed pydantic"
- [ ] Logs mostram "Uvicorn running"
- [ ] Backend responde em `/`

---

*Última atualização: Janeiro 2025*

