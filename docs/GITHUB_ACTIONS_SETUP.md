# 🚀 Guia de Configuração do GitHub Actions (CI/CD)

Este guia explica como configurar e ativar o CI/CD no GitHub Actions para o projeto HospiCast.

## ✅ O que já está configurado

O projeto já possui dois workflows configurados:

1. **`.github/workflows/ci.yml`** - Pipeline de CI (Integração Contínua)
2. **`.github/workflows/deploy.yml`** - Pipeline de Deploy (Entrega Contínua)

## 📋 Passo a Passo para Ativar

### 1. Adicionar os arquivos ao repositório

Os arquivos de workflow já estão criados. Você precisa commitá-los:

```bash
git add .github/workflows/
git commit -m "ci: Adiciona workflows de CI/CD"
git push origin main
```

### 2. Verificar no GitHub

1. Acesse seu repositório: https://github.com/mateusdfaria/portif-lio
2. Vá em **Actions** (menu superior)
3. Você verá os workflows listados:
   - **CI** - Executa em cada push/PR
   - **Deploy** - Executa em push para main ou tags

### 3. Ativar os workflows

Os workflows são **ativados automaticamente** quando você faz push dos arquivos `.github/workflows/*.yml` para o repositório.

**Não é necessário ativar manualmente!** O GitHub Actions detecta automaticamente os arquivos YAML na pasta `.github/workflows/`.

## 🔍 Verificando se está funcionando

### Teste o CI

1. Faça uma pequena alteração em qualquer arquivo
2. Faça commit e push:
   ```bash
   git add .
   git commit -m "test: Testa CI/CD"
   git push origin main
   ```
3. Acesse a aba **Actions** no GitHub
4. Você verá o workflow **CI** executando

### Verificar execução

- ✅ **Verde** = Todos os testes passaram
- ❌ **Vermelho** = Algum teste falhou (clique para ver detalhes)
- 🟡 **Amarelo** = Em execução

## ⚙️ Configuração dos Workflows

### CI Workflow (`.github/workflows/ci.yml`)

**Quando executa:**
- Push para branch `main`
- Pull Requests

**O que faz:**
- ✅ Instala dependências (backend e frontend)
- ✅ Executa linting (Ruff, ESLint)
- ✅ Executa testes (pytest, Vitest)
- ✅ Verifica qualidade de código

### Deploy Workflow (`.github/workflows/deploy.yml`)

**Quando executa:**
- Push para branch `main`
- Tags que começam com `v*` (ex: `v1.0.0`)
- Manualmente via `workflow_dispatch`

**O que faz:**
- ✅ Executa todos os testes
- ✅ Build do frontend
- ✅ Build das imagens Docker
- ✅ Deploy para produção (quando configurado)
- ✅ Cria release (quando é tag)

## 🔐 Secrets (Variáveis Secretas)

Se precisar usar variáveis secretas (ex: chaves de API, senhas), configure em:

1. Repositório → **Settings** → **Secrets and variables** → **Actions**
2. Clique em **New repository secret**
3. Adicione o nome e valor

**Exemplo de secrets úteis:**
- `VITE_API_BASE_URL` - URL da API em produção
- `DOCKER_HUB_USERNAME` - Usuário do Docker Hub
- `DOCKER_HUB_TOKEN` - Token do Docker Hub
- `DEPLOY_KEY` - Chave SSH para deploy

## 📊 Badges de Status

Adicione badges ao README para mostrar o status do CI:

```markdown
![CI](https://github.com/mateusdfaria/portif-lio/workflows/CI/badge.svg)
![Deploy](https://github.com/mateusdfaria/portif-lio/workflows/Deploy/badge.svg)
```

## 🐛 Troubleshooting

### Workflow não aparece

- Verifique se os arquivos estão em `.github/workflows/*.yml`
- Verifique se fez push para o repositório
- Verifique se está na branch correta

### Testes falhando

- Clique no workflow que falhou
- Veja os logs detalhados
- Corrija os erros localmente primeiro:
  ```bash
  # Backend
  ruff check backend
  pytest backend/tests/
  
  # Frontend
  cd frontend
  npm run lint
  npm run test
  ```

### Permissões

Se o workflow precisar de permissões especiais:
1. Vá em **Settings** → **Actions** → **General**
2. Configure as permissões necessárias

## 📝 Próximos Passos

### Para Deploy Real

1. Configure um servidor de produção
2. Adicione secrets necessários
3. Atualize o step "Deploy to production" no `deploy.yml` com seus comandos:
   - Docker Compose
   - Kubernetes
   - SSH/rsync
   - Cloud providers (AWS, Azure, GCP)

### Exemplo de Deploy com Docker

```yaml
- name: Deploy to production
  run: |
    docker-compose -f docker-compose.prod.yml up -d --build
```

### Exemplo de Deploy com SSH

```yaml
- name: Deploy via SSH
  uses: appleboy/ssh-action@master
  with:
    host: ${{ secrets.HOST }}
    username: ${{ secrets.USERNAME }}
    key: ${{ secrets.SSH_KEY }}
    script: |
      cd /app
      git pull
      docker-compose up -d --build
```

## ✅ Checklist de Ativação

- [x] Arquivos `.github/workflows/*.yml` criados
- [ ] Arquivos commitados e enviados ao GitHub
- [ ] Workflows aparecem na aba Actions
- [ ] CI executa automaticamente em push
- [ ] Testes passam no CI
- [ ] Badges adicionados ao README (opcional)
- [ ] Secrets configurados (se necessário)
- [ ] Deploy configurado (quando necessário)

---

**Status atual**: ✅ Workflows configurados e prontos para uso!

*Última atualização: Janeiro 2025*

