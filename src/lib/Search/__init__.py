import json
import os


class Search:
    """Procura por uma query no arquivo `passwords.json` e retorna uma lista de tuplas
    (address, user, password) em `self.results`.
    """
    def __init__(self, query: str, json_file: str = 'passwords.json'):
        self.query = (query or '').strip()
        self.json_file = json_file
        self.results = []
        self.search_passwords()

    def search_passwords(self):
        if not os.path.exists(self.json_file):
            return
        
        try:
            # Lê o arquivo JSON
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extrai a lista de senhas baseado no formato
            passwords_list = self._extract_passwords_list(data)
            
            q = self.query.lower()
            
            for entry in passwords_list:
                # Obtém os campos com suporte para diferentes nomes
                addr = self._get_field(entry, 'Address').strip()
                user = self._get_field(entry, 'User').strip()
                pwd = self._get_field(entry, 'Password').strip()
                
                if q == '':
                    # Se query vazia, retorna todos
                    self.results.append((addr, user, pwd))
                else:
                    # Procura a query em qualquer campo
                    if (q in addr.lower() or 
                        q in user.lower() or 
                        q in pwd.lower()):
                        self.results.append((addr, user, pwd))
                        
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {e}")
        except Exception as e:
            print(f"Error searching passwords: {e}")
    
    def _extract_passwords_list(self, data):
        """Extrai a lista de senhas do dado carregado"""
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'passwords' in data:
            return data['passwords']
        else:
            # Formato desconhecido, retorna lista vazia
            return []
    
    def _get_field(self, entry, field_name):
        """Obtém um campo do dicionário, tentando variações de capitalização"""
        # Tenta diferentes variações do nome do campo
        variations = [
            field_name.lower(),      # 'address'
            field_name.title(),      # 'Address'
            field_name.upper(),      # 'ADDRESS'
            field_name.capitalize()  # 'Address'
        ]
        
        for variation in variations:
            if variation in entry:
                value = entry[variation]
                return str(value) if value is not None else ""
        
        # Campo não encontrado, retorna string vazia
        return ""