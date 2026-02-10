import json
import os

class RemovePassword:
    def __init__(self):
        self.json_file = 'passwords.json'

    def remove_password(self, address, user):
        """Remove password from JSON file by address and user"""
        try:
            if not os.path.exists(self.json_file):
                return False

            # Lê o arquivo JSON
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Verifica o formato dos dados
            passwords_list = self._get_passwords_list(data)
            initial_len = len(passwords_list)
            
            # Remove a entrada baseada em address e user
            address_stripped = address.strip()
            user_stripped = user.strip()
            
            if isinstance(data, list):
                # Formato: lista de dicionários
                filtered_data = [
                    entry for entry in data
                    if not (self._get_field(entry, 'address').strip() == address_stripped and 
                           self._get_field(entry, 'user').strip() == user_stripped)
                ]
                
                # Verifica se houve remoção
                if len(filtered_data) < len(data):
                    # Salva o arquivo atualizado
                    with open(self.json_file, 'w', encoding='utf-8') as f:
                        json.dump(filtered_data, f, indent=2, ensure_ascii=False)
                    return True
                
            elif isinstance(data, dict) and 'passwords' in data:
                # Formato: dicionário com chave 'passwords'
                passwords = data['passwords']
                filtered_passwords = [
                    entry for entry in passwords
                    if not (self._get_field(entry, 'address').strip() == address_stripped and 
                           self._get_field(entry, 'user').strip() == user_stripped)
                ]
                
                if len(filtered_passwords) < len(passwords):
                    data['passwords'] = filtered_passwords
                    # Atualiza contagem se existir
                    if 'metadata' in data and 'count' in data['metadata']:
                        data['metadata']['count'] = len(filtered_passwords)
                    
                    with open(self.json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    return True
            
            return False
            
        except Exception as e:
            print(f'Error removing password: {str(e)}')
            return False
    
    def _get_passwords_list(self, data):
        """Extrai a lista de senhas do dado carregado"""
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'passwords' in data:
            return data['passwords']
        return []
    
    def _get_field(self, entry, field_name):
        """Obtém um campo do dicionário, tentando variações de capitalização"""
        # Tenta diferentes variações do nome do campo
        variations = [
            field_name.lower(),
            field_name.title(),
            field_name.upper(),
            field_name.capitalize()
        ]
        
        for variation in variations:
            if variation in entry:
                return str(entry[variation])
        
        # Se não encontrar, retorna string vazia
        return ""