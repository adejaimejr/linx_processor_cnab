import os
import time
import traceback
import shutil
from datetime import datetime
from dotenv import load_dotenv
import re

# Importa utilitários para geração de CSV
try:
    from generate_csv_utils import generate_output_for_antecipated_operations
except ImportError:
    print("⚠️ Módulo generate_csv_utils não encontrado. Funcionalidade de geração de arquivos desabilitada.")
    generate_output_for_antecipated_operations = None

# Carrega as variáveis de ambiente
load_dotenv()

def identify_bank(first_line):
    """Identifica o banco baseado na primeira linha do arquivo"""
    if not first_line:
        return None
    
    # Verifica o código do banco nas posições 77-79
    if len(first_line) < 79:
        print(f"ALERTA: Primeira linha com formato inválido. Comprimento: {len(first_line)}, esperado >= 79")
        return None
        
    bank_code = first_line[76:79]
    print("\nAnalisando primeira linha do arquivo:")
    print(f"Conteúdo nas posições 76-79: '{bank_code}'")
    
    if bank_code == "237" or "BRADESCO" in first_line:
        print("Banco identificado como BRADESCO")
        return "BRADESCO"
    elif bank_code == "001" or "BANCO DO BRASIL" in first_line:
        print("Banco identificado como Banco do Brasil")
        return "BB"
    
    print("AVISO: Banco não identificado na primeira linha")
    return None

def load_bank_operations():
    """Carrega as configurações de operações dos bancos do arquivo .env"""
    bb_operations = os.getenv('BB_OPERACAO', '').split(',')
    bb_enabled = os.getenv('BB_ENABLE', 'false').lower() == 'true'
    bb_separar_antecipacao = os.getenv('BB_SEPARAR_ANTECIPACAO', 'false').lower() == 'true'
    
    bradesco_operations = os.getenv('BRADESCO_OPERACAO', '').split(',')
    bradesco_enabled = os.getenv('BRADESCO_ENABLE', 'false').lower() == 'true'
    bradesco_separar_antecipacao = os.getenv('BRADESCO_SEPARAR_ANTECIPACAO', 'false').lower() == 'true'
    
    return {
        'BB': {
            'operations': bb_operations,
            'enabled': bb_enabled,
            'separar_antecipacao': bb_separar_antecipacao
        },
        'BRADESCO': {
            'operations': bradesco_operations,
            'enabled': bradesco_enabled,
            'separar_antecipacao': bradesco_separar_antecipacao
        }
    }

def is_valid_operation(operacao, bank_config):
    """
    Valida se uma operação é válida para um banco específico com base nas configurações.
    
    Args:
        operacao (str): Código da operação a ser validada
        bank_config (dict): Configurações do banco (contém a lista de operações válidas)
        
    Returns:
        bool: True se a operação for válida, False caso contrário
    """
    # Remover espaços em branco e validar
    operacao = operacao.strip() if operacao else ""
    
    # Se a operação estiver vazia, é inválida
    if not operacao:
        return False
    
    # Verifica se a operação está na lista de operações permitidas para o banco
    return operacao in bank_config['operations']

def copy_file(source_path, target_dir, timestamp=None, keep_original_name=False):
    """
    Copia um arquivo para outro diretório com timestamp opcional
    
    Args:
        source_path (str): Caminho do arquivo fonte
        target_dir (str): Diretório de destino
        timestamp (str, optional): Timestamp para adicionar ao nome do arquivo. Default is None.
        keep_original_name (bool, optional): Se True, mantém o nome original do arquivo. Default is False.
    
    Returns:
        str or None: Caminho do arquivo copiado se bem-sucedido, None caso contrário
    """
    try:
        if target_dir and os.path.exists(target_dir):
            # Gera o novo nome
            filename = os.path.basename(source_path)
            name_without_ext = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1]
            
            if keep_original_name:
                new_filename = filename
            else:
                new_filename = f"{name_without_ext}_{timestamp}{ext}" if timestamp else filename
                
            target_path = os.path.join(target_dir, new_filename)
            
            # Se o arquivo já existe no destino, não copia novamente
            if not os.path.exists(target_path):
                try:
                    # Tentativa com diferentes encodings
                    encoding_list = ['utf-8', 'iso-8859-1', 'latin1', 'cp1252']
                    content = None
                    
                    for encoding in encoding_list:
                        try:
                            with open(source_path, 'r', encoding=encoding) as source:
                                content = source.read()
                                break
                        except UnicodeDecodeError:
                            continue
                    
                    if content is None:
                        # Se todas as tentativas de leitura falharem, tenta como binário
                        with open(source_path, 'rb') as source:
                            content = source.read()
                            with open(target_path, 'wb') as target:
                                target.write(content)
                    else:
                        with open(target_path, 'w', encoding='utf-8') as target:
                            target.write(content)
                    
                    print(f"Arquivo {'original' if keep_original_name else ''} copiado para: {target_path}")
                    return target_path
                except Exception as e:
                    print(f"Erro ao ler/escrever arquivo: {str(e)}")
                    
                    # Tentativa final usando shutil.copy2 (preserva metadados)
                    try:
                        import shutil
                        shutil.copy2(source_path, target_path)
                        print(f"Arquivo copiado para {target_path} usando método alternativo")
                        return target_path
                    except Exception as e2:
                        print(f"Erro final ao copiar arquivo: {str(e2)}")
            else:
                print(f"Arquivo já existe no destino: {target_path}")
                return target_path
    except Exception as e:
        print(f"Erro ao copiar arquivo para {target_dir}: {str(e)}")
    return None

