# ✅ Testar Conexão com o Banco de Dados

## 🔍 Por que não apareceu nada?

O comando `export` apenas **define** a variável de ambiente. Ele não mostra mensagens - isso é normal!

## ✅ Verificar se a Variável Foi Configurada

```bash
# Ver se a variável existe
echo $DATABASE_URL
```

**Se aparecer a URL, está funcionando!** ✅

## 🧪 Testar a Conexão Real

Agora vamos testar se consegue conectar ao banco:

```bash
# 1. Navegar para o diretório do backend
cd backend

# 2. Verificar se o Python está instalado
python3 --version

# 3. Instalar dependências (se ainda não instalou)
pip3 install -r requirements.txt

# 4. Executar script de inicialização do banco
python3 scripts/init_database.py
```

## 📊 O que Deve Aparecer

Se tudo estiver correto, você verá:

```
🗄️  Inicializando banco de dados (POSTGRESQL)...
✅ Banco de dados inicializado com sucesso!
📊 Tabelas criadas: hospital_accounts, hospital_sessions, hospital_forecasts
📇 Índices criados: idx_sessions_hospital_id, idx_sessions_token, ...
```

## ❌ Se Der Erro

### Erro: "could not connect to server"

**Solução:** Autorize o IP do Cloud Shell no firewall:

```bash
# Autorizar IP do Cloud Shell
gcloud sql instances patch hospicast-db \
    --authorized-networks=$(curl -s ifconfig.me)/32
```

Depois tente novamente:
```bash
python3 scripts/init_database.py
```

### Erro: "password authentication failed"

**Solução:** Verifique se a senha está correta ou resete:

```bash
# Resetar senha do usuário
gcloud sql users set-password hospicast_user \
    --instance=hospicast-db \
    --password=NOVA_SENHA_FORTE

# Depois atualize a variável
export DATABASE_URL="postgresql://hospicast_user:NOVA_SENHA_FORTE@34.39.151.125:5432/hospicast"
```

### Erro: "ModuleNotFoundError: No module named 'psycopg2'"

**Solução:** Instale as dependências:

```bash
cd backend
pip3 install -r requirements.txt
```

### Erro: "No such file or directory: backend"

**Solução:** Você precisa estar no diretório correto. Se você clonou o repositório:

```bash
# Ver onde você está
pwd

# Se estiver na raiz do projeto
cd backend

# Se não tiver o repositório, clone ou faça upload
```

## 📝 Passo a Passo Completo

```bash
# 1. Verificar variável
echo $DATABASE_URL

# 2. Autorizar IP (se necessário)
gcloud sql instances patch hospicast-db \
    --authorized-networks=$(curl -s ifconfig.me)/32

# 3. Ir para o backend
cd backend

# 4. Instalar dependências
pip3 install -r requirements.txt

# 5. Testar conexão
python3 scripts/init_database.py
```

## ✅ Próximo Passo

Depois que o script funcionar e criar as tabelas, você pode continuar com o deploy no Cloud Run!

---

**Execute os comandos acima e me diga o que apareceu!**

