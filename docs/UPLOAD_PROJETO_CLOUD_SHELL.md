# 📤 Fazer Upload do Projeto para Cloud Shell

Você precisa ter os arquivos do projeto no Cloud Shell antes de executar os comandos.

## 🎯 Opções para Ter os Arquivos no Cloud Shell

### Opção 1: Clonar do GitHub (Recomendado)

Se seu projeto está no GitHub:

```bash
# Clonar repositório
git clone https://github.com/SEU_USUARIO/portif-lio.git

# OU se for privado, use SSH
git clone git@github.com:SEU_USUARIO/portif-lio.git

# Entrar no diretório
cd portif-lio

# Agora você pode executar
cd backend
python3 scripts/init_database.py
```

### Opção 2: Fazer Upload via Cloud Shell Editor

1. No Cloud Shell, clique no ícone **"Open Editor"** (lápis) no topo
2. Clique com botão direito na pasta `home` ou crie uma nova pasta
3. Clique em **"Upload Files"**
4. Selecione os arquivos do seu projeto
5. Ou arraste e solte os arquivos

### Opção 3: Fazer Upload via gcloud (se estiver no seu computador)

Se você está no seu computador local e quer enviar para o Cloud Shell:

```bash
# No seu computador local (não no Cloud Shell)
# Compactar o projeto
tar -czf portif-lio.tar.gz portif-lio/

# Enviar para Cloud Storage
gsutil cp portif-lio.tar.gz gs://SEU_BUCKET/

# No Cloud Shell, baixar
gsutil cp gs://SEU_BUCKET/portif-lio.tar.gz .
tar -xzf portif-lio.tar.gz
cd portif-lio
```

### Opção 4: Criar Estrutura Manualmente (Rápido para Teste)

Se você só quer testar a conexão rapidamente, pode criar os arquivos essenciais:

```bash
# Criar estrutura de diretórios
mkdir -p portif-lio/backend/scripts
mkdir -p portif-lio/backend/core
mkdir -p portif-lio/backend/services

# Entrar no diretório
cd portif-lio
```

Mas isso é trabalhoso. **Melhor usar a Opção 1 (GitHub) ou Opção 2 (Upload)**.

## ✅ Verificar se os Arquivos Estão Lá

```bash
# Ver onde você está
pwd

# Listar arquivos
ls -la

# Se você clonou do GitHub
ls -la portif-lio/

# Ver estrutura do backend
ls -la portif-lio/backend/
```

## 🚀 Depois de Ter os Arquivos

```bash
# 1. Entrar no diretório do projeto
cd portif-lio

# 2. Verificar se DATABASE_URL está configurada
echo $DATABASE_URL

# 3. Autorizar IP do Cloud Shell (se necessário)
gcloud sql instances patch hospicast-db \
    --authorized-networks=$(curl -s ifconfig.me)/32

# 4. Instalar dependências
cd backend
pip3 install -r requirements.txt

# 5. Testar conexão
python3 scripts/init_database.py
```

## 💡 Dica: Usar Cloud Shell Editor

O Cloud Shell tem um editor visual que facilita muito:

1. Clique no ícone **"Open Editor"** (lápis) no topo do Cloud Shell
2. No editor, você pode:
   - Criar pastas
   - Fazer upload de arquivos
   - Editar arquivos
   - Ver a estrutura do projeto

## 📋 Checklist

- [ ] Projeto está no Cloud Shell (via GitHub, upload ou Cloud Storage)
- [ ] Você está no diretório correto (`cd portif-lio`)
- [ ] DATABASE_URL está configurada (`echo $DATABASE_URL`)
- [ ] IP do Cloud Shell está autorizado no Cloud SQL
- [ ] Dependências estão instaladas (`pip3 install -r requirements.txt`)

---

**Qual opção você quer usar? GitHub é a mais fácil!**

