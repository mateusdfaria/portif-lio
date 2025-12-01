# 🔍 Verificar Clone do Git

## ✅ Verificar se o Git está configurado corretamente

### 1. Verificar Status do Git

```bash
# No Cloud Shell, navegar para o diretório do projeto
cd /home/mateusfarias2308/portif-lio

# Verificar status do Git
git status
```

**O que verificar:**
- ✅ Se aparecer "nothing to commit, working tree clean" = código está sincronizado
- ⚠️ Se aparecer arquivos modificados = há mudanças não commitadas
- ❌ Se aparecer erro = Git não está configurado ou não é um repositório Git

### 2. Verificar Remote (Repositório Remoto)

```bash
# Verificar se o remote está configurado
git remote -v
```

**O que verificar:**
- ✅ Deve mostrar o URL do repositório (GitHub, GitLab, etc.)
- ❌ Se não aparecer nada = não há remote configurado

### 3. Verificar Último Commit

```bash
# Verificar último commit
git log -1
```

**O que verificar:**
- ✅ Deve mostrar o último commit com hash, autor e mensagem
- ❌ Se não aparecer nada = não há commits

### 4. Verificar se há Mudanças Locais

```bash
# Verificar diferenças entre local e remoto
git fetch
git status
```

**O que verificar:**
- ✅ "Your branch is up to date" = está sincronizado
- ⚠️ "Your branch is behind" = precisa fazer pull
- ⚠️ "Your branch is ahead" = precisa fazer push

### 5. Verificar Arquivos Importantes

```bash
# Verificar se os arquivos importantes existem
ls -la backend/core/config.py
ls -la backend/Dockerfile
ls -la backend/main.py
```

**O que verificar:**
- ✅ Todos os arquivos devem existir
- ❌ Se algum arquivo não existir = problema no clone

## 🔄 Sincronizar com o Repositório Remoto

### Se o código local está desatualizado:

```bash
# Fazer pull das mudanças do remoto
git pull origin main
# ou
git pull origin master
```

### Se o código local tem mudanças não commitadas:

```bash
# Ver quais arquivos foram modificados
git status

# Se quiser descartar mudanças locais e usar a versão do remoto
git reset --hard origin/main
# ou
git reset --hard origin/master
```

### Se não há remote configurado:

```bash
# Adicionar remote (substitua com seu repositório)
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git

# Verificar se foi adicionado
git remote -v
```

## 📋 Comandos Completos para Verificação

```bash
# === 1. NAVEGAR PARA O DIRETÓRIO ===
cd /home/mateusfarias2308/portif-lio

# === 2. VERIFICAR STATUS ===
git status

# === 3. VERIFICAR REMOTE ===
git remote -v

# === 4. VERIFICAR ÚLTIMO COMMIT ===
git log -1

# === 5. VERIFICAR SINCRONIZAÇÃO ===
git fetch
git status

# === 6. VERIFICAR ARQUIVOS IMPORTANTES ===
ls -la backend/core/config.py
ls -la backend/Dockerfile
ls -la backend/main.py

# === 7. SE PRECISAR SINCRONIZAR ===
# git pull origin main  # ou master
```

## ⚠️ Importante

- **Se o Git não estiver configurado**: Você pode fazer o rebuild mesmo assim, mas as mudanças locais podem não estar no repositório
- **Se houver mudanças locais**: Decida se quer manter ou descartar antes do rebuild
- **Se o código estiver desatualizado**: Faça pull antes do rebuild para garantir que tem a versão mais recente

---

**Execute os comandos acima e me avise o resultado!**



