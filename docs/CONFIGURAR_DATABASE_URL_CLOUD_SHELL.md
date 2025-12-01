# 🔧 Configurar DATABASE_URL no Cloud Shell

No Cloud Shell do Google Cloud, você está em um ambiente Linux, então a sintaxe bash está correta!

## ❌ Erro na Sua URL

Você escreveu:
```bash
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA_FORTE@[IP]:34.39.151.125/hospicast"
```

**Problemas:**
1. `[IP]:34.39.151.125` está errado - deve ser apenas `34.39.151.125`
2. Falta a porta `:5432` (porta padrão do PostgreSQL)

## ✅ Forma Correta no Cloud Shell

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
# Navegar para o backend (se você clonou o repositório)
cd ~/portif-lio/backend

# OU se você fez upload dos arquivos
cd backend

# Executar script de inicialização
python3 scripts/init_database.py
```

Se funcionar, você verá:
```
✅ Banco de dados inicializado com sucesso!
📊 Tabelas criadas: hospital_accounts, hospital_sessions, hospital_forecasts
```

## 🔍 Obter IP Público (Se Precisar)

Se você não tem certeza do IP, obtenha com:

```bash
gcloud sql instances describe hospicast-db --format="get(ipAddresses[0].ipAddress)"
```

## 🐛 Problemas Comuns

### Erro: "could not connect to server"

1. Verifique se o IP está correto
2. Verifique se a porta é 5432
3. Verifique se a senha está correta
4. **No Cloud Shell, você pode precisar autorizar seu IP no firewall do Cloud SQL**

Para autorizar o IP do Cloud Shell:

```bash
# Obter IP do Cloud Shell
curl -s ifconfig.me

# Adicionar ao firewall do Cloud SQL
gcloud sql instances patch hospicast-db \
    --authorized-networks=$(curl -s ifconfig.me)/32
```

### Erro: "password authentication failed"

1. Verifique se o usuário está correto (`hospicast_user`)
2. Verifique se a senha está correta
3. Tente resetar a senha:
   ```bash
   gcloud sql users set-password hospicast_user \
       --instance=hospicast-db \
       --password=NOVA_SENHA
   ```

### Erro: "psycopg2 not found"

Instale as dependências:

```bash
cd ~/portif-lio/backend
pip3 install -r requirements.txt
```

## 📝 Exemplo Completo no Cloud Shell

```bash
# 1. Clonar repositório (se ainda não clonou)
# git clone SEU_REPOSITORIO
# cd portif-lio

# 2. Obter IP do Cloud SQL
IP=$(gcloud sql instances describe hospicast-db --format="get(ipAddresses[0].ipAddress)")
echo "IP do Cloud SQL: $IP"

# 3. Autorizar IP do Cloud Shell (se necessário)
gcloud sql instances patch hospicast-db \
    --authorized-networks=$(curl -s ifconfig.me)/32

# 4. Configurar variável (substitua SUA_SENHA_FORTE pela senha real)
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA_FORTE@$IP:5432/hospicast"

# 5. Verificar
echo $DATABASE_URL

# 6. Instalar dependências (se necessário)
cd backend
pip3 install -r requirements.txt

# 7. Testar conexão
python3 scripts/init_database.py
```

## 💡 Dica: Usar Connection Name (Recomendado para Cloud Shell)

No Cloud Shell, você pode usar o connection name ao invés do IP, o que é mais seguro:

```bash
# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe hospicast-db --format="value(connectionName)")
echo "Connection name: $CONNECTION_NAME"

# Usar connection name na URL (requer Cloud SQL Proxy ou Unix socket)
# Para Cloud Run, você usará o formato:
# postgresql://user:pass@localhost/db?host=/cloudsql/CONNECTION_NAME
```

Mas para desenvolvimento/teste no Cloud Shell, usar o IP público funciona bem.

## 🔐 Segurança

**NUNCA** commite senhas no Git! Sempre use:
- Variáveis de ambiente
- Secret Manager (em produção)
- Arquivo `.env` (adicionado ao `.gitignore`)

---

**Depois de configurar, continue com os próximos passos do deploy!**

