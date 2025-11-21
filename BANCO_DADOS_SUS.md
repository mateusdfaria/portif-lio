# 💾 Banco de Dados SUS - HospiCast

## 📋 Resumo

Foi implementado um sistema de persistência em banco de dados SQLite para salvar:
- **Hospitais públicos de Joinville** (dados cadastrais)
- **Dados SUS** (ocupação, pacientes, procedimentos, etc.)

## 🗄️ Estrutura do Banco

### Arquivo
- **Localização**: `backend/data/joinville_sus.db`
- **Tipo**: SQLite3

### Tabelas

#### 1. `hospitals`
Armazena informações dos hospitais públicos de Joinville.

**Campos:**
- `cnes` (TEXT, PRIMARY KEY) - Código CNES do hospital
- `nome` (TEXT) - Nome do hospital
- `endereco` (TEXT) - Endereço completo
- `telefone` (TEXT) - Telefone de contato
- `tipo_gestao` (TEXT) - Tipo de gestão (Municipal, Estadual)
- `capacidade_total` (INTEGER) - Total de leitos
- `capacidade_uti` (INTEGER) - Leitos de UTI
- `capacidade_emergencia` (INTEGER) - Leitos de emergência
- `especialidades` (TEXT) - JSON array com especialidades
- `latitude` (REAL) - Coordenada latitude
- `longitude` (REAL) - Coordenada longitude
- `municipio` (TEXT) - Município
- `uf` (TEXT) - Unidade Federativa
- `created_at` (TEXT) - Data de criação
- `updated_at` (TEXT) - Data de atualização

#### 2. `sus_data`
Armazena dados diários de cada hospital.

**Campos:**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `cnes` (TEXT, FOREIGN KEY) - Referência ao hospital
- `data` (TEXT) - Data do registro (YYYY-MM-DD)
- `ocupacao_leitos` (REAL) - Taxa de ocupação geral (0.0 a 1.0)
- `ocupacao_uti` (REAL) - Taxa de ocupação UTI (0.0 a 1.0)
- `ocupacao_emergencia` (REAL) - Taxa de ocupação emergência (0.0 a 1.0)
- `pacientes_internados` (INTEGER) - Número de pacientes internados
- `pacientes_uti` (INTEGER) - Número de pacientes na UTI
- `pacientes_emergencia` (INTEGER) - Número de pacientes na emergência
- `admissoes_dia` (INTEGER) - Admissões do dia
- `altas_dia` (INTEGER) - Altas do dia
- `procedimentos_realizados` (INTEGER) - Procedimentos realizados
- `tempo_espera_medio` (REAL) - Tempo médio de espera (minutos)
- `taxa_ocupacao` (REAL) - Taxa geral de ocupação
- `created_at` (TEXT) - Data de criação do registro
- **UNIQUE(cnes, data)** - Um registro por hospital por dia

**Índices:**
- `idx_sus_data_cnes` - Índice em `cnes`
- `idx_sus_data_date` - Índice em `data`
- `idx_sus_data_cnes_date` - Índice composto em `(cnes, data)`

## 🔧 Funcionalidades

### Inicialização Automática
O banco é criado automaticamente na primeira importação do módulo `joinville_sus_database`.

### Hospitais

#### Salvar Hospital
```python
from services.joinville_sus_database import save_hospital, HospitalRecord

hospital = HospitalRecord(
    cnes="1234567",
    nome="Hospital Municipal São José",
    endereco="Rua Dr. Plácido Gomes, 488",
    telefone="(47) 3441-6666",
    tipo_gestao="Municipal",
    capacidade_total=200,
    capacidade_uti=20,
    capacidade_emergencia=50,
    especialidades=["Urgência", "Internação", "UTI"],
    latitude=-26.3044,
    longitude=-48.8456,
    municipio="Joinville",
    uf="SC"
)

save_hospital(hospital)
```

#### Buscar Todos os Hospitais
```python
from services.joinville_sus_database import get_all_hospitals

hospitals = get_all_hospitals()
for hospital in hospitals:
    print(f"{hospital.nome} - {hospital.cnes}")
```

#### Buscar Hospital por CNES
```python
from services.joinville_sus_database import get_hospital_by_cnes

hospital = get_hospital_by_cnes("1234567")
if hospital:
    print(f"Hospital encontrado: {hospital.nome}")
```

### Dados SUS

