# Linx Processor CNAB

Otimizador de arquivos de retorno bancário para o ERP Linx e-millennium.

## 📋 Sobre o Projeto

Os bancos enviam arquivos de retorno (.RET) contendo diversas instruções referentes aos boletos, como:
- Liquidações
- Baixas
- Protestos
- Alterações de vencimento
- Outros eventos

O desafio é que esses arquivos podem conter muitas informações que nem sempre são necessárias para o processamento no ERP Linx e-Millennium, podendo gerar:
- Lentidão na importação
- Erros de processamento
- Dados desnecessários no sistema
- Maior tempo de processamento

### 🎯 Solução

O Linx Processor CNAB foi desenvolvido para solucionar esse problema, permitindo:
- Filtrar apenas as instruções desejadas (ex: somente liquidações)
- Remover informações desnecessárias do arquivo
- Processar arquivos automaticamente assim que são recebidos
- Manter backup dos arquivos originais
- Rastrear todo o processamento realizado
- **Gerar CSV de boletos antecipados** com dados estruturados para análise

### 💡 Benefícios

- **Importação mais Limpa**: Apenas as instruções relevantes são mantidas
- **Maior Performance**: Arquivos menores são processados mais rapidamente
- **Menos Erros**: Redução de falhas na importação do ERP
- **Automatização**: Processamento automático de novos arquivos
- **Segurança**: Backup automático dos arquivos originais
- **Análise de Dados**: Arquivos CSV ou Excel estruturados para boletos antecipados

## 🚀 Começando

### 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

### 🔧 Instalação

1. Clone o repositório
```bash
git clone https://github.com/adejaimejr/linx_processor_cnab.git
cd linx_processor_cnab
```

2. Crie um ambiente virtual e ative-o
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

> **Nota**: Para suporte a arquivos Excel (.xlsx), a biblioteca `openpyxl` será instalada automaticamente.

4. Configure as variáveis de ambiente
```bash
cp .env.example .env
```

### ⚙️ Configuração

Edite o arquivo `.env` com suas configurações:

```ini
# Configurações Banco do Brasil
BB_OPERACAO=06        # Códigos das operações desejadas (separados por vírgula)
BB_ENABLE=true        # Habilita/desabilita processamento
BB_SEPARAR_ANTECIPACAO=true # Habilita separação de arquivos antecipados e geração de CSV

# Configurações Bradesco
BRADESCO_OPERACAO=06  # Códigos das operações desejadas (separados por vírgula)
BRADESCO_ENABLE=true  # Habilita/desabilita processamento
BRADESCO_SEPARAR_ANTECIPACAO=false # Habilita separação de arquivos antecipados

# Configurações Gerais
CHECK_INTERVAL=5      # Intervalo em segundos para verificar novos arquivos
OUTPUT_FORMAT=csv     # Formato de saída para boletos antecipados: csv ou xls
```

### 📋 Códigos de Operação

Os códigos mais comuns são:
- `06`: Liquidação
- `09`: Baixa
- `02`: Entrada Confirmada
- `03`: Entrada Rejeitada

Consulte a documentação do seu banco para outros códigos.

## 📦 Como Usar

1. Coloque os arquivos .RET na pasta `cnab`
2. O sistema automaticamente:
   - Identifica o banco (Bradesco ou Banco do Brasil)
   - Faz backup do arquivo original
   - Filtra apenas as operações configuradas
   - Gera o novo arquivo processado
3. Importe o arquivo processado no e-millennium

### 📄 Arquivos Gerados

Para cada arquivo processado (exemplo: `CBR6432791707202515425.ret`), o sistema gera:
- `CBR6432791707202515425_1234567890.ret` - Backup do arquivo original com timestamp
- `CBR6432791707202515425_1234567890_alterado.ret` - Arquivo filtrado pronto para importação
- `CBR6432791707202515425_1234567890_normal.ret` - Operações normais (se separação habilitada)
- `CBR6432791707202515425_1234567890_antecipado.ret` - Operações antecipadas (se separação habilitada)
- `CBR6432791707202515425_1234567890_antecipado.csv` - **CSV com dados dos boletos antecipados** (se OUTPUT_FORMAT=csv)
- `CBR6432791707202515425_1234567890_antecipado.xlsx` - **Excel com dados dos boletos antecipados** (se OUTPUT_FORMAT=xls)
- `CBR6432791707202515425_relatorio.txt` - **Relatório detalhado do processamento**

