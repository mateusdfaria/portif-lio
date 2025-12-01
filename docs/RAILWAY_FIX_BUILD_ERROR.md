# 🔧 Correção: Erro de Build - pandas/numpy no Railway

## ❌ Erro

```
ERROR: Failed to build 'pandas' when installing build dependencies
ERROR: Unknown compiler(s): [['cc'], ['gcc'], ['clang']]
```

## ✅ Solução

O Railway está tentando compilar pandas/numpy do código-fonte, mas não tem compiladores C. A solução é usar versões com wheels pré-compilados.

### Opção 1: Atualizar requirements.txt (Já Feito)

Atualizei o `requirements.txt` para usar versões mais flexíveis que pegam wheels pré-compilados:

```txt
pandas>=2.2.1
numpy>=1.26.4
```

Isso permite que o pip escolha a versão mais recente com wheels disponíveis.

### Opção 2: Instalar Dependências de Build (No Railway)

No Railway Dashboard, altere o **Pre-deploy Command** para:

```
pip install --upgrade pip setuptools wheel && pip install -r backend/requirements.txt
```

Isso garante que pip, setuptools e wheel estão atualizados antes de instalar.

### Opção 3: Usar Versões Específicas com Wheels

Se ainda não funcionar, use versões específicas que têm wheels:

```txt
pandas==2.2.2
numpy==1.26.4
```

## 🚀 Configuração Recomendada no Railway

### Pre-deploy Command:
```
pip install --upgrade pip setuptools wheel && pip install -r backend/requirements.txt
```

### Custom Start Command:
```
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 🔍 Verificação

Após configurar, você deve ver nos logs:

```
Collecting pandas...
Using cached pandas-2.2.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
Collecting numpy...
Using cached numpy-1.26.4-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
Installing collected packages...
Successfully installed pandas numpy...
```

**Importante**: Se você ver "Using cached" ou "Downloading ... .whl", está funcionando! Se ver "Building wheel" ou "Compiling", ainda vai dar erro.

## 📝 Checklist

- [ ] requirements.txt atualizado (já feito)
- [ ] Pre-deploy Command inclui `--upgrade pip setuptools wheel`
- [ ] Logs mostram "Using cached" ou "Downloading ... .whl"
- [ ] Não aparece "Building wheel" ou "Compiling"
- [ ] Deploy completa com sucesso

---

*Última atualização: Janeiro 2025*

