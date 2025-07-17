import csv
import os
from datetime import datetime


def extract_document_data(linha):
    """
    Extrai dados do documento de uma linha CNAB para geração de CSV
    
    Args:
        linha (str): Linha do arquivo CNAB
        
    Returns:
        dict: Dicionário com os dados extraídos (n_documento, valor, data_pagamento)
              ou None se não conseguir extrair os dados
    """
    try:
        # Verificar se a linha tem tamanho suficiente
        if len(linha) < 267:
            return None
        
        # Extrair número do documento (posições 117-131)
        n_documento = linha[116:131].strip()
        
        # Extrair valor (posições 252-267)
        valor_str = linha[251:267].strip()
        if valor_str and valor_str.isdigit():
            # Dividir por 1000 para obter o formato correto (centavos)
            valor_int = int(valor_str)
            valor_formatado = f"{valor_int / 1000:.2f}".replace('.', ',')
        else:
            valor_formatado = "0,00"
        
        # Extrair data de vencimento (posições 111-116) formato DDMMAA
        data_str = linha[110:116].strip()
        if len(data_str) == 6:
            dia = data_str[:2]
            mes = data_str[2:4]
            ano = data_str[4:6]
            # Assumir que anos 00-30 são 2000-2030, e 31-99 são 1931-1999
            if int(ano) <= 30:
                ano_completo = f"20{ano}"
            else:
                ano_completo = f"19{ano}"
            data_formatada = f"{dia}/{mes}/{ano_completo}"
        else:
            data_formatada = ""
        
        return {
            'n_documento': n_documento,
            'valor': valor_formatado,
            'data_pagamento': data_formatada
        }
        
    except Exception as e:
        print(f"Erro ao extrair dados da linha: {str(e)}")
        return None


def generate_csv_from_cnab_lines(linhas_antecipadas, output_path):
    """
    Gera arquivo CSV a partir das linhas de operações antecipadas
    
    Args:
        linhas_antecipadas (list): Lista de linhas do arquivo CNAB com operações antecipadas
        output_path (str): Caminho onde salvar o arquivo CSV
        
    Returns:
        tuple: (bool, str) - (sucesso, mensagem)
    """
    try:
        dados_csv = []
        
        # Processar cada linha (exceto header e trailer)
        for i, linha in enumerate(linhas_antecipadas):
            # Pular header (primeira linha) e trailer (última linha)
            if i == 0 or i == len(linhas_antecipadas) - 1:
                continue
                
            # Verificar se é operação antecipada (tipo 1 na posição 319)
            if len(linha) >= 319:
                tipo_operacao = linha[318:319].strip()
                if tipo_operacao == '1':  # Operação antecipada
                    dados_linha = extract_document_data(linha)
                    if dados_linha and dados_linha['n_documento']:
                        dados_csv.append(dados_linha)
        
        # Gerar arquivo CSV
        if dados_csv:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['n_documento', 'valor', 'data_pagamento']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Escrever cabeçalho
                writer.writeheader()
                
                # Escrever dados
                for dados in dados_csv:
                    writer.writerow(dados)
            
            return True, f"CSV gerado com sucesso: {len(dados_csv)} registros salvos em {output_path}"
        else:
            return False, "Nenhum registro de operação antecipada encontrado para gerar CSV"
            
    except Exception as e:
        return False, f"Erro ao gerar CSV: {str(e)}"


def generate_csv_for_antecipated_operations(arquivo_antecipado):
    """
    Gera arquivo CSV para operações antecipadas a partir de um arquivo .ret
    
    Args:
        arquivo_antecipado (str): Caminho para o arquivo .ret com operações antecipadas
        
    Returns:
        tuple: (bool, str, str) - (sucesso, mensagem, caminho_csv)
    """
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(arquivo_antecipado):
            return False, f"Arquivo não encontrado: {arquivo_antecipado}", None
        
        # Definir caminho do CSV
        nome_base = os.path.splitext(arquivo_antecipado)[0]
        csv_path = f"{nome_base}.csv"
        
        # Ler arquivo
        try:
            with open(arquivo_antecipado, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
        except UnicodeDecodeError:
            with open(arquivo_antecipado, 'r', encoding='latin-1') as f:
                linhas = f.readlines()
        
        # Limpar quebras de linha
        linhas = [linha.rstrip('\n') for linha in linhas]
        
        # Gerar CSV
        sucesso, mensagem = generate_csv_from_cnab_lines(linhas, csv_path)
        
        if sucesso:
            return True, mensagem, csv_path
        else:
            return False, mensagem, None
            
    except Exception as e:
        return False, f"Erro ao processar arquivo antecipado: {str(e)}", None
