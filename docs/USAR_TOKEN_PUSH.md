# 🔐 Usar Token para Fazer Push

## ⚠️ IMPORTANTE: Segurança do Token

**Este token foi exposto!** Após fazer o push, você deve:
1. Revogar este token: https://github.com/settings/tokens
2. Criar um novo token
3. Não compartilhar tokens publicamente

## 📋 Fazer Push com Token

### 1. Configurar Usuário (se ainda não fez)

```bash
git config --global user.name "mateusdfaria"
git config --global user.email "mateusfarias2308@gmail.com"
```

### 2. Fazer Push

```bash
git push origin main
```

**Quando pedir credenciais:**
- **Usuário**: `mateusdfaria`
- **Senha**: `SEU_TOKEN_AQUI` (o token)

### 3. Alternativa: Usar Token na URL (Temporário)

```bash
# Usar token diretamente na URL (apenas uma vez)
git push https://SEU_TOKEN@github.com/mateusdfaria/portif-lio.git main
```

## 📋 Comandos Completos

```bash
# === 1. CONFIGURAR USUÁRIO ===
git config --global user.name "mateusdfaria"
git config --global user.email "mateusfarias2308@gmail.com"

# === 2. VERIFICAR STATUS ===
git status

# === 3. ADICIONAR E COMMITAR (se necessário) ===
git add .
git commit -m "Corrigir erro API_ALLOWED_ORIGINS no Pydantic v2 e adicionar documentação"

# === 4. FAZER PUSH ===
git push origin main
# Quando pedir:
# Usuário: mateusdfaria
# Senha: SEU_TOKEN_AQUI
```

## 🔒 Após o Push - Revogar Token

1. Ir para: https://github.com/settings/tokens
2. Encontrar o token que você usou
3. Clicar em "Revoke"
4. Criar um novo token se necessário

---

**Execute o push agora e depois revogue o token por segurança!**



