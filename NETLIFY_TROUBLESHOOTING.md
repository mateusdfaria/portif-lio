# 🔧 Troubleshooting Netlify - HospiCast

## ❌ Erro: "Could not read package.json: ENOENT: no such file or directory"

### Possíveis Causas

1. **Repositório conectado incorretamente**
   - O Netlify pode estar conectado ao repositório errado
   - O repositório pode estar apontando para um subdiretório

2. **Branch incorreta**
   - O Netlify pode estar usando uma branch que não tem os arquivos

3. **Estrutura de diretórios**
   - O Netlify pode estar esperando os arquivos em um local diferente

## ✅ Soluções

### 1. Verificar Repositório Conectado

1. Acesse: https://app.netlify.com
2. Vá em **Site settings** → **Build & deploy** → **Continuous Deployment**
3. Verifique:
   - **Repository**: Deve ser `mateusdfaria/portif-lio`
   - **Branch**: Deve ser `main`
   - **Base directory**: Deve estar **VAZIO** (não preencher)
   - **Publish directory**: `frontend/dist`
   - **Build command**: `cd frontend && npm ci && npm run build`

### 2. Verificar Estrutura do Repositório

Execute no terminal local:
```bash
git ls-files frontend/package.json
```

Deve retornar: `frontend/package.json`

Se não retornar nada, o arquivo não está no repositório. Adicione:
```bash
git add frontend/package.json
git commit -m "fix: Adiciona package.json"
git push origin main
```

### 3. Verificar Arquivos no GitHub

1. Acesse: https://github.com/mateusdfaria/portif-lio
2. Navegue até: `frontend/package.json`
3. Verifique se o arquivo existe e está visível

### 4. Reconfigurar Site no Netlify

Se nada funcionar, reconfigure o site:

1. **Site settings** → **General** → **Site details**
2. Anote o **Site name** e **Site ID**
3. Vá em **Build & deploy** → **Continuous Deployment**
4. Clique em **Link to a different branch**
5. Selecione novamente: `mateusdfaria/portif-lio` → `main`
6. Configure:
   - **Base directory**: (deixe vazio)
   - **Build command**: `cd frontend && npm ci && npm run build`
   - **Publish directory**: `frontend/dist`

### 5. Limpar Cache e Fazer Deploy Manual

1. **Deploys** → **Trigger deploy** → **Clear cache and deploy site**
2. Isso força um novo clone do repositório

### 6. Verificar Logs Completos

No Netlify, durante o build:
1. Clique no deploy que falhou
2. Role até **"build.command from netlify.toml"**
3. Veja a mensagem de erro completa
4. Verifique o caminho: `/opt/build/repo/frontend/package.json`

## 📋 Checklist de Verificação

- [ ] Repositório conectado: `mateusdfaria/portif-lio`
- [ ] Branch: `main`
- [ ] Base directory: (vazio)
- [ ] Build command: `cd frontend && npm ci && npm run build`
- [ ] Publish directory: `frontend/dist`
- [ ] `package.json` existe no GitHub: https://github.com/mateusdfaria/portif-lio/tree/main/frontend
- [ ] `package-lock.json` existe no GitHub
- [ ] Arquivo `netlify.toml` existe na raiz do repositório
- [ ] Cache limpo antes do deploy

## 🔍 Verificação Rápida

Execute estes comandos para verificar se tudo está correto:

```bash
# Verificar se package.json está no repositório
git ls-files frontend/package.json

# Verificar estrutura do frontend
git ls-files frontend/ | grep -E "\.(json|js|jsx|html)$"

# Verificar se netlify.toml está no repositório
git ls-files netlify.toml
```

Todos devem retornar os arquivos listados.

## 🚨 Se Nada Funcionar

1. **Criar novo site no Netlify:**
   - Delete o site atual (ou crie um novo)
   - Conecte novamente o repositório
   - Configure do zero

2. **Verificar permissões:**
   - O Netlify precisa ter acesso ao repositório
   - Verifique em: GitHub → Settings → Applications → Authorized OAuth Apps

3. **Contatar suporte:**
   - Netlify Support: https://www.netlify.com/support/

---

*Última atualização: Janeiro 2025*

