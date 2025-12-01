# 🔧 Resolver Timeout de Conexão com Cloud SQL

## ❌ Erro: "Connection timed out"

O Cloud SQL está bloqueando sua conexão porque seu IP não está autorizado no firewall.

## ✅ Solução: Autorizar seu IP no Firewall

### Opção 1: Autorizar IP via gcloud (Recomendado)

Se você tem acesso ao `gcloud`:

```bash
# 1. Obter seu IP público
# No Windows, acesse: https://whatismyipaddress.com/
# Ou use este comando no PowerShell:
# (Invoke-WebRequest -Uri "https://api.ipify.org").Content

# 2. Autorizar seu IP no Cloud SQL
gcloud sql instances patch hospicast-db \
    --authorized-networks=SEU_IP_PUBLICO/32

# Exemplo:
# gcloud sql instances patch hospicast-db --authorized-networks=189.123.45.67/32
```

### Opção 2: Autorizar via Console Web

1. Acesse: https://console.cloud.google.com/sql/instances
2. Clique na instância `hospicast-db`
3. Vá em **"Connections"** (Conexões)
4. Clique em **"Add network"** (Adicionar rede)
5. Cole seu IP público e clique em **"Add"** (Adicionar)

### Opção 3: Usar Cloud SQL Proxy (Mais Seguro)

O Cloud SQL Proxy cria um túnel seguro sem precisar autorizar IPs:

```bash
# 1. Baixar Cloud SQL Proxy
# Windows: https://cloud.google.com/sql/docs/postgres/sql-proxy#install

# 2. Obter connection name
gcloud sql instances describe hospicast-db --format="value(connectionName)"

# 3. Executar proxy (em um terminal separado)
cloud-sql-proxy.exe hospicast-prod:southamerica-east1:hospicast-db

# 4. Configurar DATABASE_URL para usar localhost
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA@127.0.0.1:5432/hospicast"

# 5. Testar conexão
python scripts/init_database.py
```

## 🚀 Solução Rápida: Autorizar IP

### Passo 1: Obter seu IP Público

**No Windows:**
- Acesse: https://whatismyipaddress.com/
- Anote o IP que aparece

**Ou no PowerShell:**
```powershell
(Invoke-WebRequest -Uri "https://api.ipify.org").Content
```

### Passo 2: Autorizar no Cloud SQL

**Via gcloud (se tiver acesso):**
```bash
# Substitua SEU_IP_PUBLICO pelo IP que você obteve
gcloud sql instances patch hospicast-db \
    --authorized-networks=SEU_IP_PUBLICO/32
```

**Via Console Web:**
1. https://console.cloud.google.com/sql/instances/hospicast-db/connections
2. Clique em **"Add network"**
3. Cole seu IP
4. Clique em **"Add"**

### Passo 3: Aguardar e Testar

Aguarde alguns segundos e tente novamente:

```bash
python scripts/init_database.py
```

## 💡 Alternativa: Fazer no Cloud Shell

Se você tem acesso ao Cloud Shell, é mais fácil:

```bash
# No Cloud Shell, autorizar IP automaticamente
gcloud sql instances patch hospicast-db \
    --authorized-networks=$(curl -s ifconfig.me)/32

# Depois configure e teste
export DATABASE_URL="postgresql://hospicast_user:SUA_SENHA@34.39.151.125:5432/hospicast"
python scripts/init_database.py
```

## 📋 Checklist

- [ ] Obter IP público
- [ ] Autorizar IP no Cloud SQL (via gcloud ou console)
- [ ] Aguardar alguns segundos
- [ ] Testar conexão novamente

## 🐛 Se Ainda Não Funcionar

### Verificar se a Instância Está Rodando

```bash
gcloud sql instances describe hospicast-db --format="get(state)"
```

Deve mostrar: `RUNNABLE`

### Verificar IP Público da Instância

```bash
gcloud sql instances describe hospicast-db --format="get(ipAddresses[0].ipAddress)"
```

Deve ser o mesmo IP que você está usando na DATABASE_URL.

### Verificar Firewall

```bash
# Ver IPs autorizados
gcloud sql instances describe hospicast-db --format="get(settings.ipConfiguration.authorizedNetworks)"
```

---

**Autorize seu IP no Cloud SQL e tente novamente!**

