# 🔧 Solução: Erro 'Prophet' object has no attribute 'stan_backend'

## 🔍 Problema

O erro ocorre porque o Prophet precisa do **CmdStan** instalado:

```
'Prophet' object has no attribute 'stan_backend'
```

## 🎯 Causa

O Prophet 1.1.5 requer:
1. **cmdstanpy** (interface Python para CmdStan)
2. **CmdStan** (compilador Stan, instalado separadamente)

## ✅ Solução Aplicada

### 1. Adicionado `cmdstanpy` ao requirements.txt

```txt
cmdstanpy>=1.1.0
```

### 2. Atualizado Dockerfile

O Dockerfile agora instala o CmdStan durante o build:

```dockerfile
# Install CmdStan (required by Prophet)
RUN python -c "import cmdstanpy; cmdstanpy.install_cmdstan(version=None, verbose=False)" || echo "CmdStan installation skipped (may already be installed)"
```

### 3. Adicionada verificação no main.py

O `main.py` agora verifica/instala o CmdStan na inicialização:

```python
try:
    import cmdstanpy
    cmdstanpy.install_cmdstan(version=None, verbose=False)
    print("✅ CmdStan verificado/instalado com sucesso")
except Exception as e:
    print(f"⚠️  Aviso ao verificar CmdStan: {e}")
```

## 📋 Próximos Passos

### 1. Fazer Redeploy no Railway

1. No Railway, vá em **Settings** → **Deploy**
2. Clique em **"Redeploy"**
3. Selecione **"Clear build cache"**
4. Aguarde o deploy terminar (pode demorar mais, pois o CmdStan é grande)

### 2. Verificar Logs

Após o deploy, verifique os logs. Deve aparecer:

```
✅ CmdStan verificado/instalado com sucesso
✅ Router de forecast carregado com sucesso
```

### 3. Testar Treinamento

Após o deploy, teste o treinamento novamente. Deve funcionar!

## ⚠️ Nota Importante

- O CmdStan é grande (~200MB) e pode demorar para instalar
- O build pode levar mais tempo na primeira vez
- Se o build falhar por timeout, tente novamente

## 🔄 Alternativa: Instalação Manual

Se o build automático falhar, você pode instalar manualmente no Railway:

1. Acesse o terminal do Railway
2. Execute:
```bash
python -c "import cmdstanpy; cmdstanpy.install_cmdstan()"
```

---

*Última atualização: Janeiro 2025*

