# 🔧 Correção: Erro de Build - scikit-learn no Railway

## ❌ Erro

```
ERROR: Failed to build scikit-learn
FileNotFoundError: [Errno 2] No such file or directory: 'cc'
```

## ✅ Solução

O Railway está usando Python 3.13, que é muito novo e não tem wheels pré-compilados para scikit-learn 1.4.1. A solução é forçar Python 3.11.

### Opção 1: Especificar Python 3.11 (Recomendado)

Já atualizei o `backend/runtime.txt` para:
```
python-3.11.0
```

Isso força o Railway a usar Python 3.11, que tem wheels para todas as bibliotecas.

### Opção 2: Atualizar scikit-learn (Já Feito)

Atualizei `requirements.txt` para:
```txt
scikit-learn>=1.4.1
```

Isso permite que pip escolha uma versão mais recente com wheels.

### Opção 3: Configurar no Railway Dashboard

Se ainda não funcionar, configure no Railway:

1. **Settings** → **Variables**
2. Adicione:
   ```
   PYTHON_VERSION=3.11
   ```

3. **Settings** → **Deploy**
4. No **Pre-deploy Command**, adicione:
   ```
   python --version && pip install --upgrade pip setuptools wheel && pip install -r backend/requirements.txt
   ```

## 🚀 Configuração Final no Railway

### Pre-deploy Command:
```
pip install --upgrade pip setuptools wheel && pip install -r backend/requirements.txt
```

### Custom Start Command:
```
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Variables (Opcional):
```
PYTHON_VERSION=3.11
```

## 🔍 Verificação

Após configurar, você deve ver nos logs:

```
Python 3.11.x
Collecting scikit-learn...
Using cached scikit-learn-1.4.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
Installing collected packages...
Successfully installed scikit-learn...
```

**Importante**: Se você ver "Using cached" ou "Downloading ... .whl", está funcionando!

## 📝 Checklist

- [ ] `runtime.txt` especifica Python 3.11 (já feito)
- [ ] `requirements.txt` usa `scikit-learn>=1.4.1` (já feito)
- [ ] Pre-deploy Command atualizado
- [ ] Logs mostram Python 3.11.x
- [ ] Logs mostram "Using cached" para scikit-learn
- [ ] Deploy completa com sucesso

## 💡 Por que Python 3.11?

- Python 3.11 tem wheels pré-compilados para todas as bibliotecas
- Python 3.13 é muito novo e muitas bibliotecas ainda não têm wheels
- Python 3.11 é estável e amplamente suportado

---

*Última atualização: Janeiro 2025*

