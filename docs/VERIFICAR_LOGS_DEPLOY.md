# 🔍 Verificar Logs Após Deploy

## ❌ Container ainda não inicia

Preciso ver os logs para identificar o problema.

## 📋 Execute este comando:

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100
```

**Me envie os logs completos**, especialmente:
- As últimas linhas com erros
- Se ainda aparece `error parsing env var "api_allowed_origins"`
- Qualquer outro erro ou traceback

## 🔍 O que procurar nos logs:

### ✅ SUCESSO - Erro resolvido:
- Não aparece mais `error parsing env var "api_allowed_origins"`
- Aparece "Application startup complete" ou similar
- O servidor inicia corretamente

### ❌ AINDA COM ERRO:
- Ainda aparece `error parsing env var "api_allowed_origins"` = precisa verificar se o rebuild incluiu a correção
- Outro erro diferente = preciso ver o erro completo

### ⚠️ OUTROS PROBLEMAS POSSÍVEIS:
- Erro de conexão com banco de dados
- Erro de importação de módulos
- Erro de porta
- Timeout muito curto

---

**Execute o comando de logs e me envie o resultado completo!**