def generate_processing_report(banco, total_lines, linhas_validas, linhas_invalidas, lines_kept, 
                          count_por_operacao, count_normal, count_antecipado, 
                          count_tipo_desconhecido, tempo_total, output_files=None):
    """
    Gera um relatório detalhado do processamento do arquivo CNAB
    
    Args:
        banco (str): Nome do banco identificado
        total_lines (int): Total de linhas no arquivo
        linhas_validas (int): Número de linhas válidas processadas (excluindo header/trailer)
        linhas_invalidas (int): Número de linhas inválidas encontradas
        lines_kept (int): Número de linhas mantidas no arquivo final
        count_por_operacao (dict): Dicionário com contagem por código de operação
        count_normal (int): Número de linhas com operações normais
        count_antecipado (int): Número de linhas com operações antecipadas
        count_tipo_desconhecido (int): Número de linhas com tipo não identificado
        tempo_total (float): Tempo total de processamento em segundos
        output_files (list): Lista de arquivos gerados pelo processamento
    
    Returns:
        str: Relatório formatado em texto
    """
    report = []
    report.append("\n" + "="*80)
    report.append(f"RELATÓRIO DE PROCESSAMENTO CNAB - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("="*80)
    
    # Informações básicas do processamento
    report.append(f"\n📊 INFORMAÇÕES GERAIS:")
    report.append(f"  • Banco identificado: {banco}")
    report.append(f"  • Total de linhas no arquivo: {total_lines}")
    
    # Calcular registros de dados (excluindo header e trailer)
    # linhas_validas já deve representar apenas os registros de dados válidos
    registros_dados_total = max(1, total_lines - 2)  # Total de registros de dados possíveis
    
    if registros_dados_total > 0:
        report.append(f"  • Registros válidos (dados): {linhas_validas} ({(linhas_validas/registros_dados_total*100):.2f}%)")
        report.append(f"  • Registros inválidos: {linhas_invalidas} ({(linhas_invalidas/registros_dados_total*100):.2f}%)")
        report.append(f"  • Registros mantidos: {lines_kept} ({(lines_kept/registros_dados_total*100):.2f}%)")
    else:
        report.append(f"  • Registros válidos (dados): {linhas_validas}")
        report.append(f"  • Registros inválidos: {linhas_invalidas}")
        report.append(f"  • Registros mantidos: {lines_kept}")
    
    # Detalhes das operações
    report.append(f"\n🔍 ANÁLISE DE OPERAÇÕES:")
    if count_por_operacao:
        # Ordenar operações por quantidade (decrescente)
        sorted_ops = sorted(count_por_operacao.items(), key=lambda x: x[1], reverse=True)
        for op, count in sorted_ops:
            percentual = (count / max(1, lines_kept) * 100)
            report.append(f"  • Operação '{op}': {count} linhas ({percentual:.2f}%)")
    else:
        report.append("  • Nenhuma operação processada")
    
    # Detalhes de tipos de valores (normal/antecipado)
    if count_normal > 0 or count_antecipado > 0:
        report.append(f"\n💰 SEPARAÇÃO POR TIPO DE VALOR:")
        if count_normal > 0:
            percentual_normal = (count_normal / max(1, count_normal + count_antecipado) * 100)
            report.append(f"  • Operações normais (tipo 2): {count_normal} ({percentual_normal:.2f}%)")
        
        if count_antecipado > 0:
            percentual_antecipado = (count_antecipado / max(1, count_normal + count_antecipado) * 100)
            report.append(f"  • Operações antecipadas (tipo 1): {count_antecipado} ({percentual_antecipado:.2f}%)")
        
        if count_tipo_desconhecido > 0:
            percentual_desconhecido = (count_tipo_desconhecido / max(1, count_normal) * 100)
            report.append(f"  • Operações com tipo não identificado: {count_tipo_desconhecido} ({percentual_desconhecido:.2f}%)")
    
    # Arquivos gerados
    if output_files:
        # Remover duplicatas mantendo a ordem
        unique_files = []
        seen_files = set()
        for file_path in output_files:
            if file_path not in seen_files:
                unique_files.append(file_path)
                seen_files.add(file_path)
        
        report.append(f"\n📁 ARQUIVOS GERADOS ({len(unique_files)}):")
        for idx, file_path in enumerate(unique_files, 1):
            file_name = os.path.basename(file_path)
            file_dir = os.path.dirname(file_path)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path) / 1024  # KB
                report.append(f"  {idx}. {file_name} ({file_size:.2f} KB)")
                report.append(f"     📂 {file_dir}")
            else:
                report.append(f"  {idx}. {file_name} ⚠️ (arquivo não encontrado)")
                report.append(f"     📂 {file_dir}")
    
    report.append("\n" + "="*80)
    
    return "\n".join(report)

