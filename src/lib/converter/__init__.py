import csv
import json
import os
from src.lib.crypto import get_crypto_manager
from src.lib.system import find_data_file, prepare_local_data_file

def convertToCSV(csv_file=None, json_file=None):
    """
    Converte CSV para JSON com criptografia de senhas.
    Retorna True se bem-sucedido, False caso contrário.
    Exclui o arquivo CSV após conversão bem-sucedida.
    """
    try:
        csv_file = str(csv_file or find_data_file('passwords.csv'))
        json_file = str(json_file or prepare_local_data_file('passwords.json'))
        
        if not os.path.exists(csv_file):
            print(f"Arquivo {csv_file} não encontrado.")
            return False
        
        # Inicializa o gerenciador de criptografia
        crypto = get_crypto_manager()
        
        # Read CSV and convert to list of dictionaries with encrypted passwords
        data = []
        with open(csv_file, 'r', encoding='utf-8', newline='') as csv_input:
            reader = csv.DictReader(csv_input, delimiter=';')
            for row in reader:
                encrypted_password = crypto.encrypt_password(str(row.get("Passwords", "")))
                entry = {
                    "Address": str(row.get("Address", "")),
                    "User": str(row.get("User", "")),
                    "Password": encrypted_password,
                }
                data.append(entry)

        # Write to JSON file with encrypted passwords
        with open(json_file, 'w', encoding='utf-8') as jsonFile:
            json.dump(data, jsonFile, indent=2, ensure_ascii=False)

        print(f"✓ Conversão concluída: {len(data)} senha(s) convertida(s) e criptografadas.")
        
        # Exclui o arquivo CSV após conversão bem-sucedida
        try:
            os.remove(csv_file)
            print(f"✓ Arquivo {csv_file} excluído com sucesso.")
        except Exception as e:
            print(f"⚠ Aviso: Não foi possível excluir {csv_file}: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro ao converter CSV para JSON: {e}")
        return False