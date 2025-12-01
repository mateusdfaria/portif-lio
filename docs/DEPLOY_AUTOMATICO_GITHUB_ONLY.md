# 🚀 Deploy Automático - Apenas GitHub

## 📋 O que foi criado

Foi criado um workflow do GitHub Actions (`.github/workflows/deploy-github-container-registry.yml`) que:

1. ✅ Faz build da imagem Docker do backend
2. ✅ Faz push para **GitHub Container Registry** (ghcr.io)
3. ✅ Funciona automaticamente quando você faz push no branch `main`
4. ✅ Não precisa de configuração externa (usa token do próprio GitHub)

## ✅ Como Funciona

### Quando é acionado:
- ✅ Push no branch `main` (com mudanças no `backend/`)
- ✅ Pull Request para `main`
- ✅ Manualmente via "Run workflow" no GitHub

### O que faz:
1. Faz checkout do código
2. Configura Docker Buildx
3. Faz login no GitHub Container Registry (usa token automático)
4. Faz build da imagem Docker
5. Faz push da imagem para `ghcr.io`
6. Cria tags automáticas (latest, sha, branch, etc.)

## 📦 Acessar a Imagem

Após o workflow executar, a imagem estará disponível em:

```
ghcr.io/mateusdfaria/portif-lio/hospicast-backend:latest
```

### Ver imagens no GitHub:
1. Ir para: https://github.com/mateusdfaria/portif-lio/pkgs/container/hospicast-backend
2. Você verá todas as versões/tags da imagem

## 🔧 Usar a Imagem

### Opção 1: Usar em qualquer plataforma Docker

A imagem pode ser usada em qualquer plataforma que suporte Docker:

```bash
# Fazer pull da imagem
docker pull ghcr.io/mateusdfaria/portif-lio/hospicast-backend:latest

# Executar localmente
docker run -p 8080:8080 \
  -e DATABASE_URL="sua_url" \
  -e API_ALLOWED_ORIGINS="*" \
  ghcr.io/mateusdfaria/portif-lio/hospicast-backend:latest
```

### Opção 2: Usar em Cloud Run (Google Cloud)

```bash
# Fazer pull e push para GCR (se necessário)
docker pull ghcr.io/mateusdfaria/portif-lio/hospicast-backend:latest
docker tag ghcr.io/mateusdfaria/portif-lio/hospicast-backend:latest gcr.io/hospicast-prod/hospicast-backend:latest
docker push gcr.io/hospicast-prod/hospicast-backend:latest

# Deploy no Cloud Run
gcloud run deploy hospicast-backend \
  --image gcr.io/hospicast-prod/hospicast-backend:latest \
  --region southamerica-east1
```

### Opção 3: Usar em Railway/Render/Fly.io

Essas plataformas podem fazer pull direto do GitHub Container Registry:

```yaml
# Exemplo para Railway
image: ghcr.io/mateusdfaria/portif-lio/hospicast-backend:latest
```

## 🔐 Permissões

O workflow usa automaticamente o `GITHUB_TOKEN` do GitHub Actions, então **não precisa configurar nenhum secret adicional**!

### Se precisar fazer pull da imagem em outro lugar:

1. Criar Personal Access Token no GitHub:
   - Ir para: https://github.com/settings/tokens
   - Criar token com permissão `read:packages`

2. Fazer login:
   ```bash
   echo $GITHUB_TOKEN | docker login ghcr.io -u SEU_USUARIO --password-stdin
   ```

## 📋 Verificar se Está Funcionando

### 1. Ver Workflows

1. Ir para: https://github.com/mateusdfaria/portif-lio/actions
2. Você verá o workflow "Build and Push to GitHub Container Registry"
3. Clicar para ver os logs

### 2. Ver Imagens

1. Ir para: https://github.com/mateusdfaria/portif-lio/pkgs/container/hospicast-backend
2. Você verá todas as versões da imagem

### 3. Testar Localmente

```bash
# Fazer pull da imagem
docker pull ghcr.io/mateusdfaria/portif-lio/hospicast-backend:latest

# Executar
docker run -p 8080:8080 \
  -e DATABASE_URL="postgresql://user:pass@host/db" \
  -e API_ALLOWED_ORIGINS="*" \
  ghcr.io/mateusdfaria/portif-lio/hospicast-backend:latest
```

## 🎯 Próximos Passos

Após o workflow executar com sucesso:

1. ✅ A imagem estará disponível no GitHub Container Registry
2. ✅ Você pode usar essa imagem em qualquer plataforma
3. ✅ Cada push cria uma nova versão da imagem

### Para fazer deploy automático em uma plataforma específica:

Você pode adicionar um step adicional no workflow para fazer deploy automático em:
- Railway
- Render
- Fly.io
- Cloud Run
- Qualquer outra plataforma

---

**Faça um push no branch main para testar o workflow!**