def backup_original_file(cnab_filepath):
    """
    Faz backup do arquivo original na pasta cnab/ com o nome original
    
    Args:
        cnab_filepath (str): Caminho completo para o arquivo original
        
    Returns:
        tuple: (str, bool) - Caminho do backup e status de sucesso
    """
    try:
        # Certifica-se de que a pasta cnab existe
        cnab_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cnab')
        if not os.path.exists(cnab_dir):
            try:
                os.makedirs(cnab_dir)
                print(f"Pasta de backup 'cnab' criada: {cnab_dir}")
            except Exception as e:
                print(f"Erro ao criar pasta de backup 'cnab': {str(e)}")
                return None, False
        
        # Obter o nome do arquivo original
        original_filename = os.path.basename(cnab_filepath)
        backup_path = os.path.join(cnab_dir, original_filename)
        
        # Verificar se o arquivo já existe no backup
        if os.path.exists(backup_path):
            # Adiciona timestamp ao nome para evitar sobrescrever
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_parts = os.path.splitext(original_filename)
            backup_path = os.path.join(cnab_dir, f"{filename_parts[0]}_{timestamp}{filename_parts[1]}")
        
        # Método principal: usar shutil para preservar metadados e permissões
        try:
            import shutil
            shutil.copy2(cnab_filepath, backup_path)
            file_size = os.path.getsize(backup_path) / 1024  # KB
            print(f"Backup realizado com sucesso: {backup_path} ({file_size:.2f} KB)")
            return backup_path, True
        except Exception as e:
            print(f"Erro no método principal de backup: {str(e)}")
            
            # Método alternativo: cópia binária direta
            try:
                print("Tentando método alternativo de backup...")
                with open(cnab_filepath, 'rb') as src_file:
                    with open(backup_path, 'wb') as dst_file:
                        dst_file.write(src_file.read())
                
                if os.path.exists(backup_path):
                    file_size = os.path.getsize(backup_path) / 1024  # KB
                    print(f"Backup realizado com método alternativo: {backup_path} ({file_size:.2f} KB)")
                    return backup_path, True
                else:
                    print("Falha no backup alternativo: arquivo não foi criado")
                    return None, False
            except Exception as e2:
                print(f"Falha final no backup: {str(e2)}")
                return None, False
                
    except Exception as e:
        print(f"Erro ao realizar backup do arquivo original: {str(e)}")
        print(traceback.format_exc())
        return None, False

def should_process_file(filename):
    """
    Verifica se um arquivo deve ser processado
    
    Args:
        filename (str): Nome do arquivo
        
    Returns:
        bool: True se o arquivo deve ser processado, False caso contrário
    """
    # Não processa arquivos que já possuem underscore (provavelmente já processados)
    if '_' in filename:
        return False
    
    # Verifica extensão
    if not (filename.upper().endswith('.RET') or filename.lower().endswith('.ret')):
        return False
    
    return True

