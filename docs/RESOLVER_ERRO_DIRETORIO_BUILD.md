# 🔧 Resolver Erro: "could not find source [./backend]"

## ❌ Erro: Diretório não encontrado

O Cloud Shell não encontrou o diretório `./backend`. Isso significa que:
1. Você não está no diretório correto, OU
2. Os arquivos do projeto não estão no Cloud Shell

## ✅ Solução: Verificar e Corrigir

### Passo 1: Verificar onde você está

```bash
# Ver diretório atual
pwd

# Listar arquivos
ls -la
```

### Passo 2: Verificar se o projeto está no Cloud Shell

```bash
# Procurar pelo diretório backend
find ~ -name "backend" -type d 2>/dev/null

# Ou listar diretórios
ls -la ~/
```

### Passo 3: Opções para ter os arquivos no Cloud Shell

#### Opção A: Clonar do GitHub (Recomendado)

Se seu projeto está no GitHub:

```bash
# Clonar repositório
git clone https://github.com/SEU_USUARIO/portif-lio.git

# Entrar no diretório
cd portif-lio

# Verificar se backend existe
ls -la backend/

# Agora fazer build
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/hospicast-backend:latest ./backend
```

#### Opção B: Fazer Upload via Cloud Shell Editor

1. No Cloud Shell, clique no ícone **"Open Editor"** (lápis) no topo
2. No editor, clique com botão direito na pasta `home`
3. Selecione **"Upload Files"**
4. Selecione os arquivos do seu projeto ou arraste e solte
5. Depois, no terminal:

```bash
# Verificar se os arquivos foram enviados
ls -la

# Se estiver em portif-lio, fazer build
cd portif-lio
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/hospicast-backend:latest ./backend
```

#### Opção C: Usar Caminho Absoluto

Se você sabe onde está o diretório:

```bash
# Exemplo: se estiver em ~/portif-lio/backend
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/hospicast-backend:latest ~/portif-lio/backend
```

## 🚀 Passo a Passo Completo

### 1. Verificar onde está

```bash
pwd
ls -la
```

### 2. Se não tiver o projeto, clonar ou fazer upload

**Clonar do GitHub:**
```bash
git clone https://github.com/SEU_USUARIO/portif-lio.git
cd portif-lio
```

**OU fazer upload via Cloud Shell Editor**

### 3. Verificar estrutura

```bash
# Verificar se backend existe
ls -la backend/

# Verificar se tem Dockerfile
ls -la backend/Dockerfile
```

### 4. Fazer build

```bash
# Se estiver na raiz do projeto
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/hospicast-backend:latest ./backend

# OU se estiver em outro lugar, usar caminho completo
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/hospicast-backend:latest ~/portif-lio/backend
```

## 💡 Dica: Verificar Estrutura

```bash
# Ver estrutura de diretórios
tree -L 2

# OU
find . -name "Dockerfile" -type f
```

---

**Verifique onde você está e onde estão os arquivos do projeto!**

