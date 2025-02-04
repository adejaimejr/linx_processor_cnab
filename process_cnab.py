import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

def identify_bank(first_line):
    """Identifica o banco baseado na primeira linha do arquivo"""
    if not first_line:
        return None
    
    # Verifica o código do banco nas posições 77-79
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
    
    bradesco_operations = os.getenv('BRADESCO_OPERACAO', '').split(',')
    bradesco_enabled = os.getenv('BRADESCO_ENABLE', 'false').lower() == 'true'
    
    return {
        'BB': {
            'operations': bb_operations,
            'enabled': bb_enabled
        },
        'BRADESCO': {
            'operations': bradesco_operations,
            'enabled': bradesco_enabled
        }
    }

def copy_file(source_path, target_dir, timestamp):
    """Copia um arquivo para outro diretório com timestamp"""
    try:
        if target_dir and os.path.exists(target_dir):
            # Gera o novo nome com timestamp
            filename = os.path.basename(source_path)
            name_without_ext = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1]
            new_filename = f"{name_without_ext}_{timestamp}{ext}"
            target_path = os.path.join(target_dir, new_filename)
            
            # Se o arquivo já existe no destino, não copia novamente
            if not os.path.exists(target_path):
                with open(source_path, 'r', encoding='utf-8') as source:
                    content = source.read()
                    with open(target_path, 'w', encoding='utf-8') as target:
                        target.write(content)
                print(f"Arquivo original copiado para: {target_path}")
            return True
    except Exception as e:
        print(f"Erro ao copiar arquivo para {target_dir}: {str(e)}")
    return False

def process_cnab_file(file_path, output_dirs=None):
    """Processa um arquivo CNAB e salva em múltiplos diretórios"""
    print(f"\n{'='*80}")
    print(f"Iniciando processamento do arquivo: {os.path.basename(file_path)}")
    print(f"{'='*80}")
    
    # Gera timestamp para os arquivos
    timestamp = str(int(time.time()))
    
    # Primeiro, copia o arquivo original com timestamp para todos os diretórios
    source_dir = os.path.dirname(file_path)
    for output_dir in output_dirs:
        if output_dir != source_dir:  # Não precisa copiar para o mesmo diretório
            copy_file(file_path, output_dir, timestamp)
    
    # Também copia o arquivo com timestamp no diretório original
    copy_file(file_path, source_dir, timestamp)
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    if not lines:
        print("Arquivo vazio!")
        return False
    
    # Identificar o banco na primeira linha
    first_line = lines[0]
    print(f"\nPrimeira linha do arquivo:")
    print(f"Conteúdo completo: {first_line}")
    print(f"Posições 76-79: '{first_line[76:79]}'")
    
    banco = identify_bank(first_line)
    if not banco:
        print(f"Banco não identificado no arquivo {os.path.basename(file_path)}")
        return False
    
    bank_config = load_bank_operations()[banco]
    
    # Verifica se o processamento está habilitado para este banco
    if not bank_config['enabled']:
        print(f"Processamento para {banco} está desabilitado no arquivo .env")
        return False
    
    print(f"\nConfiguração do {banco}:")
    print(f"Operações permitidas: {bank_config['operations']}")
    print(f"Status: {'Habilitado' if bank_config['enabled'] else 'Desabilitado'}")
    
    bank_operations = bank_config['operations']
    processed_lines = [lines[0]]  # Mantém a primeira linha
    
    print("\nAnálise das primeiras 5 linhas:")
    # Processa as linhas do meio
    lines_processed = 0
    lines_kept = 0
    for line in lines[1:-1]:
        lines_processed += 1
        operacao = line[108:110]  # Posições 109 e 110 (0-based index)
        
        if lines_processed <= 5:  # Mostra detalhes apenas das 5 primeiras linhas
            print(f"\nLinha {lines_processed}:")
            print(f"Conteúdo da linha: {line.strip()}")
            print(f"Posições 109-110 (índices 108-110): '{operacao}'")
            print(f"Operação encontrada está na lista? {'Sim' if operacao in bank_operations else 'Não'}")
        
        if operacao in bank_operations:
            processed_lines.append(line)
            lines_kept += 1
    
    processed_lines.append(lines[-1])  # Mantém a última linha
    
    print(f"\nResumo do Processamento:")
    print(f"Total de linhas processadas: {lines_processed}")
    print(f"Total de linhas mantidas: {lines_kept}")
    print(f"Percentual mantido: {(lines_kept/lines_processed*100):.2f}%")
    
    # Se não foi especificado diretório de saída, usa o diretório do arquivo original
    if output_dirs is None:
        output_dirs = [os.path.dirname(file_path)]
    
    success = True
    base_name = os.path.basename(file_path)
    name_without_ext = os.path.splitext(base_name)[0]
    ext = os.path.splitext(base_name)[1]
    
    # Salva o arquivo processado em todos os diretórios especificados
    for output_dir in output_dirs:
        try:
            if output_dir and os.path.exists(output_dir):
                # Usa o mesmo timestamp para o arquivo processado
                output_path = os.path.join(output_dir, f"{name_without_ext}_{timestamp}_alterado{ext}")
                with open(output_path, 'w', encoding='utf-8') as file:
                    file.writelines(processed_lines)
                print(f"Arquivo processado salvo em: {output_path}")
            else:
                print(f"Diretório de saída não encontrado: {output_dir}")
                success = False
        except Exception as e:
            print(f"Erro ao salvar arquivo em {output_dir}: {str(e)}")
            success = False
    
    if success:
        # Registra o processamento com o nome do arquivo original
        register_processed_file(base_name)
        
        print(f"\nResultado Final:")
        print(f"Arquivo processado como: {banco}")
        print(f"{'='*80}\n")
    
    return success

def register_processed_file(filename):
    """Registra um arquivo processado no arquivo de log"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('processed_files.md', 'a', encoding='utf-8') as file:
        file.write(f"- {filename} (processado em {current_time})\n")

def should_process_file(filename):
    """Verifica se um arquivo deve ser processado"""
    # Ignora qualquer arquivo que contenha underscore
    return "_" not in filename

def process_directory(directory, output_dirs=None):
    """Processa todos os arquivos .RET em um diretório"""
    try:
        # Lista todos os arquivos .RET (case insensitive) que não têm underscore
        ret_files = [f for f in os.listdir(directory) 
                    if f.upper().endswith('.RET') and should_process_file(f)]
        
        for filename in ret_files:
            # Verifica se o arquivo já foi processado
            if is_file_processed(filename):
                print(f"Arquivo {filename} já foi processado anteriormente. Pulando...")
                continue
            
            # Processa o arquivo
            file_path = os.path.join(directory, filename)
            if process_cnab_file(file_path, output_dirs):
                print(f"\nArquivo {filename} processado com sucesso!")
            else:
                print(f"\nErro ao processar o arquivo {filename}")
    except Exception as e:
        print(f"Erro ao processar diretório {directory}: {str(e)}")

def is_file_processed(filename):
    try:
        with open('processed_files.md', 'r', encoding='utf-8') as file:
            content = file.read()
            return filename in content
    except FileNotFoundError:
        return False

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
