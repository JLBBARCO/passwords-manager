import json
import os
from src.lib.crypto import get_crypto_manager
from src.lib.system import prepare_local_data_file

class AddPassword:
    def __init__(self):
        self.json_file = str(prepare_local_data_file('passwords.json'))
        self.crypto = get_crypto_manager()
    
    def add_password(self, address, user, password):
        """Add a new password in JSON file if not exist"""
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            else:
                data = []

            if isinstance(data, dict) and 'passwords' in data:
                passwords = data['passwords']
            elif isinstance(data, list):
                passwords = data
            else:
                passwords = []
            
            address_stripped = address.strip()
            user_stripped = user.strip()
            password_stripped = password.strip()
            
            # Criptografa a senha antes de salvar
            encrypted_password = self.crypto.encrypt_password(password_stripped)

            # Verifica se já existe com o mesmo endereço e usuário
            for entry in passwords:
                entry_address = str(entry.get('Address', entry.get('address', ''))).strip()
                entry_user = str(entry.get('User', entry.get('user', ''))).strip()
                if entry_address == address_stripped and entry_user == user_stripped:
                    return False
            
            new_entry = {
                'Address': address_stripped,
                'User': user_stripped,
                'Password': encrypted_password  # Salva a senha criptografada
            }

            passwords.append(new_entry)

            if isinstance(data, dict) and 'passwords' in data:
                data['passwords'] = passwords
            else:
                data = passwords
            
            with open(self.json_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar senha: {e}")
            return False