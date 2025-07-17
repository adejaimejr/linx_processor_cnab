# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [2.0.0] - 2025-07-17

### ✨ Adicionado
- **Geração automática de CSV para boletos antecipados**
  - Extração de dados estruturados: número do documento, valor e data de pagamento
  - Formatação correta de valores (dividido por 1000) e datas (DD/MM/AAAA)
  - Geração automática junto com arquivos `.ret` antecipados
  - Cópia automática para diretórios configurados

### 📁 Novos Arquivos
- `generate_csv_utils.py` - Módulo para geração de CSV
- `FUNCIONALIDADE_CSV.md` - Documentação detalhada da nova funcionalidade
- `CHANGELOG.md` - Histórico de versões

### 🔧 Melhorias
- README atualizado com nova funcionalidade
- Documentação completa da funcionalidade CSV
- Integração não-invasiva com código existente

### 🛠️ Técnico
- Tratamento de encoding UTF-8 e Latin-1
- Validação de dados extraídos
- Tratamento de erros sem interromper processamento principal
- Import condicional para compatibilidade

## [1.0.0] - 2025-04-01

### ✨ Funcionalidades Iniciais
- Processamento automático de arquivos CNAB
- Filtro por códigos de operação
- Backup automático de arquivos originais
- Suporte para Banco do Brasil e Bradesco
- Monitoramento de diretórios
- Geração de relatórios de processamento
- Separação de operações normais e antecipadas
