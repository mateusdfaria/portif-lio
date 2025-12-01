# 🔐 Resolver Erro de Senha Incorreta

## ❌ Erro: "password authentication failed for user 'hospicast_user'"

A senha na `DATABASE_URL` está incorreta ou o usuário não foi criado corretamente.

## ✅ Solução: Resetar Senha do Usuário

### Opção 1: Resetar Senha via gcloud

```bash
# Resetar senha do usuário hospicast_user
gcloud sql users set-password hospicast_user \
    --instance=hospicast-db \
    --password=NOVA_SENHA_FORTE_AQUI
```

**Importante:** Escolha uma senha forte e guarde em local seguro!

### Opção 2: Resetar via Console Web

1. Acesse: https://console.cloud.google.com/sql/instances/hospicast-db/users
2. Clique no usuário `hospicast_user`
3. Clique em **"Reset password"** (Redefinir senha)
4. Digite uma nova senha forte
5. Clique em **"Update"** (Atualizar)

### Opção 3: Verificar se o Usuário Existe

```bash
# Listar usuários do banco
gcloud sql users list --instance=hospicast-db
```

Se o usuário `hospicast_user` não existir, crie:

```bash
# Criar usuário
gcloud sql users create hospicast_user \
    --instance=hospicast-db \
    --password=SENHA_FORTE_AQUI
```

## 🚀 Passos Completos

### 1. Resetar Senha

```bash
# No Cloud Shell ou terminal com gcloud
gcloud sql users set-password hospicast_user \
    --instance=hospicast-db \
    --password=MinhaSenhaForte123!
```

### 2. Atualizar DATABASE_URL

No Git Bash, configure com a nova senha:

```bash
# Atualizar DATABASE_URL com a senha correta
export DATABASE_URL="postgresql://hospicast_user:MinhaSenhaForte123!@34.39.151.125:5432/hospicast"

# Verificar
echo $DATABASE_URL
```

### 3. Testar Conexão

```bash
python scripts/init_database.py
```

## 📋 Exemplo Completo

```bash
# 1. Resetar senha (no Cloud Shell ou terminal com gcloud)
gcloud sql users set-password hospicast_user \
    --instance=hospicast-db \
    --password=MinhaSenhaForte123!

# 2. No Git Bash, atualizar DATABASE_URL
export DATABASE_URL="postgresql://hospicast_user:MinhaSenhaForte123!@34.39.151.125:5432/hospicast"

# 3. Verificar
echo $DATABASE_URL

# 4. Testar
python scripts/init_database.py
```

## 💡 Dica: Usar Senha Forte

Use uma senha forte com:
- Pelo menos 8 caracteres
- Letras maiúsculas e minúsculas
- Números
- Caracteres especiais (opcional)

Exemplo: `MinhaSenhaForte123!`

## 🐛 Se Ainda Não Funcionar

### Verificar se o Usuário Existe

```bash
gcloud sql users list --instance=hospicast-db
```

### Verificar se o Banco Existe

```bash
gcloud sql databases list --instance=hospicast-db
```

Deve mostrar o banco `hospicast`.

---

**Reset a senha e atualize a DATABASE_URL com a senha correta!**

