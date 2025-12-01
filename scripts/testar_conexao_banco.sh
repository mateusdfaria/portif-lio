#!/bin/bash
# Script para testar e corrigir conexão com PostgreSQL no Cloud Run

set -e

PROJECT_ID=$(gcloud config get-value project)
REGION="southamerica-east1"
SERVICE_NAME="hospicast-backend"
INSTANCE_NAME="hospicast-db"

echo "🔍 === DIAGNÓSTICO DE CONEXÃO ==="
echo ""

# 1. Verificar DATABASE_URL atual
echo "📋 1. DATABASE_URL atual no Cloud Run:"
CURRENT_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DATABASE_URL')].value)" 2>/dev/null || echo "")

if [ -z "$CURRENT_URL" ]; then
    echo "   ❌ DATABASE_URL não encontrada!"
else
    echo "   $CURRENT_URL"
    # Verificar se tem senha
    if [[ "$CURRENT_URL" == *":@"* ]] || [[ "$CURRENT_URL" == *"://hospicast_user@"* ]]; then
        echo "   ⚠️  PROBLEMA: Senha ausente na URL!"
    fi
fi
echo ""

# 2. Obter connection name
echo "📋 2. Connection Name:"
CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)")
echo "   $CONNECTION_NAME"
echo ""

# 3. Resetar senha
echo "🔐 3. Resetando senha do usuário..."
NEW_PASSWORD="HospiCast2024SenhaForte"
gcloud sql users set-password hospicast_user \
    --instance=$INSTANCE_NAME \
    --password=$NEW_PASSWORD
echo "   ✅ Senha resetada"
echo ""

# 4. Testar conexão local (se possível)
echo "📋 4. Testando formato da URL..."
# URL para Cloud SQL via socket Unix
DATABASE_URL="postgresql://hospicast_user:${NEW_PASSWORD}@/hospicast?host=/cloudsql/${CONNECTION_NAME}"
echo "   URL formatada:"
echo "   $DATABASE_URL"
echo ""

# 5. Verificar se precisa codificar senha
echo "📋 5. Verificando se senha precisa ser codificada..."
# Se a senha tem caracteres especiais, pode precisar de URL encoding
# Mas nossa senha atual não tem, então deve estar OK
echo "   Senha: $NEW_PASSWORD"
echo ""

# 6. Atualizar Cloud Run
echo "🔄 6. Atualizando Cloud Run..."
gcloud run services update $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --update-env-vars "DATABASE_URL=${DATABASE_URL}" \
    --quiet
echo "   ✅ Serviço atualizado"
echo ""

# 7. Aguardar e verificar
echo "⏳ 7. Aguardando 10 segundos..."
sleep 10

echo "📋 8. Verificando DATABASE_URL após atualização:"
UPDATED_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DATABASE_URL')].value)")

if [ -z "$UPDATED_URL" ]; then
    echo "   ❌ DATABASE_URL ainda não encontrada!"
else
    echo "   $UPDATED_URL"
    # Verificar se tem senha agora
    if [[ "$UPDATED_URL" == *":@"* ]] || [[ "$UPDATED_URL" == *"://hospicast_user@"* ]]; then
        echo "   ⚠️  PROBLEMA: Senha ainda ausente!"
        echo ""
        echo "   💡 Tentando método alternativo..."
        # Tentar com --set-env-vars em vez de --update-env-vars
        gcloud run services update $SERVICE_NAME \
            --platform managed \
            --region $REGION \
            --set-env-vars "DATABASE_URL=${DATABASE_URL},API_ALLOWED_ORIGINS=*,LOG_LEVEL=INFO,PROMETHEUS_ENABLED=true,ENVIRONMENT=production" \
            --quiet
        echo "   ✅ Tentativa com --set-env-vars concluída"
    else
        echo "   ✅ Senha presente na URL!"
    fi
fi
echo ""

echo "🎯 === PRÓXIMOS PASSOS ==="
echo "1. Aguarde 2 minutos para o Cloud Run reiniciar"
echo "2. Teste o endpoint:"
echo "   curl -X POST https://hospicast-backend-fbuqwglmsq-rj.a.run.app/hospital-access/register \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"display_name\": \"Hospital Teste\", \"password\": \"senha123\"}'"
echo ""

