# 🔍 Interpretar Logs do Cloud Run

## 📋 Comando para Ver Logs

```bash
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 100
```

## 🔍 O que Procurar nos Logs

### ✅ Logs Normais (Sucesso)

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### ❌ Erros Comuns

#### 1. Erro de Importação
```
ModuleNotFoundError: No module named 'X'
ImportError: cannot import name 'X'
```
**Solução**: Adicionar dependência ao `requirements.txt` e fazer rebuild

#### 2. Erro de Conexão com Banco
```
psycopg2.OperationalError: could not connect to server
ConnectionError: Erro ao conectar ao PostgreSQL
```
**Solução**: Verificar se DATABASE_URL está correta e se Cloud SQL está acessível

#### 3. Erro de CmdStan
```
cmdstanpy.install_cmdstan failed
```
**Solução**: Já corrigido - CmdStan é instalado no Dockerfile, não na inicialização

#### 4. Erro de Porta
```
Address already in use
Port 8080 is not available
```
**Solução**: Já corrigido - usando PORT do Cloud Run

#### 5. Timeout
```
Container failed to start within timeout
```
**Solução**: Aumentar timeout ou verificar se há processos bloqueando

## 📊 Ver Logs em Tempo Real

```bash
# Ver logs em tempo real (follow)
gcloud run services logs read hospicast-backend \
    --platform managed \
    --region southamerica-east1 \
    --limit 50 \
    --follow
```

## 🔗 Ver Logs no Console Web

Acesse o link que apareceu no erro ou:
```
https://console.cloud.google.com/logs/viewer?project=hospicast-prod&resource=cloud_run_revision
```

## ✅ Depois de Ver os Logs

Me envie os logs (especialmente as linhas com "ERROR" ou "Traceback") para eu identificar o problema específico e corrigir.

---

**Execute o comando e me envie os logs, especialmente as partes com erro!**

