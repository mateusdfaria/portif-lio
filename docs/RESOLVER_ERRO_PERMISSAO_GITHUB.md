# 🔐 Resolver Erro de Permissão no GitHub

## ❌ Erro: "Permission denied to caiosntos"

O Git está usando credenciais do usuário errado. Vamos corrigir.

## ✅ Soluções

### Solução 1: Usar Personal Access Token (Recomendado)

#### 1. Criar Personal Access Token

1. Ir para: https://github.com/settings/tokens
2. Clicar em "Generate new token" → "Generate new token (classic)"
3. Dar um nome: `portif-lio-deploy`
4. Selecionar permissões: `repo` (todas)
5. Clicar em "Generate token"
6. **COPIAR O TOKEN** (você só verá uma vez!)

#### 2. Usar Token no Push

```bash
# Quando pedir senha, usar o token (não sua senha normal)
git push origin main

# Usuário: mateusdfaria
# Senha: [COLE O TOKEN AQUI]
```

### Solução 2: Configurar Credenciais do Git

#### Remover credenciais antigas:

```bash
# No Windows (PowerShell)
git config --global --unset credential.helper
git config --system --unset credential.helper

# Limpar credenciais salvas
# Ir para: Painel de Controle → Credenciais do Windows
# Procurar por "github.com" e remover
```

#### Configurar usuário correto:

```bash
# Configurar usuário e email
git config --global user.name "mateusdfaria"
git config --global user.email "mateusfarias2308@gmail.com"

# Verificar
git config --global user.name
git config --global user.email
```

### Solução 3: Usar SSH (Mais Seguro)

#### 1. Gerar Chave SSH

```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "mateusfarias2308@gmail.com"

# Quando pedir, pressionar Enter para usar local padrão
# Quando pedir senha, pode deixar vazio ou criar uma senha

# Ver a chave pública
cat ~/.ssh/id_ed25519.pub
# ou no Windows
type %USERPROFILE%\.ssh\id_ed25519.pub
```

#### 2. Adicionar Chave ao GitHub

1. Copiar a chave pública (saída do comando acima)
2. Ir para: https://github.com/settings/keys
3. Clicar em "New SSH key"
4. Colar a chave e salvar

#### 3. Mudar Remote para SSH

```bash
# Mudar remote de HTTPS para SSH
git remote set-url origin git@github.com:mateusdfaria/portif-lio.git

# Verificar
git remote -v

# Fazer push
git push origin main
```

## 📋 Comandos Completos - Solução Rápida (Token)

```bash
# === 1. CONFIGURAR USUÁRIO ===
git config --global user.name "mateusdfaria"
git config --global user.email "mateusfarias2308@gmail.com"

# === 2. VERIFICAR STATUS ===
git status

# === 3. ADICIONAR E COMMITAR ===
git add .
git commit -m "Corrigir erro API_ALLOWED_ORIGINS no Pydantic v2 e adicionar documentação"

# === 4. FAZER PUSH (usar token quando pedir senha) ===
git push origin main
```

## 🔍 Verificar Credenciais Atuais

```bash
# Ver usuário configurado
git config --global user.name
git config --global user.email

# Ver remote
git remote -v
```

## ⚠️ Importante

- **Personal Access Token**: Mais fácil de configurar, mas precisa ser criado no GitHub
- **SSH**: Mais seguro e não precisa digitar senha toda vez, mas requer configuração inicial
- **Credenciais do Windows**: Podem estar salvando credenciais antigas, precisa limpar

---

**Recomendo usar a Solução 1 (Personal Access Token) por ser mais rápida!**