#### Salvar Dados SUS
```python
from services.joinville_sus_database import save_sus_data, SusDataRecord

data = SusDataRecord(
    cnes="1234567",
    data="2025-01-21",
    ocupacao_leitos=0.85,
    ocupacao_uti=0.90,
    ocupacao_emergencia=0.75,
    pacientes_internados=170,
    pacientes_uti=18,
    pacientes_emergencia=38,
    admissoes_dia=25,
    altas_dia=23,
    procedimentos_realizados=35,
    tempo_espera_medio=45.5,
    taxa_ocupacao=0.85
)

save_sus_data(data)
```

#### Salvar Múltiplos Dados
```python
from services.joinville_sus_database import save_multiple_sus_data

data_list = [data1, data2, data3, ...]
save_multiple_sus_data(data_list)
```

#### Buscar Dados SUS
```python
from services.joinville_sus_database import get_sus_data

# Buscar dados de um hospital no período
data = get_sus_data(
    cnes="1234567",
    start_date="2025-01-01",
    end_date="2025-01-31"
)

for record in data:
    print(f"{record.data}: {record.ocupacao_leitos*100:.1f}% ocupação")
```

#### Verificar se Existem Dados
```python
from services.joinville_sus_database import has_sus_data

if has_sus_data("1234567", "2025-01-01", "2025-01-31"):
    print("Dados encontrados no banco!")
else:
    print("Gerando novos dados...")
```

## 🔄 Fluxo de Dados

### 1. Primeira Execução
1. Sistema tenta carregar hospitais do banco → **Não encontra**
2. Cria hospitais padrão em memória
3. **Salva hospitais no banco**
4. Quando busca dados SUS → **Não encontra no banco**
5. Gera dados baseados em padrões SUS
6. **Salva dados gerados no banco**

### 2. Execuções Subsequentes
1. Sistema carrega hospitais do banco → **Encontra**
2. Quando busca dados SUS → **Busca primeiro no banco**
3. Se encontrar no banco → **Retorna dados salvos**
4. Se não encontrar → **Gera novos dados e salva**

### 3. Dados Reais do SUS
1. Sistema tenta buscar dados reais via API do Datasus
2. Se conseguir → **Salva no banco**
3. Se não conseguir → **Gera dados e salva**

## 📊 Vantagens

✅ **Persistência**: Dados não são perdidos ao reiniciar o servidor
✅ **Performance**: Dados salvos são retornados instantaneamente
✅ **Consistência**: Mesmos dados para mesmas consultas
✅ **Histórico**: Mantém histórico de dados ao longo do tempo
✅ **Eficiência**: Evita gerar dados desnecessariamente

## 🛠️ Manutenção

### Localização do Banco
```
backend/data/joinville_sus.db
```

### Backup
```bash
# Fazer backup
cp backend/data/joinville_sus.db backend/data/joinville_sus.db.backup

# Restaurar backup
cp backend/data/joinville_sus.db.backup backend/data/joinville_sus.db
```

### Limpar Dados Antigos
```python
import sqlite3
from pathlib import Path

DB_PATH = Path("backend/data/joinville_sus.db")

# Conectar ao banco
conn = sqlite3.connect(DB_PATH)

# Deletar dados antigos (exemplo: mais de 1 ano)
conn.execute("""
    DELETE FROM sus_data 
    WHERE data < date('now', '-1 year')
""")
conn.commit()
conn.close()
```

### Visualizar Dados
```bash
# Usando sqlite3 CLI
sqlite3 backend/data/joinville_sus.db

# Comandos úteis:
.tables                    # Listar tabelas
.schema hospitals          # Ver estrutura da tabela hospitals
.schema sus_data          # Ver estrutura da tabela sus_data
SELECT * FROM hospitals;  # Ver todos os hospitais
SELECT COUNT(*) FROM sus_data;  # Contar registros
```

## 🔍 Troubleshooting

### Banco não está sendo criado
- Verifique permissões na pasta `backend/data/`
- Verifique se o diretório existe: `mkdir -p backend/data`

### Dados não estão sendo salvos
- Verifique logs do servidor para erros
- Verifique se o banco está sendo inicializado: `init_database()`

### Hospitais não aparecem
- Verifique se os hospitais foram salvos: `SELECT * FROM hospitals;`
- Reinicie o servidor para forçar recriação dos hospitais padrão

### Dados duplicados
- O banco usa `UNIQUE(cnes, data)` para evitar duplicatas
- Dados são atualizados com `INSERT OR REPLACE`

## 📝 Notas

- O banco é criado automaticamente na primeira execução
- Dados são salvos automaticamente quando gerados ou buscados
- Hospitais padrão são criados automaticamente se não existirem
- O banco é SQLite, não requer servidor separado
- Ideal para desenvolvimento e produção pequena/média

---

*Última atualização: Janeiro 2025*

