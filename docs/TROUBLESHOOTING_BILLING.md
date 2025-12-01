# 🔧 Troubleshooting - Problemas com Billing

## ❌ Erro: "The billing account is not in good standing"

Este erro significa que você precisa configurar ou corrigir a conta de billing no Google Cloud.

## 🔍 Solução Passo a Passo

### Passo 1: Verificar Status do Billing

1. Acesse o Console do Google Cloud: https://console.cloud.google.com/billing
2. Verifique se há uma conta de billing vinculada ao projeto

### Passo 2: Vincular Conta de Billing

Se não houver conta vinculada:

1. Acesse: https://console.cloud.google.com/billing
2. Clique em **"Criar conta de faturament"** ou **"Link billing account"**
3. Siga as instruções para adicionar um método de pagamento:
   - Cartão de crédito
   - Conta bancária (em alguns países)
   - Fatura (para empresas)

### Passo 3: Verificar Status da Conta

A conta de billing pode estar com problemas se:

- ❌ Cartão de crédito expirado
- ❌ Limite de crédito excedido
- ❌ Pagamento pendente
- ❌ Conta suspensa

**Como verificar:**
1. Acesse: https://console.cloud.google.com/billing
2. Clique na conta de billing
3. Verifique se há alertas ou avisos

### Passo 4: Corrigir Problemas

#### Se o cartão expirou:
1. Acesse: https://console.cloud.google.com/billing
2. Vá em **"Payment methods"** (Métodos de pagamento)
3. Atualize ou adicione um novo cartão

#### Se há pagamento pendente:
1. Verifique o email associado à conta
2. Complete o pagamento pendente
3. Aguarde alguns minutos para processamento

#### Se a conta está suspensa:
1. Entre em contato com o suporte do Google Cloud
2. Ou crie uma nova conta de billing

## 💡 Alternativas Temporárias

### Opção 1: Usar Free Trial (Se Disponível)

O Google Cloud oferece $300 de crédito grátis para novos usuários:

1. Acesse: https://cloud.google.com/free
2. Verifique se você é elegível
3. Ative o free trial

### Opção 2: Usar SQLite Localmente (Desenvolvimento)

Enquanto resolve o billing, você pode continuar desenvolvendo com SQLite:

```bash
# Não configure DATABASE_URL
# O sistema usará SQLite automaticamente
cd backend
python scripts/init_database.py
```

### Opção 3: Usar PostgreSQL Local

Instale PostgreSQL localmente para testar:

**Windows:**
```powershell
# Via Chocolatey
choco install postgresql

# Ou baixe de: https://www.postgresql.org/download/windows/
```

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
```

Depois configure:
```bash
# Criar banco local
createdb hospicast
export DATABASE_URL="postgresql://postgres:senha@localhost:5432/hospicast"
cd backend
python scripts/init_database.py
```

## ✅ Verificar se Billing Está OK

Após configurar o billing, verifique:

```bash
# Verificar projetos e billing
gcloud billing accounts list

# Verificar se o projeto está vinculado
gcloud billing projects describe hospicast-prod

# Se não estiver vinculado, vincule:
gcloud billing projects link hospicast-prod --billing-account=BILLING_ACCOUNT_ID
```

Onde `BILLING_ACCOUNT_ID` você encontra em: https://console.cloud.google.com/billing

## 🆘 Ainda com Problemas?

### Verificar Permissões

Certifique-se de que você tem permissão para gerenciar billing:

```bash
# Verificar suas permissões
gcloud projects get-iam-policy hospicast-prod

# Se necessário, peça ao administrador para dar permissão:
# roles/billing.admin ou roles/billing.projectManager
```

### Contatar Suporte

Se o problema persistir:

1. Acesse: https://cloud.google.com/support
2. Crie um ticket de suporte
3. Ou use o chat de suporte (se disponível)

## 📋 Checklist

- [ ] Conta de billing criada
- [ ] Método de pagamento adicionado e válido
- [ ] Conta de billing vinculada ao projeto
- [ ] Sem pagamentos pendentes
- [ ] Sem cartões expirados
- [ ] Permissões corretas no projeto

## 💰 Custos Estimados

Para começar, você precisará de:

- **Cloud SQL (db-f1-micro)**: ~R$ 35-50/mês
- **Cloud Run**: Primeiros 2 milhões de requisições grátis
- **Total inicial**: ~R$ 40-60/mês

Você pode configurar alertas de billing para não passar do orçamento:

1. Acesse: https://console.cloud.google.com/billing
2. Vá em **"Budgets & alerts"**
3. Configure um alerta (ex: R$ 50/mês)

---

**Depois de resolver o billing, continue com o deploy seguindo o `QUICK_START_GOOGLE_CLOUD.md`**