def process_cnab_file(arquivo, operacoes_desejadas=None, banco=None, separar_antecipacao=False, output_dirs=None):
    """
    Processa um arquivo CNAB, filtrando por operações desejadas e identificando o banco.
    
    Args:
        arquivo (str): Caminho para o arquivo CNAB
        operacoes_desejadas (list, optional): Lista de operações a serem mantidas
        banco (str, optional): Nome do banco para forçar a identificação
        separar_antecipacao (bool, optional): Indica se deve separar operações antecipadas
        output_dirs (list, optional): Lista de diretórios onde salvar os arquivos processados
        
    Returns:
        tuple: (caminho_arquivo_alterado, string_relatorio, status_processamento)
    """
    import time
    inicio_processamento = time.time()
    
    print(f"\n🔄 Processando arquivo: {os.path.basename(arquivo)}")
    tamanho_arquivo = os.path.getsize(arquivo) / 1024  # KB
    print(f"📦 Tamanho do arquivo: {tamanho_arquivo:.2f} KB")
    
    # Fazer backup do arquivo original na pasta cnab
    backup_path, backup_success = backup_original_file(arquivo)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Preparar relatório
    relatorio = []
    relatorio.append("=" * 80)
    relatorio.append(f"RELATÓRIO DE PROCESSAMENTO CNAB - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    relatorio.append("=" * 80)
    relatorio.append("")
    
    # Contadores para estatísticas
    total_linhas = 0
    linhas_validas = 0
    linhas_invalidas = 0
    linhas_mantidas = 0
    
    # Contadores para tipos de operações
    contagem_operacoes = {}
    
    # Contadores para tipos de valor (normal/antecipado)
    operacoes_normais = 0
    operacoes_antecipadas = 0
    operacoes_sem_tipo = 0
    
    # Lista para guardar arquivos gerados
    arquivos_gerados = []
    
    # Adicionar o arquivo de backup à lista se o backup foi bem-sucedido
    if backup_success and backup_path:
        backup_tamanho = os.path.getsize(backup_path) / 1024  # KB
        arquivos_gerados.append((backup_path, backup_tamanho))
        print(f"📁 Backup original salvo em: {backup_path} ({backup_tamanho:.2f} KB)")
    
    # Detectar banco
    try:
        banco_detectado = identify_bank(arquivo) if not banco else banco
        if not banco_detectado:
            print("⚠️ Não foi possível identificar o banco do arquivo")
            relatorio.append("⚠️ ALERTA: Não foi possível identificar o banco do arquivo")
            banco_detectado = "DESCONHECIDO"
        else:
            print(f"🏦 Banco identificado: {banco_detectado}")
            relatorio.append(f"📊 INFORMAÇÕES GERAIS:")
            relatorio.append(f"  • Banco identificado: {banco_detectado}")
    except Exception as e:
        print(f"❌ Erro ao identificar banco: {str(e)}")
        relatorio.append(f"❌ ERRO: Falha ao identificar banco - {str(e)}")
        banco_detectado = "ERRO"
    
    # Definir caminhos dos arquivos de saída
    diretorio = os.path.dirname(arquivo)
    nome_arquivo = os.path.basename(arquivo)
    nome_base, extensao = os.path.splitext(nome_arquivo)
    
    # Nome do arquivo alterado (sem timestamp se já tiver)
    if re.search(r'\d{14}', nome_base):
        arquivo_alterado = os.path.join(diretorio, f"{nome_base}_alterado{extensao}")
    else:
        arquivo_alterado = os.path.join(diretorio, f"{nome_base}_{timestamp}_alterado{extensao}")
    
    # Nomes para arquivos separados por tipo
    arquivo_normal = arquivo_alterado.replace('_alterado', '_normal')
    arquivo_antecipado = arquivo_alterado.replace('_alterado', '_antecipado')
    
    # Verificar se as operações desejadas foram especificadas
    if not operacoes_desejadas or not isinstance(operacoes_desejadas, list) or len(operacoes_desejadas) == 0:
        print("⚠️ Nenhuma operação desejada especificada, mantendo todas as linhas")
        relatorio.append("⚠️ ALERTA: Nenhuma operação desejada especificada, mantendo todas as linhas")
    
    try:
        # Primeiro, tente com UTF-8
        with open(arquivo, 'r', encoding='utf-8') as f:
            primeira_linha = f.readline()
            # Verificar se a primeira linha está no formato esperado
            if len(primeira_linha.strip()) < 240:  # CNAB400 tem pelo menos 400 caracteres por linha
                print(f"⚠️ A primeira linha não está no formato esperado. Comprimento: {len(primeira_linha.strip())}")
                relatorio.append(f"⚠️ ALERTA: Primeira linha com formato incorreto ({len(primeira_linha.strip())} caracteres)")
    except UnicodeDecodeError:
        # Se falhar com UTF-8, tente com latin-1
        try:
            with open(arquivo, 'r', encoding='latin-1') as f:
                primeira_linha = f.readline()
                if len(primeira_linha.strip()) < 240:
                    print(f"⚠️ A primeira linha não está no formato esperado. Comprimento: {len(primeira_linha.strip())}")
                    relatorio.append(f"⚠️ ALERTA: Primeira linha com formato incorreto ({len(primeira_linha.strip())} caracteres)")
        except Exception as e:
            print(f"❌ Erro ao verificar primeira linha: {str(e)}")
            relatorio.append(f"❌ ERRO: Falha ao verificar primeira linha - {str(e)}")
    
    # Listas para as linhas de cada tipo
    linhas_normais = []
    linhas_antecipadas = []
    
    # Ler o arquivo e processar
    try:
        # Primeiro tente com UTF-8
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
        except UnicodeDecodeError:
            # Se falhar, tente com latin-1
            with open(arquivo, 'r', encoding='latin-1') as f:
                linhas = f.readlines()
        
        total_linhas = len(linhas)
        print(f"📊 Total de linhas no arquivo: {total_linhas}")
        relatorio.append(f"  • Total de linhas no arquivo: {total_linhas}")
        
        # Processar linha por linha
        linhas_alteradas = []
        
        for i, linha in enumerate(linhas):
            total_linhas = i + 1  # Contar total de linhas
            try:
                linha = linha.rstrip('\n')
                
                # Verificar se a linha tem o tamanho mínimo esperado
                if len(linha.strip()) < 240:
                    linhas_invalidas += 1
                    print(f"⚠️ Linha {i+1} ignorada: tamanho insuficiente ({len(linha.strip())} caracteres)")
                    continue
                
                # Se for header (primeira linha) ou trailer (última linha), manter sempre
                if i == 0 or i == len(linhas) - 1:
                    linhas_alteradas.append(linha)
                    linhas_normais.append(linha)
                    linhas_antecipadas.append(linha)
                    linhas_mantidas += 1
                    continue
                
                # Contar apenas registros de dados (não header/trailer) como linhas válidas
                linhas_validas += 1
                
                # Extrair código da operação (posição pode variar de acordo com o layout)
                codigo_operacao = None
                if len(linha) >= 108:  # Layout CNAB400
                    codigo_operacao = linha[108:110].strip()
                
                # Extrair tipo de operação (coluna 319 - 1: Antecipada, 2: Normal)
                tipo_operacao = None
                if len(linha) >= 320:
                    tipo_operacao = linha[318:319].strip()  # Zero-based index
                
                # Registrar estatística de operação
                if codigo_operacao:
                    if codigo_operacao in contagem_operacoes:
                        contagem_operacoes[codigo_operacao] += 1
                    else:
                        contagem_operacoes[codigo_operacao] = 1
                
                # Registrar estatística por tipo
                if tipo_operacao == '1':
                    operacoes_antecipadas += 1
                elif tipo_operacao == '2':
                    operacoes_normais += 1
                else:
                    operacoes_sem_tipo += 1
                
                # Verificar se a operação está entre as desejadas
                if not operacoes_desejadas or not codigo_operacao or codigo_operacao in operacoes_desejadas:
                    linhas_alteradas.append(linha)
                    linhas_mantidas += 1
                    
                    # Separar por tipo se solicitado
                    if separar_antecipacao:
                        if tipo_operacao == '1':
                            linhas_antecipadas.append(linha)
                        else:  # Incluir sem tipo ou com tipo 2 no arquivo normal
                            linhas_normais.append(linha)
                    else:
                        # Se não for separar, adiciona em ambos para garantir header e trailer
                        linhas_normais.append(linha)
                        linhas_antecipadas.append(linha)
                
            except Exception as e:
                linhas_invalidas += 1
                print(f"❌ Erro ao processar linha {i+1}: {str(e)}")
                relatorio.append(f"❌ ERRO: Linha {i+1} - {str(e)}")
                continue
        
        # Salvar arquivo alterado com as linhas filtradas
        with open(arquivo_alterado, 'w', encoding='utf-8') as f:
            f.write('\n'.join(linhas_alteradas))
        
        tamanho_alterado = os.path.getsize(arquivo_alterado) / 1024  # KB
        print(f"💾 Arquivo alterado salvo: {os.path.basename(arquivo_alterado)} ({tamanho_alterado:.2f} KB)")
        arquivos_gerados.append((arquivo_alterado, tamanho_alterado))
        
        # Cria cópia do arquivo original com timestamp se necessário
        if not re.search(r'\d{14}', nome_base):
            arquivo_original_com_timestamp = os.path.join(diretorio, f"{nome_base}_{timestamp}{extensao}")
            shutil.copy2(arquivo, arquivo_original_com_timestamp)
            tamanho_original = os.path.getsize(arquivo_original_com_timestamp) / 1024  # KB
            print(f"💾 Cópia do original salva: {os.path.basename(arquivo_original_com_timestamp)} ({tamanho_original:.2f} KB)")
            arquivos_gerados.append((arquivo_original_com_timestamp, tamanho_original))
        
        # Separar por tipo (normal e antecipado) se solicitado
        if separar_antecipacao:
            # Salvar arquivo de operações normais
            if linhas_normais:
                with open(arquivo_normal, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(linhas_normais))
                tamanho_normal = os.path.getsize(arquivo_normal) / 1024  # KB
                print(f"💾 Arquivo normal salvo: {os.path.basename(arquivo_normal)} ({tamanho_normal:.2f} KB)")
                arquivos_gerados.append((arquivo_normal, tamanho_normal))
            else:
                print("⚠️ Nenhuma operação normal encontrada, arquivo normal não gerado")
                relatorio.append("⚠️ ALERTA: Nenhuma operação normal encontrada")
            
            # Salvar arquivo de operações antecipadas
            if linhas_antecipadas:
                with open(arquivo_antecipado, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(linhas_antecipadas))
                tamanho_antecipado = os.path.getsize(arquivo_antecipado) / 1024  # KB
                print(f"💾 Arquivo antecipado salvo: {os.path.basename(arquivo_antecipado)} ({tamanho_antecipado:.2f} KB)")
                arquivos_gerados.append((arquivo_antecipado, tamanho_antecipado))
                
                # Gerar arquivo de saída (CSV/XLS) para operações antecipadas
                if generate_output_for_antecipated_operations:
                    try:
                        output_format = os.getenv('OUTPUT_FORMAT', 'csv').upper()
                        sucesso_output, mensagem_output, caminho_output = generate_output_for_antecipated_operations(arquivo_antecipado)
                        if sucesso_output and caminho_output:
                            tamanho_output = os.path.getsize(caminho_output) / 1024  # KB
                            print(f"📈 {output_format} antecipado gerado: {os.path.basename(caminho_output)} ({tamanho_output:.2f} KB)")
                            arquivos_gerados.append((caminho_output, tamanho_output))
                            relatorio.append(f"📈 {output_format}: {mensagem_output}")
                        else:
                            print(f"⚠️ Falha ao gerar {output_format}: {mensagem_output}")
                            relatorio.append(f"⚠️ {output_format}: {mensagem_output}")
                    except Exception as e:
                        output_format = os.getenv('OUTPUT_FORMAT', 'csv').upper()
                        print(f"❌ Erro ao gerar {output_format}: {str(e)}")
                        relatorio.append(f"❌ Erro {output_format}: {str(e)}")
            else:
                print("⚠️ Nenhuma operação antecipada encontrada, arquivo antecipado não gerado")
                relatorio.append("⚠️ ALERTA: Nenhuma operação antecipada encontrada")
        
        # Se foram especificados diretórios adicionais de saída, copia os arquivos para eles
        if output_dirs:
            for output_dir in output_dirs:
                if output_dir and os.path.exists(output_dir) and output_dir != diretorio:
                    print(f"\n📂 Copiando arquivos para diretório adicional: {output_dir}")
                    
                    # Copia o arquivo alterado
                    destino_alterado = os.path.join(output_dir, os.path.basename(arquivo_alterado))
                    try:
                        shutil.copy2(arquivo_alterado, destino_alterado)
                        tamanho = os.path.getsize(destino_alterado) / 1024  # KB
                        print(f"💾 Arquivo alterado copiado: {os.path.basename(destino_alterado)} ({tamanho:.2f} KB)")
                        arquivos_gerados.append((destino_alterado, tamanho))
                    except Exception as e:
                        print(f"❌ Erro ao copiar arquivo alterado para {output_dir}: {str(e)}")
                    
                    # Copia o arquivo normal se existir
                    if separar_antecipacao and linhas_normais:
                        destino_normal = os.path.join(output_dir, os.path.basename(arquivo_normal))
                        try:
                            shutil.copy2(arquivo_normal, destino_normal)
                            tamanho = os.path.getsize(destino_normal) / 1024  # KB
                            print(f"💾 Arquivo normal copiado: {os.path.basename(destino_normal)} ({tamanho:.2f} KB)")
                            arquivos_gerados.append((destino_normal, tamanho))
                        except Exception as e:
                            print(f"❌ Erro ao copiar arquivo normal para {output_dir}: {str(e)}")
                    
                    # Copia o arquivo antecipado se existir
                    if separar_antecipacao and linhas_antecipadas:
                        destino_antecipado = os.path.join(output_dir, os.path.basename(arquivo_antecipado))
                        try:
                            shutil.copy2(arquivo_antecipado, destino_antecipado)
                            tamanho = os.path.getsize(destino_antecipado) / 1024  # KB
                            print(f"💾 Arquivo antecipado copiado: {os.path.basename(destino_antecipado)} ({tamanho:.2f} KB)")
                            arquivos_gerados.append((destino_antecipado, tamanho))
                            
                            # Copia o arquivo de saída (CSV/XLS) antecipado se existir
                            output_format = os.getenv('OUTPUT_FORMAT', 'csv').lower()
                            if output_format == 'xls':
                                output_antecipado = arquivo_antecipado.replace('.ret', '.xlsx').replace('.RET', '.xlsx')
                            else:
                                output_antecipado = arquivo_antecipado.replace('.ret', '.csv').replace('.RET', '.csv')
                            
                            if os.path.exists(output_antecipado):
                                destino_output = os.path.join(output_dir, os.path.basename(output_antecipado))
                                try:
                                    shutil.copy2(output_antecipado, destino_output)
                                    tamanho_output = os.path.getsize(destino_output) / 1024  # KB
                                    format_upper = output_format.upper()
                                    print(f"📈 {format_upper} antecipado copiado: {os.path.basename(destino_output)} ({tamanho_output:.2f} KB)")
                                    arquivos_gerados.append((destino_output, tamanho_output))
                                except Exception as e:
                                    format_upper = output_format.upper()
                                    print(f"❌ Erro ao copiar {format_upper} antecipado para {output_dir}: {str(e)}")
                        except Exception as e:
                            print(f"❌ Erro ao copiar arquivo antecipado para {output_dir}: {str(e)}")
    
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {str(e)}")
        print(traceback.format_exc())
        relatorio.append(f"❌ ERRO CRÍTICO: {str(e)}")
        return None, '\n'.join(relatorio), False
    
    # Calcular estatísticas finais
    tempo_processamento = time.time() - inicio_processamento
    velocidade_processamento = total_linhas / tempo_processamento if tempo_processamento > 0 else 0
    
    porcentagem_validas = (linhas_validas / total_linhas) * 100 if total_linhas > 0 else 0
    porcentagem_invalidas = (linhas_invalidas / total_linhas) * 100 if total_linhas > 0 else 0
    porcentagem_mantidas = (linhas_mantidas / total_linhas) * 100 if total_linhas > 0 else 0
    
    # Exibir resumo final
    print(f"\n✅ Processamento concluído em {tempo_processamento:.2f} segundos")
    print(f"📊 Linhas no arquivo: {total_linhas}")
    print(f"📊 Linhas mantidas: {linhas_mantidas} ({porcentagem_mantidas:.2f}%)")
    
    # Preparar lista de arquivos para o relatório (remover duplicatas por nome de arquivo)
    arquivos_unicos = {}
    for caminho, tamanho in arquivos_gerados:
        nome_arquivo = os.path.basename(caminho)
        if nome_arquivo not in arquivos_unicos:
            arquivos_unicos[nome_arquivo] = (caminho, tamanho)
    
    arquivos_para_relatorio = [caminho for caminho, _ in arquivos_unicos.values()]
    
    # Corrigir registros mantidos (apenas registros de dados, não header/trailer)
    registros_mantidos_corrigidos = max(0, linhas_mantidas - 2) if total_linhas > 2 else linhas_mantidas
    
    # Gerar relatório usando a função corrigida
    relatorio_texto = generate_processing_report(
        banco_detectado, 
        total_linhas, 
        linhas_validas,  # Já conta apenas registros de dados
        linhas_invalidas, 
        registros_mantidos_corrigidos,  # Usar valor corrigido
        contagem_operacoes,
        operacoes_normais,
        operacoes_antecipadas,
        operacoes_sem_tipo,
        tempo_processamento,
        arquivos_para_relatorio
    )
    
    # Salvar relatório detalhado em arquivo
    report_path = save_processing_report(banco_detectado, relatorio_texto, arquivo, output_dirs)
    if report_path:
        arquivos_gerados.append((report_path, os.path.getsize(report_path) / 1024))
    
    # Registrar o arquivo como processado
    register_processed_file(os.path.basename(arquivo))
    
    print(f"\n✅ Processamento concluído com sucesso!")
    return True

def process_directory(directory, output_dirs=None):
    """Processa todos os arquivos .RET em um diretório"""
    try:
        # Carrega as configurações dos bancos
        bank_configs = load_bank_operations()
        
        # Lista todos os arquivos .RET (case insensitive) que não têm underscore
        ret_files = [f for f in os.listdir(directory) 
                    if (f.upper().endswith('.RET') or f.lower().endswith('.ret')) and should_process_file(f)]
        
        for filename in ret_files:
            # Verifica se o arquivo já foi processado
            if is_file_processed(filename):
                print(f"Arquivo {filename} já foi processado anteriormente. Pulando...")
                continue
            
            # Processa o arquivo
            file_path = os.path.join(directory, filename)
            
            # Primeiro identifica o banco para determinar a configuração correta
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    primeira_linha = f.readline()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        primeira_linha = f.readline()
                except Exception:
                    primeira_linha = ""
            
            banco_identificado = identify_bank(primeira_linha)
            
            # Define as operações desejadas e se deve separar por antecipação com base no banco identificado
            operacoes_desejadas = None
            separar_antecipacao = False
            
            if banco_identificado == "BB" and bank_configs['BB']['enabled']:
                operacoes_desejadas = bank_configs['BB']['operations']
                separar_antecipacao = bank_configs['BB']['separar_antecipacao']
                print(f"Banco do Brasil identificado. Separar antecipação: {separar_antecipacao}")
            elif banco_identificado == "BRADESCO" and bank_configs['BRADESCO']['enabled']:
                operacoes_desejadas = bank_configs['BRADESCO']['operations']
                separar_antecipacao = bank_configs['BRADESCO']['separar_antecipacao']
                print(f"Bradesco identificado. Separar antecipação: {separar_antecipacao}")
            else:
                print(f"Banco não identificado ou não habilitado: {banco_identificado}")
            
            # Processa o arquivo com as configurações corretas
            if process_cnab_file(file_path, operacoes_desejadas, banco_identificado, separar_antecipacao, output_dirs):
                print(f"\nArquivo {filename} processado com sucesso!")
            else:
                print(f"\nErro ao processar o arquivo {filename}")
    except Exception as e:
        print(f"Erro ao processar diretório {directory}: {str(e)}")
        print(traceback.format_exc())

def is_file_processed(filename):
    try:
        with open('processed_files.md', 'r', encoding='utf-8') as file:
            content = file.read()
            return filename in content
    except FileNotFoundError:
        return False

def register_processed_file(filename):
    """
    Registra um arquivo como processado no arquivo processed_files.md
    
    Args:
        filename (str): Nome do arquivo processado
    """
    try:
        with open('processed_files.md', 'a+', encoding='utf-8') as file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file.write(f"- {filename} - Processado em {timestamp}\n")
            print(f"Arquivo {filename} registrado como processado.")
    except Exception as e:
        print(f"Erro ao registrar arquivo processado: {str(e)}")

def save_processing_report(banco, report_content, arquivo_processado=None, output_dirs=None):
    """
    Salva o relatório de processamento em arquivo
    
    Args:
        banco (str): Nome do banco identificado para identificação do relatório
        report_content (str): Conteúdo do relatório a ser salvo
        arquivo_processado (str, optional): Nome do arquivo processado para incluir no nome do relatório
        output_dirs (list, optional): Lista de diretórios onde copiar o relatório
        
    Returns:
        str or None: Caminho do arquivo de relatório se bem-sucedido, None em caso de erro
    """
    try:
        # Obtém o diretório de relatórios do .env ou usa o padrão
        reports_dir_name = os.getenv('REPORTS_DIR', 'reports')
        reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), reports_dir_name)
        
        # Cria diretório de relatórios se não existir
        if not os.path.exists(reports_dir):
            try:
                os.makedirs(reports_dir)
                print(f"Diretório de relatórios criado: {reports_dir}")
            except Exception as e:
                print(f"⚠️ Erro ao criar diretório de relatórios: {str(e)}")
                # Tenta salvar no diretório atual se não conseguir criar
                reports_dir = os.path.dirname(os.path.abspath(__file__))
                print(f"Usando diretório alternativo: {reports_dir}")
        
        # Gera nome do relatório no formato ideal: <nome_arquivo>_relatorio.txt
        if arquivo_processado:
            # Remove extensão do nome do arquivo
            nome_arquivo = os.path.splitext(os.path.basename(arquivo_processado))[0]
            report_filename = f"{nome_arquivo}_relatorio.txt"
        else:
            # Fallback para quando não há arquivo processado
            banco_normalizado = banco.upper()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"{banco_normalizado}_{timestamp}_relatorio.txt"
            
        report_path = os.path.join(reports_dir, report_filename)
        
        # Salva o relatório em arquivo
        with open(report_path, 'w', encoding='utf-8') as report_file:
            report_file.write(report_content)
        
        file_size = os.path.getsize(report_path) / 1024  # KB
        print(f"\n📝 Relatório detalhado salvo em: {report_path} ({file_size:.2f} KB)")
        
        # Copia o relatório para os diretórios de saída (pasta da rede)
        if output_dirs:
            for output_dir in output_dirs:
                if output_dir and os.path.exists(output_dir):
                    try:
                        destino_report = os.path.join(output_dir, report_filename)
                        shutil.copy2(report_path, destino_report)
                        print(f"📝 Relatório copiado para: {destino_report} ({file_size:.2f} KB)")
                    except Exception as e:
                        print(f"⚠️ Erro ao copiar relatório para {output_dir}: {str(e)}")
        
        return report_path
        
    except Exception as e:
        print(f"⚠️ Erro ao salvar relatório: {str(e)}")
        print(traceback.format_exc())
        
        # Tenta método alternativo de salvamento
        try:
            print("Tentando método alternativo de salvamento...")
            # Tenta salvar na raiz do projeto
            root_dir = os.path.dirname(os.path.abspath(__file__))
            alternative_path = os.path.join(root_dir, f"report_{banco}_{timestamp}.txt")
            with open(alternative_path, 'w', encoding='utf-8') as alt_file:
                alt_file.write(report_content)
            print(f"📄 Relatório salvo com método alternativo: {alternative_path}")
            return alternative_path
        except Exception as e2:
            print(f"❌ Falha final ao salvar relatório: {str(e2)}")
            return None

