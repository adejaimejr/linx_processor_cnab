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

### 💡 Benefícios

- **Importação mais Limpa**: Apenas as instruções relevantes são mantidas
- **Maior Performance**: Arquivos menores são processados mais rapidamente
- **Menos Erros**: Redução de falhas na importação do ERP
- **Automatização**: Processamento automático de novos arquivos
- **Segurança**: Backup automático dos arquivos originais

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

# Configurações Bradesco
BRADESCO_OPERACAO=06  # Códigos das operações desejadas (separados por vírgula)
BRADESCO_ENABLE=true  # Habilita/desabilita processamento

# Configurações Gerais
CHECK_INTERVAL=5      # Intervalo em segundos para verificar novos arquivos
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

Para cada arquivo processado (exemplo: `ARQUIVO.RET`), o sistema gera:
- `ARQUIVO_1234567890.RET` - Backup do arquivo original com timestamp
- `ARQUIVO_1234567890_alterado.RET` - Arquivo filtrado pronto para importação

## 🛠️ Tecnologias

* [Python](https://www.python.org/) - Linguagem de programação
* [python-dotenv](https://pypi.org/project/python-dotenv/) - Gerenciamento de configurações

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