# 📤 Usar SCP para Transferir Arquivos

## 📋 O que é SCP?

SCP (Secure Copy Protocol) permite transferir arquivos entre seu computador e servidores remotos de forma segura.

## 🔧 Pré-requisitos

### No Windows:
- **Opção 1**: Usar Git Bash (já vem com SCP)
- **Opção 2**: Usar PowerShell com OpenSSH (Windows 10+)
- **Opção 3**: Usar WSL (Windows Subsystem for Linux)

### Verificar se SCP está instalado:

```bash
# No Git Bash ou PowerShell
scp

# Deve mostrar ajuda do comando
```

## 📤 Transferir Arquivos para Cloud Shell

### Opção 1: Via Cloud Shell Upload

Cloud Shell tem upload integrado:

```bash
# No Cloud Shell, clicar no menu (3 linhas) → Upload file
# Ou usar o editor e arrastar arquivos
```

### Opção 2: Via SCP (do seu PC para Cloud Shell)

**Cloud Shell não aceita conexões SCP diretas**, mas você pode:

1. **Fazer upload via Console Web**:
   - Abrir Cloud Shell Editor
   - Clicar com botão direito → Upload Files

2. **Usar Git** (recomendado):
   ```bash
   # No seu PC
   git add .
   git commit -m "Atualizar código"
   git push origin main
   
   # No Cloud Shell
   cd ~/portif-lio
   git pull origin main
   ```

## 📥 Transferir Arquivos do Cloud Shell para seu PC

### Usar SCP do Cloud Shell para PC:

```bash
# No Cloud Shell, obter seu IP público
curl ifconfig.me

# No seu PC (Git Bash ou PowerShell)
# Substituir USERNAME e IP
scp -r mateusfarias2308@IP_PUBLICO:~/portif-lio/backend ./backend-backup
```

## 🔄 Transferir entre Servidores

### Exemplo: De Cloud Shell para Cloud Run (via Container)

```bash
# Não é necessário - Cloud Build faz isso automaticamente
```

## 📋 Comandos SCP Comuns

### Sintaxe Básica:

```bash
scp [opções] origem destino
```

### Exemplos:

#### 1. Copiar arquivo único:

```bash
# Do PC para servidor
scp arquivo.txt usuario@servidor:/caminho/destino/

# Do servidor para PC
scp usuario@servidor:/caminho/arquivo.txt ./
```

#### 2. Copiar pasta inteira:

```bash
# Do PC para servidor (recursivo)
scp -r pasta/ usuario@servidor:/caminho/destino/

# Do servidor para PC
scp -r usuario@servidor:/caminho/pasta/ ./
```

#### 3. Com porta customizada:

```bash
scp -P 2222 arquivo.txt usuario@servidor:/caminho/
```

#### 4. Com chave SSH:

```bash
scp -i ~/.ssh/chave_privada arquivo.txt usuario@servidor:/caminho/
```

## 🎯 Para HospiCast - Transferir Projeto

### Opção 1: Via Git (Recomendado)

```bash
# No seu PC
cd C:\Users\Caio\Downloads\hospcast\portif-lio
git add .
git commit -m "Atualizar código"
git push origin main

# No Cloud Shell
cd ~/portif-lio
git pull origin main
```

### Opção 2: Via Cloud Shell Editor

1. Abrir Cloud Shell Editor
2. Clicar com botão direito na pasta
3. Selecionar "Upload Files"
4. Selecionar arquivos do projeto

### Opção 3: Via SCP (se tiver servidor SSH)

Se você tiver um servidor SSH acessível:

```bash
# Do PC para servidor
scp -r C:\Users\Caio\Downloads\hospcast\portif-lio\backend\ \
    usuario@servidor:/caminho/backend/

# Do servidor para PC
scp -r usuario@servidor:/caminho/backend/ \
    C:\Users\Caio\Downloads\hospcast\portif-lio\backend-backup\
```

## 🔐 Autenticação SSH

### Usar chave SSH (mais seguro):

```bash
# Gerar chave SSH (se ainda não tiver)
ssh-keygen -t ed25519 -C "seu_email@example.com"

# Copiar chave pública para servidor
ssh-copy-id usuario@servidor

# Usar SCP com chave
scp -i ~/.ssh/id_ed25519 arquivo.txt usuario@servidor:/caminho/
```

### Usar senha:

```bash
# SCP pedirá senha quando necessário
scp arquivo.txt usuario@servidor:/caminho/
```

## 📋 Comandos Úteis

### Verificar conexão SSH:

```bash
# Testar conexão
ssh usuario@servidor

# Testar com verbose
ssh -v usuario@servidor
```

### Transferir com progresso:

```bash
# Mostrar progresso
scp -v arquivo.txt usuario@servidor:/caminho/

# Ou usar rsync (mais eficiente)
rsync -avz --progress pasta/ usuario@servidor:/caminho/
```

## ⚠️ Limitações do Cloud Shell

**Cloud Shell não aceita conexões SSH/SCP externas** por segurança. Use:

1. ✅ **Git** (recomendado)
2. ✅ **Cloud Shell Editor** (upload de arquivos)
3. ✅ **Cloud Storage** (gsutil)

## 🎯 Solução Recomendada para HospiCast

### Workflow Ideal:

```bash
# 1. No seu PC - Fazer mudanças
cd C:\Users\Caio\Downloads\hospcast\portif-lio
# ... fazer mudanças no código ...

# 2. Commit e Push
git add .
git commit -m "Descrição das mudanças"
git push origin main

# 3. No Cloud Shell - Atualizar
cd ~/portif-lio
git pull origin main

# 4. Fazer deploy
gcloud builds submit --tag gcr.io/hospicast-prod/hospicast-backend:latest ./backend
```

## 📤 Alternativa: Usar Cloud Storage

### Upload via gsutil:

```bash
# Criar bucket (se não existir)
gsutil mb gs://hospicast-uploads

# Upload do PC (se tiver gsutil instalado)
gsutil cp -r backend/ gs://hospicast-uploads/

# Download no Cloud Shell
gsutil cp -r gs://hospicast-uploads/backend/ ./
```

---

**Para HospiCast, recomendo usar Git para sincronizar código entre PC e Cloud Shell!**



