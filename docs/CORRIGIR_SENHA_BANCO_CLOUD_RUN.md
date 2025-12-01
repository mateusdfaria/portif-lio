# 🔐 Corrigir Senha do Banco no Cloud Run

## ❌ Erro: Password Authentication Failed

O erro indica que a senha do usuário `hospicast_user` no Cloud Run está incorreta.

## ✅ Solução: Resetar Senha e Atualizar Cloud Run

### Opção 1: Resetar Senha e Atualizar (Recomendado)

```bash
# === 1. RESETAR SENHA DO BANCO ===
# Escolha uma senha forte
NEW_PASSWORD="SuaNovaSenhaForte123!"

# Resetar senha do usuário
gcloud sql users set-password hospicast_user \
    --instance=hospicast-db \
    --password=$NEW_PASSWORD

echo "✅ Senha resetada"

# === 2. OBTER CONNECTION NAME ===
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection Name: $CONNECTION_NAME"

# === 3. ATUALIZAR DATABASE_URL NO CLOUD RUN ===
DATABASE_URL="postgresql://hospicast_user:${NEW_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "DATABASE_URL=${DATABASE_URL}" \
    --quiet

echo "✅ Cloud Run atualizado com nova senha"
```

### Opção 2: Usar Senha Existente (Se Você Sabe Qual É)

```bash
# === 1. OBTER CONNECTION NAME ===
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection Name: $CONNECTION_NAME"

# === 2. DEFINIR SENHA (use a senha que você sabe) ===
DB_PASSWORD="mateus22"  # Use a senha correta aqui

# === 3. ATUALIZAR DATABASE_URL NO CLOUD RUN ===
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "DATABASE_URL=${DATABASE_URL}" \
    --quiet

echo "✅ Cloud Run atualizado"
```

---

## 📋 Comandos Completos (Copiar e Colar)

### Resetar Senha e Atualizar:

```bash
# === CONFIGURAÇÃO ===
NEW_PASSWORD="SuaNovaSenhaForte123!"  # Escolha uma senha forte
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")

# === RESETAR SENHA ===
echo "🔐 Resetando senha do banco..."
gcloud sql users set-password hospicast_user \
    --instance=hospicast-db \
    --password=$NEW_PASSWORD

# === ATUALIZAR CLOUD RUN ===
echo "🔄 Atualizando Cloud Run..."
DATABASE_URL="postgresql://hospicast_user:${NEW_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "DATABASE_URL=${DATABASE_URL}" \
    --quiet

echo ""
echo "✅ Senha resetada e Cloud Run atualizado!"
echo "📝 Guarde esta senha: $NEW_PASSWORD"
```

### Usar Senha Existente:

```bash
# === CONFIGURAÇÃO ===
DB_PASSWORD="mateus22"  # Use a senha correta
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")

# === ATUALIZAR CLOUD RUN ===
echo "🔄 Atualizando Cloud Run..."
DATABASE_URL="postgresql://hospicast_user:${DB_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "DATABASE_URL=${DATABASE_URL}" \
    --quiet

echo "✅ Cloud Run atualizado!"
```

---

## 🔍 Verificar se Funcionou

### 1. Verificar Logs do Cloud Run

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 20
```

**Não deve mais aparecer**: `password authentication failed`

### 2. Testar Cadastro de Hospital

1. Acesse o frontend
2. Tente cadastrar um hospital novamente
3. Deve funcionar agora!

---

## 🔐 Gerenciar Senhas do Banco

### Ver Usuários do Banco:

```bash
gcloud sql users list --instance=hospicast-db
```

### Resetar Senha (Método Alternativo):

```bash
# Via Console Web:
# 1. Acesse: https://console.cloud.google.com/sql/instances/hospicast-db/users
# 2. Clique no usuário "hospicast_user"
# 3. Clique em "Reset Password"
# 4. Digite a nova senha
# 5. Atualize o Cloud Run com a nova senha
```

---

## ⚠️ Importante

1. **Guarde a senha em local seguro** - você vai precisar dela para atualizar o Cloud Run
2. **Use senha forte** - mínimo 8 caracteres, com letras, números e símbolos
3. **Atualize o Cloud Run imediatamente** após resetar a senha
4. **Teste após atualizar** - tente cadastrar um hospital para verificar

---

**Execute os comandos acima para corrigir a senha do banco!** 🎯

