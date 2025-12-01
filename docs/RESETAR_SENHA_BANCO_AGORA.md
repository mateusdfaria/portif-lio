# 🔐 Resetar Senha do Banco - Solução Imediata

## ❌ Erro: Password Authentication Failed

```
password authentication failed for user "hospicast_user"
```

A senha do banco de dados no Cloud Run está incorreta.

## ✅ Solução: Resetar Senha e Atualizar Cloud Run

### Comandos Completos (Copiar e Colar)

```bash
# === 1. ESCOLHER NOVA SENHA FORTE ===
NEW_PASSWORD="HospiCast2024!SenhaForte"  # Escolha uma senha forte (mínimo 8 caracteres)

# === 2. RESETAR SENHA NO BANCO ===
echo "🔐 Resetando senha do banco..."
gcloud sql users set-password hospicast_user \
    --instance=hospicast-db \
    --password=$NEW_PASSWORD

echo "✅ Senha resetada"
echo ""

# === 3. OBTER CONNECTION NAME ===
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection Name: $CONNECTION_NAME"
echo ""

# === 4. ATUALIZAR CLOUD RUN ===
echo "🔄 Atualizando Cloud Run..."
DATABASE_URL="postgresql://hospicast_user:${NEW_PASSWORD}@localhost/hospicast?host=/cloudsql/${CONNECTION_NAME}"

gcloud run services update hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --set-env-vars "DATABASE_URL=${DATABASE_URL},API_ALLOWED_ORIGINS=*,LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production" \
    --quiet

echo ""
echo "✅ Senha resetada e Cloud Run atualizado!"
echo "📝 Guarde esta senha em local seguro: $NEW_PASSWORD"
echo ""
echo "⏳ Aguarde 1-2 minutos para o Cloud Run atualizar..."
echo "💡 Depois, tente cadastrar o hospital novamente"
```

---

## 🔍 Verificar se Funcionou

### 1. Aguardar Atualização

Aguarde 1-2 minutos para o Cloud Run atualizar.

### 2. Verificar Logs

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 20
```

**Não deve mais aparecer**: `password authentication failed`

### 3. Testar Cadastro

1. Acesse o frontend
2. Tente cadastrar um hospital novamente
3. Deve funcionar agora!

---

## ⚠️ Importante

1. **Use senha forte**: Mínimo 8 caracteres, com letras, números e símbolos
2. **Guarde a senha**: Você vai precisar dela para futuras atualizações
3. **Atualize o Cloud Run imediatamente** após resetar a senha
4. **Teste após atualizar**: Tente cadastrar um hospital para verificar

---

## 🔐 Gerenciar Senhas

### Ver Usuários do Banco:

```bash
gcloud sql users list --instance=hospicast-db
```

### Resetar Senha (Método Alternativo via Console):

1. Acesse: https://console.cloud.google.com/sql/instances/hospicast-db/users
2. Clique no usuário "hospicast_user"
3. Clique em "Reset Password"
4. Digite a nova senha
5. Atualize o Cloud Run com a nova senha

---

**Execute os comandos acima para resetar a senha e atualizar o Cloud Run!** 🎯

