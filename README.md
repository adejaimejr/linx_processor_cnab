# Linx Processor CNAB

Processador inteligente de arquivos CNAB para otimização de importação no ERP Linx e-millennium.

## 📋 Sobre o Projeto

O Linx Processor CNAB é uma ferramenta especializada para processar arquivos de retorno bancário (.RET) do Banco do Brasil e Bradesco, focando em:

- **Filtragem Inteligente**: Seleciona apenas as instruções bancárias específicas (ex: liquidações) do arquivo CNAB
- **Otimização de Importação**: Reduz o tamanho do arquivo removendo instruções desnecessárias
- **Integração com e-millennium**: Melhora a performance e reduz erros na importação do ERP
- **Processamento Automático**: Monitora a pasta e processa novos arquivos automaticamente

### 🎯 Benefícios

- Redução de erros na importação do ERP
- Aumento de performance no processamento
- Eliminação de instruções desnecessárias
- Backup automático dos arquivos originais
- Rastreamento de processamento

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

## 📦 Como Usar

1. Coloque os arquivos .RET na pasta `cnab`
2. O sistema processará automaticamente os arquivos, gerando:
   - Cópia do arquivo original com timestamp
   - Arquivo processado apenas com as instruções desejadas
3. Os arquivos processados estarão prontos para importação no e-millennium

### 📄 Formato dos Arquivos

Para cada arquivo processado, o sistema gera:
- `ORIGINAL_1234567890.RET` - Backup do arquivo original
- `ORIGINAL_1234567890_alterado.RET` - Arquivo filtrado para importação

## 🛠️ Construído com

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