#### 📈 Formatos de Saída Disponíveis

##### CSV (OUTPUT_FORMAT=csv)
O arquivo CSV contém os seguintes campos:
- **n_documento**: Número do documento
- **valor**: Valor do boleto formatado como XXX,YY
- **data_pagamento**: Data de vencimento no formato DD/MM/AAAA

```csv
n_documento,valor,data_pagamento
91033-E,"845,95",24/04/2025
91058-E,"607,95",24/04/2025
91124-E,"494,97",24/04/2025
```

##### Excel/XLS (OUTPUT_FORMAT=xls)
O arquivo Excel (.xlsx) oferece formatação profissional com:
- **Formatação de moeda**: Valores exibidos como R$ 845,95
- **Cabeçalho destacado**: Fundo cinza e texto em negrito
- **Bordas**: Melhor visualização dos dados
- **Filtragem automática**: Remove headers/trailers automaticamente
- **Validação rigorosa**: Apenas títulos válidos são exportados

**Campos do Excel:**
- **Número do Documento**: Identificação do boleto
- **Valor**: Formatado como moeda brasileira (R$ #.##0,00)
- **Data de Pagamento**: Data no formato DD/MM/AAAA

#### 📊 Relatórios de Processamento

O sistema gera automaticamente relatórios detalhados para cada arquivo processado:

**Nome do relatório:** `<nome_arquivo>_relatorio.txt`

**Conteúdo do relatório:**
- 📊 **Estatísticas de processamento**: Total de registros, válidos, inválidos e mantidos
- 📁 **Arquivos gerados**: Lista completa de todos os arquivos criados
- 🏦 **Informações do banco**: Banco detectado e configurações aplicadas
- 📝 **Detalhamento por operação**: Contadores por tipo de operação processada
- 📅 **Timestamp**: Data e hora do processamento

**Localização dos relatórios:**
- 📁 **Local**: `reports/`
- 🌐 **Rede**: Copiado automaticamente para o diretório de saída configurado

**Exemplo de relatório:**
```
================================================================================
RELATÓRIO DE PROCESSAMENTO CNAB - 2025-01-18 10:15:30
================================================================================

🏦 BANCO DETECTADO: BB

📊 ESTATÍSTICAS DE PROCESSAMENTO:
  • Total de linhas: 31
  • Registros válidos (dados): 29 (100.00%)
  • Registros inválidos: 0 (0.00%)
  • Registros mantidos: 29 (100.00%)

📁 ARQUIVOS GERADOS (5 arquivos):
  • CBR6432791707202515425_20250118101530.ret (1.2 KB)
  • CBR6432791707202515425_20250118101530_alterado.ret (1.1 KB)
  • CBR6432791707202515425_20250118101530_normal.ret (0.8 KB)
  • CBR6432791707202515425_20250118101530_antecipado.ret (0.4 KB)
  • CBR6432791707202515425_20250118101530_antecipado.csv (0.2 KB)
```

## 🛠️ Tecnologias

* [Python](https://www.python.org/) - Linguagem de programação
* [python-dotenv](https://pypi.org/project/python-dotenv/) - Gerenciamento de configurações
* [openpyxl](https://pypi.org/project/openpyxl/) - Geração de arquivos Excel (opcional)

## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE.md](LICENSE.md) para detalhes

## ✨ Como Contribuir

1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature (`git checkout -b feature/AmazingFeature`)
3. Adicione suas mudanças (`git add .`)
4. Comite suas mudanças (`git commit -m 'Add some AmazingFeature'`)
5. Faça o Push da Branch (`git push origin feature/AmazingFeature`)
6. Abra um Pull Request

## 📞 Suporte

Para suporte, abra uma issue no repositório ou entre em contato com os mantenedores.