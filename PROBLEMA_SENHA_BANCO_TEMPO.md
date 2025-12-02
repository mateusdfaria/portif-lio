# 🔐 Por Que a Senha do Banco Dá Erro Depois de um Tempo?

Este documento explica as possíveis causas do erro de senha do banco de dados após um período de funcionamento.

---

## 🔍 Possíveis Causas

### 1. **Expiração de Senha no Cloud SQL** ⚠️ (Mais Comum)

O Google Cloud SQL pode ter políticas de expiração de senha configuradas.

#### Como Verificar:

```bash
# Verificar políticas de senha do usuário
gcloud sql users describe hospicast_user \
  --instance=hospicast-db
```

#### Solução:

```bash
# Redefinir senha (mesma ou nova)
gcloud sql users set-password hospicast_user \
  --instance=hospicast-db \
  --password="NOVA_SENHA_FORTE"

# Atualizar no Cloud Run
gcloud run services update hospicast-backend \
  --platform managed \
  --region southamerica-east1 \
  --update-env-vars DATABASE_URL="postgresql://hospicast_user:NOVA_SENHA_FORTE@/hospicast?host=/cloudsql/hospicast-prod:southamerica-east1:hospicast-db"
```

---

### 2. **Pool de Conexões com Conexões Antigas** 🔄

O aplicativo pode estar usando conexões antigas do pool que foram invalidadas.

#### Sintomas:
- Erro aparece após algumas horas/dias
- Reiniciar o serviço resolve temporariamente
- Erro: "password authentication failed"

#### Solução: Implementar Pool de Conexões com Reconnect

Criar um gerenciador de conexões que detecta conexões inválidas:

```python
# backend/core/database.py - Adicionar função de reconnect
import time
from psycopg2 import pool, OperationalError

# Pool de conexões (se ainda não existir)
connection_pool = None

def get_database_connection_with_retry(max_retries=3, retry_delay=1):
    """Obtém conexão com retry automático."""
    global connection_pool
    
    for attempt in range(max_retries):
        try:
            if connection_pool is None or connection_pool.closed:
                # Recriar pool se necessário
                connection_pool = psycopg2.pool.SimpleConnectionPool(
                    1, 20,  # min, max connections
                    user=user,
                    password=password,
                    database=database,
                    host=host,
                    port=port
                )
            
            conn = connection_pool.getconn()
            # Testar conexão
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return conn
            
        except (OperationalError, psycopg2.InterfaceError) as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                connection_pool = None  # Forçar recriação
                continue
            raise ConnectionError(f"Erro ao conectar após {max_retries} tentativas: {e}")
```

---

### 3. **Caracteres Especiais na Senha Corrompidos** 🔤

Se a senha contém caracteres especiais, eles podem ser corrompidos na URL.

#### Sintomas:
- Senha funciona no início
- Para de funcionar após algum tempo
- Caracteres especiais na senha (ex: `@`, `#`, `%`, `&`)

#### Solução: URL Encode da Senha

```python
from urllib.parse import quote_plus

# Ao construir DATABASE_URL, fazer encode da senha
password_encoded = quote_plus(password)
DATABASE_URL = f"postgresql://{user}:{password_encoded}@/{database}?host={host}"
```

Ou usar variáveis separadas em vez de URL:

```python
# Em vez de URL, usar parâmetros separados
conn = psycopg2.connect(
    user=user,
    password=password,  # Sem encoding necessário
    database=database,
    host=host,
    port=port
)
```

---

### 4. **Múltiplas Instâncias com Configurações Diferentes** 🔀

Se houver múltiplas revisões do Cloud Run com DATABASE_URL diferentes.

#### Como Verificar:

```bash
# Ver todas as revisões
gcloud run revisions list \
  --service hospicast-backend \
  --region southamerica-east1 \
  --format="table(metadata.name,spec.containers[0].env)"

# Ver qual revisão está recebendo tráfego
gcloud run services describe hospicast-backend \
  --region southamerica-east1 \
  --format="value(status.traffic)"
```

#### Solução:

```bash
# Garantir que todas as revisões usam a mesma senha
# Ou deletar revisões antigas
gcloud run revisions delete REVISION_NAME \
  --region southamerica-east1
```

---

### 5. **Cache de Variáveis de Ambiente** 💾

O Cloud Run pode estar usando cache de variáveis de ambiente antigas.

#### Solução:

```bash
# Forçar atualização explícita
gcloud run services update hospicast-backend \
  --platform managed \
  --region southamerica-east1 \
  --update-env-vars DATABASE_URL="postgresql://hospicast_user:SENHA_ATUAL@/hospicast?host=/cloudsql/hospicast-prod:southamerica-east1:hospicast-db" \
  --revision-suffix=$(date +%s)  # Forçar nova revisão
```

---

### 6. **Timeout de Conexão do Cloud SQL** ⏱️

Conexões inativas podem ser fechadas pelo Cloud SQL.

#### Sintomas:
- Funciona após reiniciar
- Para após período de inatividade
- Erro: "connection closed" ou "password authentication failed"

#### Solução: Configurar Keep-Alive

```python
# Adicionar parâmetros de conexão
conn = psycopg2.connect(
    user=user,
    password=password,
    database=database,
    host=host,
    port=port,
    connect_timeout=10,
    keepalives=1,
    keepalives_idle=30,
    keepalives_interval=10,
    keepalives_count=5
)
```

