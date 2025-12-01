# 🔐 Login no GitHub no Cloud Shell

## ✅ Solução Rápida (Token já configurado)

Seu repositório já está configurado com token! Basta configurar o Git e fazer push:

```bash
# === 1. CONFIGURAR GIT ===
git config --global user.name "Mateus Farias"
git config --global user.email "mateusfarias2308@gmail.com"

# === 2. IR PARA O PROJETO ===
cd ~/portif-lio

# === 3. VERIFICAR REMOTE ===
git remote -v

# === 4. FAZER PUSH ===
git push origin main
```

**O token já está na URL do remote, então não precisa digitar senha!** ✅

---

## 📋 Métodos Disponíveis

### Método 1: Personal Access Token (Recomendado) ✅

Este é o método mais seguro e recomendado.

#### 1. Criar Personal Access Token no GitHub

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token"** → **"Generate new token (classic)"**
3. Configure:
   - **Note**: `Cloud Shell - HospiCast`
   - **Expiration**: Escolha uma data (ou "No expiration")
   - **Scopes**: Marque:
     - ✅ `repo` (acesso completo aos repositórios)
     - ✅ `workflow` (se usar GitHub Actions)
4. Clique em **"Generate token"**
5. **COPIE O TOKEN** (você só verá ele uma vez!)

#### 2. Configurar Git no Cloud Shell

```bash
# Configurar nome e email
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@gmail.com"

# Configurar remote com token
git remote set-url origin https://SEU_TOKEN@github.com/mateusdfaria/portif-lio.git
```

#### 3. Fazer Push

```bash
cd ~/portif-lio
git push origin main
```

**Quando pedir credenciais:**
- **Username**: seu usuário do GitHub
- **Password**: o **TOKEN** que você copiou (não sua senha do GitHub!)

---

### Método 2: SSH Key (Alternativo) 🔑

#### 1. Gerar SSH Key no Cloud Shell

```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "seu-email@gmail.com"

# Quando pedir, pressione Enter para usar o caminho padrão
# Quando pedir senha, pressione Enter (sem senha)

# Mostrar chave pública
cat ~/.ssh/id_ed25519.pub
```

#### 2. Adicionar SSH Key no GitHub

1. Copie o conteúdo de `~/.ssh/id_ed25519.pub`
2. Acesse: https://github.com/settings/keys
3. Clique em **"New SSH key"**
4. Configure:
   - **Title**: `Cloud Shell - HospiCast`
   - **Key**: Cole o conteúdo copiado
5. Clique em **"Add SSH key"**

#### 3. Configurar Git

```bash
# Configurar nome e email
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@gmail.com"
```

#### 4. Alterar Remote para SSH

```bash
cd ~/portif-lio

# Verificar remote atual
git remote -v

# Alterar para SSH (se estiver usando HTTPS)
git remote set-url origin git@github.com:SEU_USUARIO/portif-lio.git

# Testar conexão
ssh -T git@github.com

# Fazer push
git push origin main
```

---

## 🚀 Comandos Rápidos - Cloud Shell

```bash
# === 1. CONFIGURAR GIT ===
git config --global user.name "Mateus Farias"
git config --global user.email "mateusfarias2308@gmail.com"

# === 2. IR PARA O PROJETO ===
cd ~/portif-lio

# === 3. VERIFICAR REMOTE ===
git remote -v
# Deve mostrar: https://SEU_TOKEN@github.com/mateusdfaria/portif-lio.git

# === 4. FAZER PUSH ===
git push origin main
# Não precisa digitar senha - o token já está na URL!
```

**Se o remote não estiver configurado:**

```bash
# Adicionar remote com token
git remote add origin https://SEU_TOKEN@github.com/mateusdfaria/portif-lio.git

# Ou atualizar remote existente
git remote set-url origin https://SEU_TOKEN@github.com/mateusdfaria/portif-lio.git
```

---

## 🔍 Verificar Configuração

```bash
# Ver configurações do Git
git config --global --list

# Ver remote configurado
git remote -v

# Testar conexão (SSH)
ssh -T git@github.com
```

---

## ⚠️ Troubleshooting

### Erro: "Permission denied (publickey)"

**Solução**: Use o Método 1 (Personal Access Token) ou configure SSH corretamente.

### Erro: "Authentication failed"

**Solução**: 
- Verifique se o token está correto
- Use o token como senha, não sua senha do GitHub
- Regere o token se necessário

### Erro: "remote origin already exists"

**Solução**:
```bash
# Ver remote atual
git remote -v

# Remover e adicionar novamente
git remote remove origin
git remote add origin https://github.com/SEU_USUARIO/portif-lio.git
```

---

**Recomendação**: Use o **Método 1 (Personal Access Token)** - é mais simples e funciona imediatamente! 🎯

