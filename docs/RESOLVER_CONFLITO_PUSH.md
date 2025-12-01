# 🔄 Resolver Conflito ao Fazer Push

## ❌ Erro: "Updates were rejected because the remote contains work"

O repositório remoto (GitHub) tem commits que não estão no repositório local (Cloud Shell).

## ✅ Solução: Fazer Pull Primeiro

### Opção 1: Pull e Merge (Recomendado) ✅

```bash
cd ~/portif-lio

# 1. Fazer pull das alterações remotas
git pull origin main --no-rebase

# 2. Se houver conflitos, resolvê-los e depois:
git add .
git commit -m "merge: integrar alterações remotas"

# 3. Fazer push
git push origin main
```

### Opção 2: Pull com Rebase (Histórico Linear)

```bash
cd ~/portif-lio

# 1. Fazer pull com rebase
git pull origin main --rebase

# 2. Se houver conflitos, resolvê-los e depois:
git add .
git rebase --continue

# 3. Fazer push
git push origin main
```

### Opção 3: Forçar Push (⚠️ CUIDADO - Só se tiver certeza)

**⚠️ ATENÇÃO**: Isso vai **sobrescrever** o histórico remoto. Use apenas se:
- Você tem certeza que as alterações remotas não são importantes
- Você está trabalhando sozinho no projeto
- Você quer descartar as alterações remotas

```bash
cd ~/portif-lio

# Forçar push (sobrescreve o remoto)
git push origin main --force
```

**⚠️ NÃO use `--force` se outras pessoas estão trabalhando no projeto!**

---

## 🚀 Comandos Completos - Solução Recomendada

```bash
# === 1. IR PARA O PROJETO ===
cd ~/portif-lio

# === 2. VERIFICAR STATUS ===
git status

# === 3. FAZER PULL ===
git pull origin main --no-rebase

# === 4. SE HOUVER CONFLITOS ===
# Editar os arquivos com conflitos (procure por <<<<<<<)
# Depois:
git add .
git commit -m "merge: integrar alterações remotas"

# === 5. FAZER PUSH ===
git push origin main
```

---

## 🔍 Verificar o que está diferente

```bash
# Ver commits que estão no remoto mas não no local
git fetch origin
git log HEAD..origin/main

# Ver commits que estão no local mas não no remoto
git log origin/main..HEAD

# Ver diferenças
git diff origin/main
```

---

## 📋 Fluxo Completo (Pull + Push)

```bash
# === 1. CONFIGURAR GIT (se ainda não fez) ===
git config --global user.name "Mateus Farias"
git config --global user.email "mateusfarias2308@gmail.com"

# === 2. IR PARA O PROJETO ===
cd ~/portif-lio

# === 3. ADICIONAR ALTERAÇÕES LOCAIS (se houver) ===
git add backend/requirements.txt backend/core/config.py docs/

# === 4. COMMIT (se houver alterações não commitadas) ===
git commit -m "fix: atualizar para Pydantic v2 com versões compatíveis"

# === 5. FAZER PULL ===
git pull origin main --no-rebase

# === 6. RESOLVER CONFLITOS (se houver) ===
# Se aparecerem conflitos, edite os arquivos e depois:
# git add .
# git commit -m "merge: integrar alterações remotas"

# === 7. FAZER PUSH ===
git push origin main
```

---

## ⚠️ Se Houver Conflitos

Quando você faz `git pull`, pode aparecer algo como:

```
Auto-merging backend/requirements.txt
CONFLICT (content): Merge conflict in backend/requirements.txt
```

### Resolver Conflitos:

1. **Abrir o arquivo com conflito** (ex: `backend/requirements.txt`)
2. **Procurar por marcadores de conflito**:
   ```
   <<<<<<< HEAD
   (suas alterações locais)
   =======
   (alterações remotas)
   >>>>>>> origin/main
   ```
3. **Escolher qual versão manter** ou **combinar ambas**
4. **Remover os marcadores** (`<<<<<<<`, `=======`, `>>>>>>>`)
5. **Salvar o arquivo**
6. **Adicionar e commitar**:
   ```bash
   git add backend/requirements.txt
   git commit -m "merge: resolver conflito em requirements.txt"
   ```
7. **Fazer push**:
   ```bash
   git push origin main
   ```

---

**Execute os comandos acima para resolver o conflito!** 🎯

