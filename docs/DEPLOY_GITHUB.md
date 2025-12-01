# 🚀 Deploy no GitHub - Commit e Push

## 📋 Passos para Fazer Deploy no GitHub

### 1. Verificar Status Atual

```bash
# No Cloud Shell ou localmente
cd /home/mateusfarias2308/portif-lio  # ou o caminho do seu projeto

# Verificar status
git status
```

### 2. Adicionar Arquivos Modificados

```bash
# Adicionar todos os arquivos modificados
git add .

# Ou adicionar arquivos específicos
git add backend/core/config.py
git add backend/Dockerfile
git add docs/
```

### 3. Fazer Commit

```bash
# Fazer commit com mensagem descritiva
git commit -m "Corrigir erro API_ALLOWED_ORIGINS no Pydantic v2 e adicionar documentação"
```

### 4. Verificar Remote

```bash
# Verificar se o remote está configurado
git remote -v
```

**Se não aparecer nada**, adicione o remote:

```bash
# Adicionar remote (substitua com seu repositório)
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
```

### 5. Fazer Push

```bash
# Fazer push para o branch main
git push origin main

# Ou se o branch for master
git push origin master

# Se for a primeira vez, use:
git push -u origin main
```

## 🔍 Verificar se Funcionou

```bash
# Verificar status após push
git status

# Verificar último commit
git log -1
```

## ⚠️ Resolver Conflitos

### Se aparecer erro de conflito:

```bash
# Fazer pull primeiro para sincronizar
git pull origin main

# Resolver conflitos manualmente se necessário
# Depois fazer commit e push novamente
git add .
git commit -m "Resolver conflitos"
git push origin main
```

## 📋 Comandos Completos (Copiar e Colar)

```bash
# === 1. NAVEGAR PARA O DIRETÓRIO ===
cd /home/mateusfarias2308/portif-lio

# === 2. VERIFICAR STATUS ===
git status

# === 3. ADICIONAR ARQUIVOS ===
git add .

# === 4. FAZER COMMIT ===
git commit -m "Corrigir erro API_ALLOWED_ORIGINS e adicionar documentação"

# === 5. VERIFICAR REMOTE ===
git remote -v

# === 6. FAZER PUSH ===
git push origin main
# ou
git push origin master
```

## 🔐 Autenticação GitHub

### Se pedir usuário e senha:

**Opção 1: Personal Access Token (Recomendado)**
1. Ir para: https://github.com/settings/tokens
2. Criar novo token com permissões `repo`
3. Usar o token como senha quando pedir

**Opção 2: SSH Key**
```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "seu_email@example.com"

# Adicionar chave ao GitHub
cat ~/.ssh/id_ed25519.pub
# Copiar e adicionar em: https://github.com/settings/keys
```

## 📝 Mensagens de Commit Sugeridas

```bash
# Para correção de bug
git commit -m "fix: corrigir erro API_ALLOWED_ORIGINS no Pydantic v2"

# Para adicionar documentação
git commit -m "docs: adicionar guias de deploy e troubleshooting"

# Para atualizar configuração
git commit -m "chore: atualizar configuração do Docker e Cloud Run"

# Para múltiplas mudanças
git commit -m "fix: corrigir API_ALLOWED_ORIGINS e adicionar documentação"
```

---

**Execute os comandos acima e me avise se funcionou!**



