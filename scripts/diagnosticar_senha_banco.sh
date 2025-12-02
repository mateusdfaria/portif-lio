#!/bin/bash

# Script para diagnosticar problemas de senha do banco de dados

set -e

export PROJECT_ID="hospicast-prod"
export SERVICE_NAME="hospicast-backend"
export REGION="southamerica-east1"
export DB_USER="hospicast_user"
export INSTANCE_NAME="hospicast-db"

echo "🔍 Diagnosticando problema de senha do banco de dados..."
echo ""

# 1. Verificar usuário no Cloud SQL
echo "1️⃣ Verificando usuário no Cloud SQL..."
gcloud sql users describe ${DB_USER} \
  --instance=${INSTANCE_NAME} 2>/dev/null || {
  echo "❌ Usuário ${DB_USER} não encontrado!"
  exit 1
}
echo "✅ Usuário encontrado"
echo ""

# 2. Verificar DATABASE_URL atual no Cloud Run
echo "2️⃣ Verificando DATABASE_URL no Cloud Run..."
CURRENT_DB_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(spec.template.spec.containers[0].env[0].value)" 2>/dev/null || echo "")

if [ -z "$CURRENT_DB_URL" ]; then
  echo "❌ DATABASE_URL não encontrado no Cloud Run!"
  exit 1
fi

# Extrair senha da URL (ocultar na exibição)
DB_URL_DISPLAY=$(echo "$CURRENT_DB_URL" | sed 's/:[^@]*@/:***@/')
echo "DATABASE_URL atual: $DB_URL_DISPLAY"
echo ""

# 3. Verificar revisões do Cloud Run
echo "3️⃣ Verificando revisões do Cloud Run..."
REVISIONS=$(gcloud run revisions list \
  --service ${SERVICE_NAME} \
  --region ${REGION} \
  --format="value(metadata.name)" | wc -l)
echo "Total de revisões: $REVISIONS"
echo ""

# 4. Verificar logs recentes
echo "4️⃣ Verificando logs recentes para erros de autenticação..."
ERRORS=$(gcloud run services logs read ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --limit 100 2>/dev/null | grep -i "password\|authentication\|failed" | head -5 || echo "Nenhum erro encontrado")

if [ -n "$ERRORS" ] && [ "$ERRORS" != "Nenhum erro encontrado" ]; then
  echo "⚠️  Erros encontrados nos logs:"
  echo "$ERRORS"
else
  echo "✅ Nenhum erro de autenticação nos logs recentes"
fi
echo ""

# 5. Testar conexão (se possível)
echo "5️⃣ Testando conexão..."
echo "💡 Para testar a conexão, você precisa:"
echo "   1. Redefinir a senha no Cloud SQL"
echo "   2. Atualizar o DATABASE_URL no Cloud Run"
echo ""

# 6. Oferecer soluções
echo "🔧 Soluções possíveis:"
echo ""
echo "Opção 1: Redefinir senha e atualizar Cloud Run"
echo "   ./scripts/corrigir_database_url.sh"
echo ""
echo "Opção 2: Verificar se há múltiplas revisões"
echo "   gcloud run revisions list --service ${SERVICE_NAME} --region ${REGION}"
echo ""
echo "Opção 3: Ver logs detalhados"
echo "   gcloud run services logs read ${SERVICE_NAME} --region ${REGION} --limit 50"
echo ""

# 7. Verificar se há política de expiração
echo "6️⃣ Verificando políticas de senha..."
echo "💡 Cloud SQL pode ter políticas de expiração configuradas"
echo "   Verifique no Console: https://console.cloud.google.com/sql/instances/${INSTANCE_NAME}/users"
echo ""

echo "✅ Diagnóstico concluído!"
echo ""
echo "📋 Resumo:"
echo "   - Usuário: ${DB_USER}"
echo "   - Instância: ${INSTANCE_NAME}"
echo "   - Serviço: ${SERVICE_NAME}"
echo "   - Revisões: ${REVISIONS}"
echo ""
echo "💡 Próximos passos:"
echo "   1. Se a senha expirou, use: ./scripts/corrigir_database_url.sh"
echo "   2. Se o problema persistir, verifique logs detalhados"
echo "   3. Considere implementar reconnect automático (veja PROBLEMA_SENHA_BANCO_TEMPO.md)"


