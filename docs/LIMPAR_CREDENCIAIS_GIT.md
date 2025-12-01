# 🔧 Limpar Credenciais Antigas do Git

## ❌ Problema: Git ainda usa credenciais antigas

O Git está usando credenciais salvas do usuário "caiosntos". Vamos limpar e usar o token.

## ✅ Solução: Limpar Credenciais e Usar Token

### Opção 1: Usar Token na URL (Mais Rápido)

```bash
# Fazer push usando token diretamente na URL
git push https://SEU_TOKEN_AQUI@github.com/mateusdfaria/portif-lio.git main
```

### Opção 2: Limpar Credenciais e Configurar Token

#### No Windows (PowerShell):

```powershell
# Limpar credenciais do Git
git config --global --unset credential.helper
git credential-manager-core erase https://github.com

# Limpar credenciais do Windows
# Ir para: Painel de Controle → Credenciais do Windows
# Procurar por "github.com" e remover todas as entradas
```

#### Depois fazer push:

```bash
git push origin main
# Quando pedir:
# Usuário: mateusdfaria
# Senha: SEU_TOKEN_AQUI
```

### Opção 3: Configurar Remote com Token

```bash
# Atualizar remote para incluir token
git remote set-url origin https://SEU_TOKEN_AQUI@github.com/mateusdfaria/portif-lio.git

# Verificar
git remote -v

# Fazer push
git push origin main
```

**⚠️ IMPORTANTE**: Após o push, remover o token da URL:

```bash
# Remover token da URL (por segurança)
git remote set-url origin https://github.com/mateusdfaria/portif-lio.git
```

## 📋 Comandos Completos - Solução Rápida

```bash
# === OPÇÃO 1: Push direto com token (mais rápido) ===
git push https://SEU_TOKEN_AQUI@github.com/mateusdfaria/portif-lio.git main

# === OPÇÃO 2: Configurar remote com token ===
git remote set-url origin https://SEU_TOKEN_AQUI@github.com/mateusdfaria/portif-lio.git
git push origin main

# Depois remover token da URL (por segurança)
git remote set-url origin https://github.com/mateusdfaria/portif-lio.git
```

## 🔍 Limpar Credenciais do Windows

1. Pressionar `Win + R`
2. Digitar: `control /name Microsoft.CredentialManager`
3. Ir em "Credenciais do Windows"
4. Procurar por "github.com"
5. Remover todas as entradas relacionadas

## ⚠️ Segurança

Após fazer o push com sucesso:
1. **Revogar este token**: https://github.com/settings/tokens
2. **Criar um novo token** se necessário
3. **Remover token da URL** do remote (se usou Opção 3)

---

**Recomendo usar a Opção 1 (push direto) por ser mais rápida!**
