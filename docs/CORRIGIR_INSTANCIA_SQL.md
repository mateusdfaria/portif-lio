# 🔧 Corrigir Instância Cloud SQL

Você criou uma instância MySQL, mas precisamos de **PostgreSQL** para o HospiCast.

## ❌ Problemas na Instância Atual

- ❌ **MySQL** ao invés de PostgreSQL
- ❌ Região **us-central1-c** (EUA) ao invés de **southamerica-east1** (Brasil)
- ❌ Tier **db-n1-standard-1** (caro) ao invés de **db-f1-micro** (barato)

## ✅ Solução: Criar Instância Correta

### Passo 1: Deletar Instância Incorreta

```bash
gcloud sql instances delete hospicast-db --quiet
```

### Passo 2: Criar Instância PostgreSQL Correta

```bash
gcloud sql instances create hospicast-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=southamerica-east1 \
    --root-password=SUA_SENHA_FORTE_AQUI
```

**Importante:**
- `POSTGRES_15` - Versão do PostgreSQL
- `db-f1-micro` - Tier mais barato (suficiente para começar)
- `southamerica-east1` - Região de São Paulo (melhor latência para Brasil)
- Escolha uma **senha forte** e guarde em local seguro!

### Passo 3: Criar Banco de Dados

```bash
gcloud sql databases create hospicast --instance=hospicast-db
```

### Passo 4: Criar Usuário

```bash
gcloud sql users create hospicast_user \
    --instance=hospicast-db \
    --password=OUTRA_SENHA_FORTE_AQUI
```

## 📋 Comandos Completos (Copie e Cole)

```bash
# 1. Deletar instância incorreta
gcloud sql instances delete hospicast-db --quiet

# 2. Criar instância PostgreSQL correta
gcloud sql instances create hospicast-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=southamerica-east1 \
    --root-password=SUA_SENHA_FORTE_AQUI

# 3. Criar banco de dados
gcloud sql databases create hospicast --instance=hospicast-db

# 4. Criar usuário
gcloud sql users create hospicast_user \
    --instance=hospicast-db \
    --password=OUTRA_SENHA_FORTE_AQUI
```

## ⏱️ Tempo de Criação

A criação da instância pode levar **5-10 minutos**. Aguarde até aparecer `STATUS: RUNNABLE`.

## ✅ Verificar se Está Correta

```bash
gcloud sql instances describe hospicast-db
```

Deve mostrar:
- `databaseVersion: POSTGRES_15`
- `region: southamerica-east1`
- `settings.tier: db-f1-micro`

## 🚀 Próximos Passos

Após criar a instância correta, continue com:

1. Obter IP público
2. Configurar schema do banco
3. Fazer deploy no Cloud Run

Veja o `QUICK_START_GOOGLE_CLOUD.md` para continuar.

