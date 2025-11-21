# 🔧 Solução: Erro `np.float_` foi removido no NumPy 2.0

## 🔍 Problema

O router de forecast não está sendo carregado porque:

```
❌ Erro ao carregar router de forecast: `np.float_` was removed in the NumPy 2.0 release. Use `np.float64` instead.
```

## 🎯 Causa

O **Prophet 1.1.5** não é compatível com **NumPy 2.0**. O Prophet usa `np.float_` internamente, que foi removido no NumPy 2.0.

## ✅ Solução

Fixar a versão do NumPy para < 2.0.0 no `requirements.txt`:

```txt
numpy>=1.26.4,<2.0.0
```

## 📋 Passos

### 1. Atualizar requirements.txt

O arquivo já foi atualizado para:
```txt
numpy>=1.26.4,<2.0.0
```

### 2. Fazer Redeploy no Railway

1. No Railway, vá em **Settings** → **Deploy**
2. Clique em **"Redeploy"**
3. Selecione **"Clear build cache"**
4. Aguarde o deploy terminar

### 3. Verificar Logs

Após o redeploy, verifique os logs. Deve aparecer:

```
✅ Router de forecast carregado com sucesso
```

### 4. Testar Rota

Após o redeploy, acesse:
```
https://web-production-039db.up.railway.app/docs
```

Procure por:
- **POST** `/forecast/train-file` na lista de rotas

## 🔄 Alternativa: Atualizar Prophet

Se quiser usar NumPy 2.0, você precisaria atualizar o Prophet para uma versão mais recente que seja compatível. No entanto, a versão mais recente do Prophet pode ter outras incompatibilidades.

**Recomendação**: Manter NumPy < 2.0.0 por enquanto, pois é a solução mais estável.

## 📝 Nota

O Prophet está em manutenção e pode não ter suporte completo para NumPy 2.0 ainda. A fixação da versão do NumPy é a solução mais segura.

---

*Última atualização: Janeiro 2025*

