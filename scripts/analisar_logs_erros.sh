#!/bin/bash

# Script para analisar logs e encontrar erros relacionados ao banco de dados

export SERVICE_NAME="hospicast-backend"
export REGION="southamerica-east1"

echo "🔍 Analisando logs para erros de banco de dados..."
echo ""

# 1. Buscar erros de autenticação/password
echo "1️⃣ Erros de autenticação/password (últimas 100 linhas):"
gcloud run services logs read ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --limit 100 2>/dev/null | grep -i "password\|auth\|failed\|error" | head -10 || echo "   Nenhum erro encontrado"
echo ""

# 2. Buscar erros de conexão
echo "2️⃣ Erros de conexão:"
gcloud run services logs read ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --limit 100 2>/dev/null | grep -i "connection\|connect\|timeout\|refused" | head -10 || echo "   Nenhum erro encontrado"
echo ""

# 3. Buscar erros PostgreSQL
echo "3️⃣ Erros PostgreSQL:"
gcloud run services logs read ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --limit 100 2>/dev/null | grep -i "postgres\|psycopg\|database" | head -10 || echo "   Nenhum erro encontrado"
echo ""

# 4. Verificar padrão de reinicializações
echo "4️⃣ Reinicializações (Shutting down):"
SHUTDOWNS=$(gcloud run services logs read ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --limit 200 2>/dev/null | grep -c "Shutting down" || echo "0")
echo "   Total de reinicializações nas últimas 200 linhas: $SHUTDOWNS"
echo ""

# 5. Verificar status do serviço
echo "5️⃣ Status atual do serviço:"
gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(status.conditions[0].status,status.conditions[0].message)" 2>/dev/null || echo "   Não foi possível obter status"
echo ""

# 6. Verificar última revisão
echo "6️⃣ Última revisão ativa:"
gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(status.latestReadyRevisionName,status.latestCreatedRevisionName)" 2>/dev/null
echo ""

echo "✅ Análise concluída!"
echo ""
echo "💡 Interpretação:"
if [ "$SHUTDOWNS" -gt 5 ]; then
  echo "   ⚠️  Muitas reinicializações detectadas"
  echo "   💡 Pode ser:"
  echo "      - Deploys frequentes"
  echo "      - Health check falhando"
  echo "      - Erros não capturados nos logs"
else
  echo "   ✅ Número de reinicializações parece normal"
fi

