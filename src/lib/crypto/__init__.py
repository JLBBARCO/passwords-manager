from cryptography.fernet import Fernet
import os


class CryptoManager:
    """Gerencia a criptografia e descriptografia de senhas usando Fernet (AES)"""
    
    def __init__(self, key_file='encryption.key'):
        """
        Inicializa o gerenciador de criptografia.
        
        Args:
            key_file: Nome do arquivo onde a chave será armazenada
        """
        self.key_file = key_file
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)
    
    def _load_or_generate_key(self):
        """Carrega a chave existente ou gera uma nova"""
        if os.path.exists(self.key_file):
            # Carrega a chave existente
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            # Gera uma nova chave
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt_password(self, password: str) -> str:
        """
        Criptografa uma senha.
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Senha criptografada em formato string
        """
        if not password:
            return ""
        
        try:
            # Converte a senha para bytes, criptografa e retorna como string
            encrypted_bytes = self.cipher.encrypt(password.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            print(f"Erro ao criptografar senha: {e}")
            return password
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """
        Descriptografa uma senha.
        
        Args:
            encrypted_password: Senha criptografada
            
        Returns:
            Senha em texto plano
        """
        if not encrypted_password:
            return ""
        
        try:
            # Converte a string para bytes, descriptografa e retorna como string
            decrypted_bytes = self.cipher.decrypt(encrypted_password.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            # Se falhar na descriptografia, pode ser que a senha não esteja criptografada
            # Retorna a senha original (útil para migração de dados antigos)
            print(f"Aviso: Não foi possível descriptografar a senha: {e}")
            return encrypted_password
    
    def is_encrypted(self, text: str) -> bool:
        """
        Verifica se um texto está criptografado.
        
        Args:
            text: Texto a ser verificado
            
        Returns:
            True se o texto parecer estar criptografado, False caso contrário
        """
        if not text:
            return False
        
        try:
            # Tenta descriptografar - se funcionar, está criptografado
            self.cipher.decrypt(text.encode('utf-8'))
            return True
        except:
            return False


# Instância global do gerenciador de criptografia
_crypto_manager = None


def get_crypto_manager():
    """Retorna a instância global do gerenciador de criptografia"""
    global _crypto_manager
    if _crypto_manager is None:
        _crypto_manager = CryptoManager()
    return _crypto_manager
