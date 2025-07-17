# Funcionalidade de Geração de CSV para Boletos Antecipados

## Visão Geral

Esta funcionalidade foi adicionada ao sistema de processamento CNAB para gerar automaticamente arquivos CSV contendo os dados dos boletos antecipados, sem alterar o código existente em produção.

## Como Funciona

### 1. Ativação Automática
- A funcionalidade é ativada automaticamente quando `separar_antecipacao=true` está configurado no `.env`
- Funciona para bancos BB e Bradesco quando a separação de antecipação está habilitada

### 2. Geração do CSV
- Quando um arquivo `.ret` de operações antecipadas é gerado, um CSV correspondente é criado automaticamente
- O CSV tem o mesmo nome do arquivo `.ret`, mas com extensão `.csv`
- Exemplo: `CBR6432212404202515720_antecipado.ret` → `CBR6432212404202515720_antecipado.csv`

### 3. Campos do CSV
O CSV contém os seguintes campos:
- **n_documento**: Número do documento (posições 117-131 do CNAB)
- **valor**: Valor do boleto formatado como XXX,YY (posições 252-267 do CNAB, dividido por 1000)
- **data_pagamento**: Data de vencimento no formato DD/MM/AAAA (posições 111-116 do CNAB)

### 4. Exemplo de Saída
```csv
n_documento,valor,data_pagamento
91033-E,"845,95",24/04/2025
91058-E,"607,95",24/04/2025
91124-E,"494,97",24/04/2025
```

## Arquivos Adicionados

### `generate_csv_utils.py`
Módulo contendo as funções utilitárias para geração de CSV:
- `extract_document_data(linha)`: Extrai dados de uma linha CNAB
- `generate_csv_from_cnab_lines(linhas, output_path)`: Gera CSV a partir de linhas CNAB
- `generate_csv_for_antecipated_operations(arquivo)`: Função principal para gerar CSV

### `test_csv_generation.py`
Script de teste para validar a funcionalidade de geração de CSV.

## Modificações no Código Existente

### `process_cnab.py`
- Adicionado import do módulo `generate_csv_utils`
- Adicionada geração automática de CSV após salvar arquivo antecipado
- Adicionada cópia do CSV para diretórios adicionais configurados

## Configuração

### Arquivo `.env`
Para ativar a funcionalidade, configure:
```env
BB_SEPARAR_ANTECIPACAO=true
# ou
BRADESCO_SEPARAR_ANTECIPACAO=true
```

## Comportamento

### Quando a Funcionalidade é Executada
1. Sistema processa arquivo CNAB
2. Identifica operações antecipadas (tipo '1' na posição 319)
3. Gera arquivo `.ret` com operações antecipadas
4. **AUTOMATICAMENTE** gera arquivo `.csv` correspondente
5. Copia ambos os arquivos para diretórios configurados

### Tratamento de Erros
- Se o módulo `generate_csv_utils` não for encontrado, a funcionalidade é desabilitada silenciosamente
- Erros na geração de CSV são registrados no relatório mas não interrompem o processamento principal
- Mensagens de erro são exibidas no console e incluídas no relatório

### Logs e Relatórios
- Geração de CSV é registrada no console: `📊 CSV antecipado gerado: arquivo.csv (X.XX KB)`
- Informações são incluídas no relatório de processamento
- Arquivos CSV são listados na seção "ARQUIVOS GERADOS" do relatório

## Compatibilidade

- ✅ Não altera funcionalidade existente
- ✅ Funciona com BB e Bradesco
- ✅ Compatível com processamento em lote
- ✅ Suporta múltiplos diretórios de saída
- ✅ Tratamento de encoding UTF-8 e Latin-1

## Teste

Para testar a funcionalidade:
```bash
python test_csv_generation.py
```

## Exemplo de Uso

1. Configure no `.env`:
   ```env
   BB_SEPARAR_ANTECIPACAO=true
   ```

2. Execute o processamento normalmente:
   ```bash
   python process_cnab.py
   ```

3. Os arquivos CSV serão gerados automaticamente junto com os arquivos `.ret` antecipados.

## Notas Importantes

- A funcionalidade só é executada quando há operações antecipadas no arquivo
- O CSV é gerado apenas para operações com tipo '1' (antecipadas)
- Valores são formatados corretamente (divididos por 1000) para exibir centavos
- Datas são convertidas do formato DDMMAA para DD/MM/AAAA
- A funcionalidade é opcional e pode ser desabilitada removendo o módulo `generate_csv_utils.py`
