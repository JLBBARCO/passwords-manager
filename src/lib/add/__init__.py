import pandas as pd
import json
import os

class AddPassword:
    def __init__(self):
        self.json_file = 'passwords.json'
    
    def add_password(self, address, user, password):
        """Add a new password in JSON file if not exist"""
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            else:
                data = []
            
            df = pd.DataFrame(data)
            
            if df.empty:
                df = pd.DataFrame(columns=['Address', 'User', 'Password'])
            elif 'Address' not in df.columns:
                df = pd.DataFrame(columns=['Address', 'User', 'Password'])
            
            if not df.empty:
                df['Address'] = df['Address'].str.strip()
                df['User'] = df['User'].str.strip()
                df['Password'] = df['Password'].str.strip()
            
            address_stripped = address.strip()
            user_stripped = user.strip()
            password_stripped = password.strip()
            
            if not df.empty:
                existing = df[
                    (df['Address'] == address_stripped) & 
                    (df['User'] == user_stripped) & 
                    (df['Password'] == password_stripped)
                ]
                
                if not existing.empty:
                    return False
            
            new_entry = {
                'Address': address_stripped,
                'User': user_stripped,
                'Password': password_stripped
            }
            
            data = df.to_dict('records')
            data.append(new_entry)
            
            with open(self.json_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar senha: {e}")
            return False