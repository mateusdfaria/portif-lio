# 🔄 Atualizar GitHub e Cloud Shell

## 📋 Passo 1: Fazer Commit e Push para GitHub

### No Seu Computador (Windows)

```bash
cd C:\Users\Caio\Downloads\hospcast\portif-lio

# === 1. VER STATUS ===
git status

# === 2. ADICIONAR TODAS AS ALTERAÇÕES ===
git add .

# === 3. COMMIT ===
git commit -m "feat: adicionar workflow de deploy completo e documentação"

# === 4. PUSH ===
git push origin main
```

### Se Der Erro de Autenticação

```bash
# Verificar remote
git remote -v

# Se precisar configurar token
git remote set-url origin https://SEU_TOKEN@github.com/mateusdfaria/portif-lio.git

# Depois fazer push
git push origin main
```

---

## 📋 Passo 2: Atualizar no Cloud Shell

### Opção 1: Pull (Atualizar Arquivos Existentes)

```bash
cd ~/portif-lio

# === 1. VER STATUS ===
git status

# === 2. VERIFICAR BRANCH ===
git branch

# === 3. FAZER PULL ===
git pull origin main

# === 4. VERIFICAR ===
git status
```

### Opção 2: Clone Limpo (Se Tiver Problemas)

Se o pull não funcionar ou houver conflitos:

```bash
# === 1. BACKUP (OPCIONAL) ===
cd ~
cp -r portif-lio portif-lio-backup 2>/dev/null || echo "Backup opcional"

# === 2. REMOVER DIRETÓRIO ANTIGO ===
rm -rf portif-lio

# === 3. CLONE NOVO ===
git clone https://github.com/mateusdfaria/portif-lio.git

# === 4. ENTRAR NO DIRETÓRIO ===
cd portif-lio

# === 5. VERIFICAR ===
ls -la
git status
```

---

## 📋 Comandos Completos

### No Windows (Fazer Push)

```bash
cd C:\Users\Caio\Downloads\hospcast\portif-lio

# Ver o que mudou
git status

# Adicionar tudo
git add .

# Commit
git commit -m "feat: adicionar workflow de deploy completo e documentação

- Adicionar deploy-completo.yml (backend + frontend)
- Adicionar documentação de configuração de secrets
- Adicionar guias de troubleshooting"

# Push
git push origin main
```

### No Cloud Shell (Fazer Pull)

```bash
cd ~/portif-lio

# Ver status atual
git status

# Verificar se está na branch main
git branch

# Fazer pull das atualizações
git pull origin main

# Verificar se atualizou
git status
ls -la .github/workflows/
```

---

## 🔍 Verificar se Atualizou

### No Cloud Shell

```bash
cd ~/portif-lio

# Ver se o arquivo novo existe
ls -la .github/workflows/deploy-completo.yml

# Ver conteúdo
cat .github/workflows/deploy-completo.yml | head -20

# Ver se os docs foram atualizados
ls -la docs/ | grep -i "deploy\|secret\|config"
```

---

## 🚨 Se Houver Conflitos

### Resolver Conflitos no Pull

```bash
cd ~/portif-lio

# Tentar pull
git pull origin main

# Se der conflito, ver arquivos com conflito
git status

# Para cada arquivo com conflito:
# 1. Abrir o arquivo
# 2. Procurar por <<<<<<< HEAD
# 3. Resolver manualmente
# 4. Adicionar: git add arquivo
# 5. Continuar: git commit
```

### Ou Fazer Merge

```bash
# Fazer merge mantendo suas alterações locais
git pull origin main --no-rebase

# Se houver conflitos, resolver e depois:
git add .
git commit -m "merge: integrar alterações remotas"
```

---

## ✅ Checklist

### No Windows:
- [ ] `git status` mostra arquivos modificados
- [ ] `git add .` adicionou tudo
- [ ] `git commit` criou commit
- [ ] `git push` enviou para GitHub
- [ ] Verificou no GitHub que os arquivos foram enviados

### No Cloud Shell:
- [ ] `git pull` baixou as atualizações
- [ ] `deploy-completo.yml` existe
- [ ] Documentação foi atualizada
- [ ] Tudo está sincronizado

---

## 🔄 Workflow Completo

### 1. Fazer Alterações Localmente (Windows)
```bash
# Fazer suas alterações
# ...

# Commit e push
git add .
git commit -m "sua mensagem"
git push origin main
```

### 2. Atualizar no Cloud Shell
```bash
cd ~/portif-lio
git pull origin main
```

### 3. Usar no Cloud Shell
```bash
# Agora você pode usar os arquivos atualizados
cd ~/portif-lio
# ... seus comandos ...
```

---

## 📝 Exemplo de Mensagem de Commit

```bash
git commit -m "feat: adicionar workflow de deploy completo

- Criar deploy-completo.yml para deploy unificado
- Adicionar documentação de configuração de secrets
- Adicionar guias de troubleshooting
- Atualizar documentação de deploy"
```

---

**Execute os comandos acima para atualizar GitHub e Cloud Shell!** 🎯

