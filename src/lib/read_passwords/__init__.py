import pandas as pd
import threading
import time
import json
import os
from src.lib import converter

class PasswordLoader:

    def __init__(self, app_instance):
        self.app = app_instance
        self.data_loaded = False
        self.passwords_data = []
        self.status_message = "Initialization..."
        self.ErrorFileNotFound = "File Not Found"
        self.loading_thread = None
        self.start_loading()

    def load_data(self):
        try:
            self.status_message = "Loading passwords..."
            if hasattr(self.app, 'update_status'):
                self.app.after(0, lambda: self.app.update_status(self.status_message))
            time.sleep(1)
            
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
                    
            self.data_loaded = True
            self.status_message = f"{len(self.passwords_data)} passwords loaded successfully!"
            time.sleep(1)
            
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