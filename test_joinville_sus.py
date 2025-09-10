#!/usr/bin/env python3
"""
Script de teste para APIs dos Hospitais SUS de Joinville
"""
import requests
import json
from datetime import datetime, timedelta

# Configuração
API_BASE_URL = "http://localhost:8000"
START_DATE = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
END_DATE = datetime.now().strftime("%Y-%m-%d")

def test_api_endpoint(endpoint, description):
    """Testa um endpoint da API"""
    print(f"\n🔍 Testando: {description}")
    print(f"   URL: {API_BASE_URL}{endpoint}")
    
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Dados: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}...")
            return data
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   📝 Erro: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erro de conexão: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"   ❌ Erro de JSON: {e}")
        return None

def main():
    """Executa todos os testes dos Hospitais SUS de Joinville"""
    print("🏥 Testando APIs dos Hospitais Públicos de Joinville - SUS")
    print("=" * 70)
    print("📝 Inclui: Hospital Municipal São José, Hospital Infantil Dr. Jeser Amarante Faria, Hospital Regional Hans Dieter Schmidt")
    print("=" * 70)
    
    # 1. Lista de hospitais
    hospitals_data = test_api_endpoint("/joinville-sus/hospitals", "Lista de Hospitais SUS")
    
    if not hospitals_data:
        print("❌ Não foi possível carregar hospitais. Verifique se o backend está rodando.")
        return
    
    hospitals = hospitals_data.get('hospitals', [])
    if not hospitals:
        print("❌ Nenhum hospital encontrado.")
        return
    
    # 2. Informações de cada hospital
    for hospital in hospitals:
        cnes = hospital.get('cnes')
        nome = hospital.get('nome')
        
        print(f"\n🏥 Testando Hospital: {nome}")
        print("-" * 50)
        
        # Informações do hospital
        test_api_endpoint(f"/joinville-sus/hospitals/{cnes}", f"Informações do {nome}")
        
        # Dados SUS
        test_api_endpoint(
            f"/joinville-sus/hospitals/{cnes}/sus-data?start_date={START_DATE}&end_date={END_DATE}", 
            f"Dados SUS do {nome}"
        )
        
        # KPIs SUS
        test_api_endpoint(
            f"/joinville-sus/hospitals/{cnes}/sus-kpis?start_date={START_DATE}&end_date={END_DATE}", 
            f"KPIs SUS do {nome}"
        )
    
    # 3. Resumo geral
    test_api_endpoint(
        f"/joinville-sus/summary?start_date={START_DATE}&end_date={END_DATE}", 
        "Resumo Geral dos Hospitais SUS"
    )
    
    # 4. Capacidade
    test_api_endpoint("/joinville-sus/capacity", "Capacidade dos Hospitais")
    
    # 5. Especialidades
    test_api_endpoint("/joinville-sus/specialties", "Especialidades Disponíveis")
    
    # 6. Alertas
    test_api_endpoint(
        f"/joinville-sus/alerts?start_date={START_DATE}&end_date={END_DATE}", 
        "Alertas dos Hospitais SUS"
    )
    
    print("\n🎯 Testes Concluídos!")
    print("\n📋 Próximos Passos:")
    print("1. Execute o backend: uvicorn main:app --reload")
    print("2. Execute o frontend: npm run dev")
    print("3. Acesse: http://localhost:3000")
    print("4. Clique em 'Hospitais SUS' na navegação")
    print("5. Explore os dados reais dos hospitais públicos de Joinville")
    
    print("\n🏥 Hospitais Disponíveis:")
    for hospital in hospitals:
        icon = "👶" if "Infantil" in hospital['nome'] else "🏥"
        print(f"   {icon} {hospital['nome']} ({hospital['tipo_gestao']}) - CNES: {hospital['cnes']}")
        print(f"     Capacidade: {hospital['capacidade_total']} leitos")
        print(f"     Especialidades: {len(hospital['especialidades'])}")

if __name__ == "__main__":
    main()
