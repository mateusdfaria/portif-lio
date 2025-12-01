# 🔧 Correção: pydantic incompatível com Python 3.13

## ❌ Erro

```
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
```

## ✅ Solução

O problema é que `pydantic 1.10.14` não é compatível com Python 3.13. A melhor solução é **forçar Python 3.11** que é mais estável.

### Solução: Forçar Python 3.11

Já atualizei o `backend/runtime.txt` para:
```
python-3.11.0
```

Mas o Railway pode estar ignorando. Configure no Railway Dashboard:

### Configuração no Railway Dashboard

1. **Settings** → **Variables**
2. Adicione:
   ```
   PYTHON_VERSION=3.11
   ```

3. **Settings** → **Deploy**
4. No **Pre-deploy Command**, adicione verificação:
   ```
   python --version && pip install --upgrade pip setuptools wheel && pip install -r backend/requirements.txt
   ```

### Alternativa: Usar Nixpacks Explicitamente

O arquivo `nixpacks.toml` já está configurado para Python 3.11. O Railway deve detectar automaticamente.

## 🚀 Configuração Recomendada

### Variables:
```
PYTHON_VERSION=3.11
```

### Pre-deploy Command:
```
pip install --upgrade pip setuptools wheel && pip install -r backend/requirements.txt
```

### Custom Start Command:
```
cd backend && pip install -r requirements.txt && python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 🔍 Verificação

Após configurar, você deve ver nos logs:

```
Python 3.11.x
Collecting pydantic==1.10.14...
Successfully installed pydantic...
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8080
```

**Importante**: Verifique que os logs mostram **Python 3.11.x**, não 3.13!

## 💡 Por que Python 3.11?

- Python 3.11 tem wheels para todas as bibliotecas
- pydantic 1.10.14 é totalmente compatível
- Python 3.13 é muito novo e tem problemas de compatibilidade
- Python 3.11 é estável e amplamente testado

## 📝 Checklist

- [ ] Variável `PYTHON_VERSION=3.11` configurada no Railway
- [ ] `runtime.txt` especifica Python 3.11 (já feito)
- [ ] Logs mostram Python 3.11.x (não 3.13!)
- [ ] Logs mostram "Successfully installed pydantic"
- [ ] Logs mostram "Uvicorn running"
- [ ] Backend responde em `/`

---

*Última atualização: Janeiro 2025*

