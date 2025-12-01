# 🔍 Configuração do SonarCloud

Este guia mostra como configurar o SonarCloud para análise de qualidade de código no projeto HospiCast.

---

## 📋 Pré-requisitos

1. Conta no [SonarCloud](https://sonarcloud.io) (gratuita)
2. Repositório no GitHub
3. Acesso para configurar GitHub Secrets

---

## 🚀 Passo a Passo

### 1. Criar Conta no SonarCloud

1. Acesse: https://sonarcloud.io
2. Clique em **"Log in"** e faça login com sua conta GitHub
3. Autorize o SonarCloud a acessar seus repositórios

### 2. Criar Organização

1. No SonarCloud, clique em **"Create Organization"**
2. Escolha **"Free Plan"**
3. Selecione seus repositórios do GitHub
4. Anote o nome da organização (ex: `seu-usuario-github`)

### 3. Adicionar Projetos

O SonarCloud pode detectar automaticamente os projetos, ou você pode criar manualmente:

1. Vá em **"Projects"** → **"Add Project"**
2. Selecione **"From GitHub"**
3. Escolha o repositório `portif-lio`
4. O SonarCloud criará automaticamente:
   - `hospicast-backend` (Python)
   - `hospicast-frontend` (JavaScript)

### 4. Obter Token do SonarCloud

1. No SonarCloud, vá em **"My Account"** → **"Security"**
2. Em **"Generate Tokens"**, crie um novo token
3. Nome: `GitHub Actions`
4. **Copie o token** (você só verá uma vez!)

### 5. Configurar GitHub Secrets

1. No GitHub, vá em: **Settings** → **Secrets and variables** → **Actions**
2. Clique em **"New repository secret"**
3. Adicione:
   - **Name**: `SONAR_TOKEN`
   - **Value**: Cole o token do SonarCloud
4. Clique em **"Add secret"**

### 6. Atualizar Configurações dos Projetos

Edite os arquivos `sonar-project.properties`:

#### Backend (`backend/sonar-project.properties`)

```properties
sonar.organization=seu-org-sonarcloud  # Substitua pelo nome da sua organização
```

#### Frontend (`frontend/sonar-project.properties`)

```properties
sonar.organization=seu-org-sonarcloud  # Substitua pelo nome da sua organização
```

### 7. Fazer Commit e Push

```bash
git add backend/sonar-project.properties frontend/sonar-project.properties .github/workflows/sonarcloud.yml
git commit -m "feat: adicionar configuração do SonarCloud"
git push origin main
```

### 8. Verificar Análise

1. Vá em **Actions** no GitHub
2. Você verá o workflow **"SonarCloud Analysis"** executando
3. Após concluir, acesse o SonarCloud para ver os resultados

---

## 📊 O que o SonarCloud Analisa

### Backend (Python)
- ✅ Código duplicado
- ✅ Complexidade ciclomática
- ✅ Cobertura de testes
- ✅ Code smells
- ✅ Bugs potenciais
- ✅ Vulnerabilidades de segurança
- ✅ Manutenibilidade

### Frontend (JavaScript/React)
- ✅ Código duplicado
- ✅ Complexidade
- ✅ Cobertura de testes
- ✅ Code smells
- ✅ Bugs
- ✅ Vulnerabilidades
- ✅ Acessibilidade

---

## 🔧 Configurações Avançadas

### Excluir Arquivos da Análise

Edite `sonar.exclusions` nos arquivos `sonar-project.properties`:

```properties
sonar.exclusions=**/__pycache__/**,**/tests/**,**/node_modules/**
```

### Configurar Quality Gates

1. No SonarCloud, vá em **"Quality Gates"**
2. Configure os critérios de qualidade desejados
3. O projeto usará automaticamente o Quality Gate padrão

### Integração com Pull Requests

O workflow já está configurado para:
- ✅ Executar análise em PRs
- ✅ Comentar resultados no PR
- ✅ Bloquear merge se houver problemas críticos (opcional)

---

## 📈 Métricas Importantes

### Coverage (Cobertura)
- **Backend**: Mínimo 75% (já configurado)
- **Frontend**: Mínimo 25% (já configurado)

### Code Smells
- Tente manter abaixo de 50 por projeto

### Bugs
- Zero bugs críticos
- Mínimo de bugs major

### Vulnerabilidades
- Zero vulnerabilidades críticas
- Mínimo de vulnerabilidades major

---

## 🐛 Troubleshooting

### Erro: "Organization not found"

**Solução**: Verifique se o nome da organização em `sonar-project.properties` está correto.

### Erro: "Invalid token"

**Solução**: 
1. Gere um novo token no SonarCloud
2. Atualize o GitHub Secret `SONAR_TOKEN`

### Análise não executa

**Solução**:
1. Verifique se o workflow está habilitado em **Actions**
2. Verifique se o `SONAR_TOKEN` está configurado
3. Veja os logs do workflow para mais detalhes

### Coverage não aparece

**Solução**:
1. Certifique-se de que os testes estão gerando relatórios de coverage
2. Verifique os caminhos em `sonar.python.coverage.reportPaths` (backend)
3. Verifique os caminhos em `sonar.javascript.lcov.reportPaths` (frontend)

---

## 📚 Recursos

- [Documentação SonarCloud](https://docs.sonarcloud.io/)
- [SonarCloud GitHub Action](https://github.com/SonarSource/sonarcloud-github-action)
- [Quality Gates](https://docs.sonarcloud.io/user-guide/quality-gates/)

---

## ✅ Checklist de Configuração

- [ ] Conta criada no SonarCloud
- [ ] Organização criada
- [ ] Projetos adicionados
- [ ] Token gerado
- [ ] GitHub Secret `SONAR_TOKEN` configurado
- [ ] `sonar-project.properties` atualizados com organização correta
- [ ] Workflow commitado e push feito
- [ ] Análise executada com sucesso
- [ ] Resultados visualizados no SonarCloud

---

**🎉 Pronto! Seu projeto agora tem análise de qualidade de código automatizada!**