def main():
    # Carrega o intervalo de verificação do .env
    check_interval = int(os.getenv('CHECK_INTERVAL', '30'))
    
    # Obtém os diretórios do .env
    local_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                            os.getenv('LOCAL_CNAB_DIR', 'cnab'))
    network_dir = os.getenv('NETWORK_CNAB_DIR')
    
    # Lista de diretórios onde salvar os arquivos
    output_dirs = [local_dir]
    if network_dir:
        output_dirs.append(network_dir)
    
    print(f"Monitorando diretórios:")
    print(f"Local: {local_dir}")
    print(f"Rede: {network_dir}")
    print(f"Salvando arquivos em: {', '.join(output_dirs)}")
    print(f"Intervalo de verificação: {check_interval} segundos")
    
    while True:
        try:
            print(f"\n{'='*80}")
            print(f"Verificando arquivos em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}")
            
            # Processa diretório local
            print("\nProcessando diretório local...")
            process_directory(local_dir, output_dirs)
            
            # Processa diretório de rede
            if network_dir and os.path.exists(network_dir):
                print("\nProcessando diretório de rede...")
                process_directory(network_dir, output_dirs)
            else:
                print(f"\nDiretório de rede não encontrado: {network_dir}")
            
            print(f"\nAguardando {check_interval} segundos para próxima verificação...")
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            print("\nProcessamento interrompido pelo usuário.")
            break
        except Exception as e:
            print(f"\nErro durante o processamento: {str(e)}")
            print(f"Tentando novamente em {check_interval} segundos...")
            time.sleep(check_interval)

if __name__ == "__main__":
    main()
