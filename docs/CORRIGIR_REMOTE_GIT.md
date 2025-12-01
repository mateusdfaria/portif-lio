# 🔧 Corrigir Remote do Git

## ❌ Erro: "remote origin already exists"

O remote já está configurado. Vamos verificar e corrigir.

## 📋 Passos para Corrigir

### 1. Verificar Remote Atual

```bash
# Ver qual remote está configurado
git remote -v
```

### 2. Opções para Corrigir

#### Opção A: Atualizar o Remote Existente

```bash
# Remover o remote atual
git remote remove origin

# Adicionar o remote correto
git remote add origin https://github.com/mateusdfaria/portf-lio.git
```

#### Opção B: Atualizar URL do Remote Existente

```bash
# Atualizar a URL do remote existente
git remote set-url origin https://github.com/mateusdfaria/portf-lio.git

# Verificar se foi atualizado
git remote -v
```

### 3. Verificar se Está Correto

```bash
# Verificar remote
git remote -v

# Deve mostrar:
# origin  https://github.com/mateusdfaria/portf-lio.git (fetch)
# origin  https://github.com/mateusdfaria/portf-lio.git (push)
```

### 4. Fazer Push

```bash
# Verificar status
git status

# Adicionar arquivos se necessário
git add .

# Fazer commit se necessário
git commit -m "Corrigir erro API_ALLOWED_ORIGINS e adicionar documentação"

# Fazer push
git push origin main
# ou
git push origin master
```

## 📋 Comandos Completos

```bash
# === 1. VERIFICAR REMOTE ATUAL ===
git remote -v

# === 2. ATUALIZAR URL DO REMOTE ===
git remote set-url origin https://github.com/mateusdfaria/portf-lio.git

# === 3. VERIFICAR SE FOI ATUALIZADO ===
git remote -v

# === 4. VERIFICAR STATUS ===
git status

# === 5. ADICIONAR E COMMITAR ===
git add .
git commit -m "Corrigir erro API_ALLOWED_ORIGINS e adicionar documentação"

# === 6. FAZER PUSH ===
git push origin main
```

---

**Execute os comandos acima e me avise o resultado!**



