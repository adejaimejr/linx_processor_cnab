# Linx Processor CNAB

Processador de arquivos CNAB para transações financeiras.

## 📋 Sobre o Projeto

Este projeto é responsável por processar arquivos CNAB contendo transações financeiras, realizando a leitura, validação e armazenamento dos dados em banco de dados.

## 🚀 Começando

Estas instruções permitirão que você obtenha uma cópia do projeto em operação na sua máquina local para fins de desenvolvimento e teste.

### 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL
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
# Edite o arquivo .env com suas configurações
```

## 📦 Estrutura do Projeto

```
linx_processor_cnab/
├── cnab/               # Diretório para arquivos CNAB
├── process_cnab.py     # Script principal
├── requirements.txt    # Dependências do projeto
└── README.md          # Documentação
```

## 🛠️ Construído com

* [Python](https://www.python.org/) - Linguagem de programação
* [PostgreSQL](https://www.postgresql.org/) - Banco de dados

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