---

### 7. **Senha Alterada em Outro Lugar** 🔄

A senha pode ter sido alterada manualmente no Cloud SQL Console.

#### Como Verificar:

```bash
# Tentar conectar diretamente
psql "postgresql://hospicast_user:SENHA@/hospicast?host=/cloudsql/hospicast-prod:southamerica-east1:hospicast-db"
```

#### Solução:

Sincronizar a senha em todos os lugares:
1. Cloud SQL
2. Cloud Run (variável de ambiente)
3. GitHub Secrets (se usado)
4. Scripts de deploy

---

## 🛠️ Solução Preventiva: Script de Monitoramento

Criar um script que verifica a conexão periodicamente:

```python
# backend/scripts/check_database_connection.py
import os
import sys
from core.database import get_database_connection

def check_connection():
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        print("✅ Conexão OK")
        return True
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    success = check_connection()
    sys.exit(0 if success else 1)
```

Adicionar ao Cloud Run como health check:

```yaml
# .github/workflows/deploy-cloud-run.yml
- name: Health Check
  run: |
    # Executar health check após deploy
    python backend/scripts/check_database_connection.py
```

---

## 🔧 Solução Definitiva: Implementar Reconnect Automático

Atualizar `backend/core/database.py` para reconectar automaticamente:

```python
import psycopg2
from psycopg2 import pool, OperationalError, InterfaceError
import time
from urllib.parse import urlparse, parse_qs, quote_plus

_connection_pool = None
_max_retries = 3
_retry_delay = 1

def _recreate_pool():
    """Recria o pool de conexões."""
    global _connection_pool
    
    parsed = urlparse(DATABASE_URL)
    user = parsed.username or ""
    password = parsed.password or ""
    database = parsed.path.lstrip("/") or "hospicast"
    query_params = parse_qs(parsed.query)
    host = query_params.get("host", [None])[0]
    port = query_params.get("port", [None])[0] or "5432"
    
    if _connection_pool and not _connection_pool.closed:
        _connection_pool.closeall()
    
    _connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        user=user,
        password=password,
        database=database,
        host=host,
        port=port,
        connect_timeout=10,
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5
    )

def get_database_connection():
    """Retorna uma conexão com retry automático."""
    global _connection_pool
    
    for attempt in range(_max_retries):
        try:
            if _connection_pool is None or _connection_pool.closed:
                _recreate_pool()
            
            conn = _connection_pool.getconn()
            
            # Testar conexão
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            
            conn.cursor_factory = psycopg2.extras.RealDictCursor
            return conn
            
        except (OperationalError, InterfaceError, psycopg2.Error) as e:
            if attempt < _max_retries - 1:
                time.sleep(_retry_delay)
                _connection_pool = None  # Forçar recriação
                continue
            raise ConnectionError(f"Erro ao conectar após {_max_retries} tentativas: {e}")
```

---

## 📋 Checklist de Diagnóstico

Quando o erro aparecer, verifique:

- [ ] **Senha expirou no Cloud SQL?**
  ```bash
  gcloud sql users describe hospicast_user --instance=hospicast-db
  ```

- [ ] **DATABASE_URL está correto no Cloud Run?**
  ```bash
  gcloud run services describe hospicast-backend \
    --region southamerica-east1 \
    --format="value(spec.template.spec.containers[0].env[0].value)"
  ```

- [ ] **Consegue conectar diretamente?**
  ```bash
  psql "postgresql://hospicast_user:SENHA@/hospicast?host=/cloudsql/..."
  ```

- [ ] **Há múltiplas revisões com senhas diferentes?**
  ```bash
  gcloud run revisions list --service hospicast-backend
  ```

- [ ] **Logs mostram erro específico?**
  ```bash
  gcloud run services logs read hospicast-backend --limit 50
  ```

---

## 🎯 Recomendações

1. **Use senhas fortes sem caracteres especiais** (evita problemas de encoding)
2. **Implemente reconnect automático** (resolve maioria dos casos)
3. **Configure health checks** (detecta problemas cedo)
4. **Monitore logs regularmente** (identifica padrões)
5. **Documente mudanças de senha** (evita confusão)

---

## 🚨 Solução Rápida (Quando o Erro Acontecer)

```bash
# 1. Verificar senha atual
gcloud sql users describe hospicast_user --instance=hospicast-db

# 2. Redefinir senha (se necessário)
gcloud sql users set-password hospicast_user \
  --instance=hospicast-db \
  --password="NOVA_SENHA_FORTE_AQUI"

# 3. Atualizar Cloud Run
export DATABASE_URL="postgresql://hospicast_user:NOVA_SENHA_FORTE_AQUI@/hospicast?host=/cloudsql/hospicast-prod:southamerica-east1:hospicast-db"

gcloud run services update hospicast-backend \
  --platform managed \
  --region southamerica-east1 \
  --update-env-vars DATABASE_URL="${DATABASE_URL}"

# 4. Verificar
curl https://hospicast-backend-fbuqwglmsq-rj.a.run.app/
```

---

**💡 Dica**: Se o problema persistir, implemente o pool de conexões com reconnect automático (Solução Definitiva acima).


