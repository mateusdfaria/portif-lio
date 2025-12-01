# 🔧 Configurar DATABASE_URL no Bash (Git Bash)

## ❌ Erro na Sua URL

Você escreveu:
```bash
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA_FORTE@[IP]:34.39.151.125/hospicast"
```

**Problemas:**
1. `[IP]:34.39.151.125` está errado - deve ser apenas `34.39.151.125`
2. Falta a porta `:5432` (porta padrão do PostgreSQL)

## ✅ Forma Correta no Bash

```bash
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA_FORTE@34.39.151.125:5432/hospicast"
```

**Importante:** 
- Substitua `SUA_SENHA_FORTE` pela senha real que você criou
- A porta padrão do PostgreSQL é `5432`
- Remova o `[IP]:` - use apenas o IP diretamente

## 📋 Formato Correto da URL

```
postgresql://[usuário]:[senha]@[IP]:[porta]/[banco]
```

**Exemplo completo:**
```bash
export DATABASE_URL="postgresql://hospicast_user:minhasenha123@34.39.151.125:5432/hospicast"
```

## ✅ Verificar se Funcionou

```bash
# Verificar se a variável foi configurada
echo $DATABASE_URL
```

## ✅ Testar Conexão

Após configurar, teste:

```bash
# Navegar para o backend
cd backend

# Executar script de inicialização
python scripts/init_database.py
```

Se funcionar, você verá:
```
✅ Banco de dados inicializado com sucesso!
📊 Tabelas criadas: hospital_accounts, hospital_sessions, hospital_forecasts
```

## 🔍 Verificar IP Público

Se você não tem certeza do IP, obtenha com:

```bash
gcloud sql instances describe hospicast-db --format="get(ipAddresses[0].ipAddress)"
```

## 🐛 Problemas Comuns

### Erro: "could not connect to server"

1. Verifique se o IP está correto (34.39.151.125)
2. Verifique se a porta é 5432
3. Verifique se a senha está correta
4. Verifique se o Cloud SQL permite conexões do seu IP (firewall)

### Erro: "password authentication failed"

1. Verifique se o usuário está correto (`hospicast_user`)
2. Verifique se a senha está correta
3. Tente resetar a senha:
   ```bash
   gcloud sql users set-password hospicast_user \
       --instance=hospicast-db \
       --password=NOVA_SENHA
   ```

### Erro: "connection timeout"

O Cloud SQL pode estar bloqueando seu IP. Para desenvolvimento local, você pode:

1. **Usar Cloud SQL Proxy** (recomendado):
   ```bash
   # Baixar proxy
   # Windows: https://cloud.google.com/sql/docs/postgres/sql-proxy#install
   
   # Executar proxy
   ./cloud-sql-proxy hospicast-prod:southamerica-east1:hospicast-db
   
   # Depois use:
   export DATABASE_URL="postgresql://hospicast_user:senha@127.0.0.1:5432/hospicast"
   ```

2. **Ou adicionar seu IP ao firewall do Cloud SQL**:
   ```bash
   # Obter seu IP público
   # Acesse: https://whatismyipaddress.com/
   
   # Adicionar ao firewall
   gcloud sql instances patch hospicast-db \
       --authorized-networks=SEU_IP_PUBLICO/32
   ```

## 📝 Exemplo Completo

```bash
# 1. Configurar variável (substitua SUA_SENHA_FORTE pela senha real)
export DATABASE_URL="postgresql://hospicast_user:minhasenha123@34.39.151.125:5432/hospicast"

# 2. Verificar
echo $DATABASE_URL

# 3. Testar conexão
cd backend
python scripts/init_database.py
```

## 💡 Dica: Criar Arquivo .env

Para não precisar exportar toda vez, crie um arquivo `.env` na raiz do projeto:

```bash
# Criar arquivo .env
cat > .env << EOF
DATABASE_URL=postgresql://hospicast_user:SUA_SENHA_FORTE@34.39.151.125:5432/hospicast
API_ALLOWED_ORIGINS=*
LOG_LEVEL=INFO
PROMETHEUS_ENABLED=true
EOF
```

**⚠️ IMPORTANTE:** Adicione `.env` ao `.gitignore` para não commitar senhas!

## 🔐 Segurança

**NUNCA** commite senhas no Git! Sempre use:
- Arquivo `.env` (adicionado ao `.gitignore`)
- Variáveis de ambiente
- Secret Manager (em produção)

---

**Depois de configurar, continue com os próximos passos do deploy!**

