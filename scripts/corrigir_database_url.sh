#!/bin/bash

# Script para corrigir DATABASE_URL no Cloud Run
# Resolve erro: password authentication failed for user "hospicast_user"

set -e

export PROJECT_ID="hospicast-prod"
export SERVICE_NAME="hospicast-backend"
export REGION="southamerica-east1"
export DB_USER="hospicast_user"
export DB_NAME="hospicast"
export CONNECTION_NAME="hospicast-prod:southamerica-east1:hospicast-db"

echo "🔧 Corrigindo DATABASE_URL no Cloud Run..."
echo ""

# Verificar DATABASE_URL atual
echo "📋 DATABASE_URL atual:"
CURRENT_DB_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(spec.template.spec.containers[0].env[0].value)" 2>/dev/null || echo "")
if [ -n "$CURRENT_DB_URL" ]; then
  # Ocultar senha na exibição
  echo "$CURRENT_DB_URL" | sed 's/:[^@]*@/:***@/'
else
  echo "   (não encontrado)"
fi

echo ""
echo "💡 Opções:"
echo "   1. Redefinir senha do usuário no Cloud SQL"
echo "   2. Usar senha existente (você precisa saber qual é)"
echo ""
read -p "Escolha uma opção (1 ou 2): " OPTION

case $OPTION in
  1)
    echo ""
    echo "🔑 Redefinindo senha do usuário ${DB_USER}..."
    read -sp "Digite a nova senha: " DB_PASSWORD
    echo ""
    read -sp "Confirme a nova senha: " DB_PASSWORD_CONFIRM
    echo ""
    
    if [ "$DB_PASSWORD" != "$DB_PASSWORD_CONFIRM" ]; then
      echo "❌ Senhas não coincidem!"
      exit 1
    fi
    
    # Redefinir senha no Cloud SQL
    echo ""
    echo "🔄 Atualizando senha no Cloud SQL..."
    gcloud sql users set-password ${DB_USER} \
      --instance=hospicast-db \
      --password="${DB_PASSWORD}" || {
      echo "❌ Erro ao atualizar senha no Cloud SQL"
      exit 1
    }
    echo "✅ Senha atualizada no Cloud SQL"
    ;;
  2)
    echo ""
    read -sp "Digite a senha atual do usuário ${DB_USER}: " DB_PASSWORD
    echo ""
    ;;
  *)
    echo "❌ Opção inválida"
    exit 1
    ;;
esac

# Montar DATABASE_URL
export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@/${DB_NAME}?host=/cloudsql/${CONNECTION_NAME}"

echo ""
echo "🔄 Atualizando DATABASE_URL no Cloud Run..."
gcloud run services update ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --update-env-vars DATABASE_URL="${DATABASE_URL}" || {
  echo "❌ Erro ao atualizar Cloud Run"
  exit 1
}

echo ""
echo "✅ DATABASE_URL atualizado com sucesso!"
echo ""
echo "🧪 Testando conexão..."
sleep 5  # Aguardar alguns segundos para o serviço reiniciar

# Testar endpoint
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format="value(status.url)")

if curl -f -s "${SERVICE_URL}/" > /dev/null; then
  echo "✅ Serviço respondendo corretamente!"
else
  echo "⚠️  Serviço pode estar reiniciando. Verifique os logs:"
  echo "   gcloud run services logs read ${SERVICE_NAME} --region ${REGION} --limit 20"
fi

echo ""
echo "📝 Para verificar os logs:"
echo "   gcloud run services logs read ${SERVICE_NAME} --region ${REGION} --limit 20"


