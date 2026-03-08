import threading
import json
import os
from src.lib import converter
from src.lib.crypto import get_crypto_manager

class PasswordLoader:

    def __init__(self, app_instance):
        self.app = app_instance
        self.data_loaded = False
        self.passwords_data = []
        self.status_message = "Initialization..."
        self.ErrorFileNotFound = "File Not Found"
        self.loading_thread = None
        self.crypto = get_crypto_manager()
        self.start_loading()

    def load_data(self):
        try:
            self.status_message = "Loading passwords..."
            if hasattr(self.app, 'update_status'):
                self.app.after(0, lambda: self.app.update_status(self.status_message))
            
            # Verifica se o arquivo existe
            if not os.path.exists('passwords.json') and os.path.exists('passwords.csv'):
                converter.convertToCSV()
            elif not os.path.exists('passwords.json'):
                self.status_message = self.ErrorFileNotFound
                self.data_loaded = True  # Define como True mesmo sem dados
                if hasattr(self.app, 'after'):
                    self.app.after(0, self.app.on_data_loaded)
                return
            
            # Lê o arquivo JSON
            with open('passwords.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Converte os dados para o formato esperado
                if isinstance(data, list):
                    # Formato: lista de dicionários
                    self.passwords_data = data
                elif isinstance(data, dict) and 'passwords' in data:
                    # Formato: dicionário com chave 'passwords'
                    self.passwords_data = data['passwords']
                else:
                    # Outro formato - tenta converter
                    self.passwords_data = []
            
            # Verifica se as senhas precisam ser criptografadas (migração automática)
            needs_encryption = self._check_needs_encryption()
            
            if needs_encryption:
                self.status_message = "Migrando senhas para formato criptografado..."
                if hasattr(self.app, 'update_status'):
                    self.app.after(0, lambda: self.app.update_status(self.status_message))
                
                # Cria backup antes de migrar
                backup_file = 'passwords_backup_unencrypted.json'
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"✓ Backup criado em: {backup_file}")
                
                # Criptografa todas as senhas
                for entry in self.passwords_data:
                    if 'Password' in entry:
                        entry['Password'] = self.crypto.encrypt_password(entry['Password'])
                    elif 'password' in entry:
                        entry['password'] = self.crypto.encrypt_password(entry['password'])
                
                # Salva o arquivo com senhas criptografadas
                if isinstance(data, list):
                    encrypted_data = self.passwords_data
                else:
                    data['passwords'] = self.passwords_data
                    encrypted_data = data
                
                with open('passwords.json', 'w', encoding='utf-8') as f:
                    json.dump(encrypted_data, f, indent=2, ensure_ascii=False)
                
                print(f"✓ {len(self.passwords_data)} senha(s) migrada(s) para formato criptografado.")
                
                # Exclui o backup após migração bem-sucedida
                try:
                    os.remove(backup_file)
                    print(f"✓ Backup temporário excluído.")
                except Exception as e:
                    print(f"⚠ Aviso: Não foi possível excluir o backup: {e}")
                    
            # Descriptografa as senhas para uso na aplicação
            for entry in self.passwords_data:
                if 'Password' in entry:
                    entry['Password'] = self.crypto.decrypt_password(entry['Password'])
                elif 'password' in entry:
                    entry['password'] = self.crypto.decrypt_password(entry['password'])
                    
            self.data_loaded = True
            self.status_message = f"{len(self.passwords_data)} passwords loaded successfully!"
            
        except json.JSONDecodeError as e:
            self.status_message = f"Error reading JSON file: {e}"
            self.passwords_data = []
            self.data_loaded = True
        except Exception as e:
            self.status_message = f"Error to load data: {e}"
            self.passwords_data = []
            self.data_loaded = True
            
        if hasattr(self.app, 'after'):
            self.app.after(0, self.app.on_data_loaded)

    def start_loading(self):
        self.loading_thread = threading.Thread(target=self.load_data, daemon=True)
        self.loading_thread.start()

    @property
    def address(self):
        return [record.get('Address', record.get('address', '')) for record in self.passwords_data]

    @property
    def user(self):
        return [record.get('User', record.get('user', '')) for record in self.passwords_data]

    @property
    def password(self):
        return [record.get('Password', record.get('password', '')) for record in self.passwords_data]

    @property
    def all_data(self):
        return self.passwords_data
    
    def _check_needs_encryption(self):
        """
        Verifica se as senhas no arquivo precisam ser criptografadas.
        Retorna True se encontrar pelo menos uma senha não criptografada.
        """
        if not self.passwords_data:
            return False
        
        # Verifica a primeira senha para determinar se está criptografada
        for entry in self.passwords_data[:3]:  # Verifica até 3 entradas para mais confiança
            password = entry.get('Password', entry.get('password', ''))
            if password and not self.crypto.is_encrypted(password):
                return True
        
        return False