#!/bin/bash

# Script para verificar configuração completa do banco de dados

set -e

export PROJECT_ID="hospicast-prod"
export SERVICE_NAME="hospicast-backend"
export REGION="southamerica-east1"
export DB_USER="hospicast_user"
export INSTANCE_NAME="hospicast-db"

echo "🔍 Verificando configuração completa do banco de dados..."
echo ""

# 1. Informações do usuário
echo "1️⃣ Informações do usuário:"
gcloud sql users describe ${DB_USER} \
  --instance=${INSTANCE_NAME}
echo ""

# 2. Configurações da instância (pode ter políticas de senha)
echo "2️⃣ Configurações da instância:"
gcloud sql instances describe ${INSTANCE_NAME} \
  --format="yaml(settings)" | grep -i "password\|expir\|policy" || echo "   (Nenhuma política de senha encontrada)"
echo ""

# 3. DATABASE_URL no Cloud Run
echo "3️⃣ DATABASE_URL configurado no Cloud Run:"
CURRENT_DB_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(spec.template.spec.containers[0].env[0].value)" 2>/dev/null || echo "")

if [ -n "$CURRENT_DB_URL" ]; then
  # Ocultar senha na exibição
  echo "$CURRENT_DB_URL" | sed 's/:[^@]*@/:***@/'
  
  # Extrair informações da URL
  if echo "$CURRENT_DB_URL" | grep -q "hospicast_user"; then
    echo "   ✅ Usuário correto na URL"
  else
    echo "   ⚠️  Usuário diferente na URL"
  fi
  
  if echo "$CURRENT_DB_URL" | grep -q "/cloudsql/"; then
    echo "   ✅ Usando Cloud SQL socket (correto)"
  else
    echo "   ⚠️  Não está usando Cloud SQL socket"
  fi
else
  echo "   ❌ DATABASE_URL não encontrado!"
fi
echo ""

# 4. Verificar todas as variáveis de ambiente
echo "4️⃣ Todas as variáveis de ambiente no Cloud Run:"
gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="yaml(spec.template.spec.containers[0].env)" | head -20
echo ""

# 5. Verificar logs recentes para erros
echo "5️⃣ Últimos erros nos logs (últimas 20 linhas):"
gcloud run services logs read ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --limit 20 2>/dev/null | grep -i "error\|fail\|password\|auth" || echo "   Nenhum erro encontrado"
echo ""

# 6. Verificar revisões ativas
echo "6️⃣ Revisões do Cloud Run:"
gcloud run revisions list \
  --service ${SERVICE_NAME} \
  --region ${REGION} \
  --format="table(metadata.name,status.conditions[0].status,spec.containers[0].env[0].value)" 2>/dev/null | head -5
echo ""

echo "✅ Verificação concluída!"
echo ""
echo "💡 Próximos passos:"
echo "   1. Se a senha está incorreta, use: ./scripts/corrigir_database_url.sh"
echo "   2. Se o problema é conexão, verifique os logs detalhados"
echo "   3. Considere implementar reconnect automático"


