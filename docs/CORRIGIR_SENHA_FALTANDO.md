# 🔐 Corrigir Erro: No Password Supplied

## ❌ Erro: "no password supplied"

O erro indica que a `DATABASE_URL` no Cloud Run não contém a senha ou está incorreta.

## ✅ Solução: Atualizar DATABASE_URL com Senha

### Passo 1: Resetar Senha do Banco (Se Necessário)

```bash
# Escolher nova senha forte
NEW_PASSWORD="HospiCast2024!SenhaForte"  # Escolha uma senha forte

# Resetar senha
gcloud sql users set-password hospicast_user \
    --instance=hospicast-db \
    --password=$NEW_PASSWORD

echo "✅ Senha resetada"
```

### Passo 2: Obter Connection Name

```bash
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection Name: $CONNECTION_NAME"
```

### Passo 3: Montar DATABASE_URL Correta

```bash
# Use a senha que você acabou de definir
DB_PASSWORD="HospiCast2024!SenhaForte"  # Use a mesma senha do passo 1
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")

# Montar URL completa
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

echo "DATABASE_URL=$DATABASE_URL"
```

### Passo 4: Atualizar Cloud Run

```bash
# Atualizar Cloud Run com DATABASE_URL completa
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "DATABASE_URL=${DATABASE_URL},API_ALLOWED_ORIGINS=*,LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production" \
    --quiet

echo "✅ Cloud Run atualizado"
```

---

## 📋 Comandos Completos (Copiar e Colar)

```bash
# === 1. RESETAR SENHA ===
NEW_PASSWORD="HospiCast2024!SenhaForte"  # Escolha uma senha forte

echo "🔐 Resetando senha do banco..."
gcloud sql users set-password hospicast_user \
    --instance=hospicast-db \
    --password=$NEW_PASSWORD

echo "✅ Senha resetada"
echo ""

# === 2. OBTER CONNECTION NAME ===
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection Name: $CONNECTION_NAME"
echo ""

# === 3. MONTAR DATABASE_URL ===
DB_PASSWORD="$NEW_PASSWORD"  # Usar a mesma senha
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

echo "DATABASE_URL gerada:"
echo "$DATABASE_URL"
echo ""

# === 4. ATUALIZAR CLOUD RUN ===
echo "🔄 Atualizando Cloud Run..."
gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "DATABASE_URL=${DATABASE_URL},API_ALLOWED_ORIGINS=*,LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production" \
    --quiet

echo ""
echo "✅ Senha configurada e Cloud Run atualizado!"
echo "📝 Guarde esta senha: $NEW_PASSWORD"
echo ""
echo "⏳ Aguarde 1-2 minutos para o Cloud Run atualizar..."
echo "💡 Depois, tente cadastrar o hospital novamente"
```

---

## 🔍 Verificar se Funcionou

### 1. Verificar DATABASE_URL no Cloud Run

```bash
# Ver variável de ambiente
gcloud run services describe hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DATABASE_URL')].value)"
```

**Deve conter**: `postgresql://hospicast_user:SENHA@localhost/hospicast?host=/cloudsql/...`

### 2. Verificar Logs

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 20
```

**Não deve mais aparecer**: `no password supplied`

### 3. Testar Cadastro

1. Acesse o frontend
2. Tente cadastrar um hospital
3. Deve funcionar agora!

---

## ⚠️ Formato Correto da DATABASE_URL

A URL deve ter este formato:

```
postgresql://USUARIO:SENHA@localhost/DATABASE?host=/cloudsql/CONNECTION_NAME
```

**Exemplo**:
```
postgresql://hospicast_user:MinhaSenha123!@localhost/hospicast?host=/cloudsql/hospicast-prod:southamerica-east1:hospicast-db
```

**Importante**:
- ✅ Senha deve estar entre `:` e `@`
- ✅ Senha não deve ter caracteres especiais que quebrem a URL (use URL encoding se necessário)
- ✅ Connection name deve estar completo

---

## 🔐 Se a Senha Tiver Caracteres Especiais

Se sua senha tiver caracteres especiais que podem quebrar a URL, use URL encoding:

```bash
# Exemplo: senha "Senha@123!"
# @ vira %40
# ! vira %21

DB_PASSWORD_RAW="Senha@123!"
DB_PASSWORD_ENCODED=$(echo -n "$DB_PASSWORD_RAW" | jq -sRr @uri)
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD_ENCODED}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"
```

Ou use uma senha sem caracteres especiais problemáticos.

---

## ✅ Checklist

- [ ] Senha resetada no banco
- [ ] Connection name obtido
- [ ] DATABASE_URL montada corretamente (com senha)
- [ ] Cloud Run atualizado
- [ ] Aguardou 1-2 minutos
- [ ] Testou cadastrar hospital
- [ ] Funcionou!

---

**Execute os comandos acima para corrigir a senha faltando!** 🎯

