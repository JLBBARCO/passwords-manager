"""
Script de Migração - Criptografia de Senhas Existentes

Este script criptografa todas as senhas existentes no arquivo passwords.json.
Execute-o apenas UMA VEZ após instalar o sistema de criptografia.
"""

from src.lib.external_libs import json, os
from src.lib.crypto import get_crypto_manager


def migrate_passwords():
    """Migra senhas não criptografadas para o formato criptografado"""
    json_file = 'passwords.json'
    
    # Verifica se o arquivo existe
    if not os.path.exists(json_file):
        print("Nenhum arquivo passwords.json encontrado. Nada a migrar.")
        return
    
    # Carrega os dados
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Determina o formato
    if isinstance(data, list):
        passwords_list = data
    elif isinstance(data, dict) and 'passwords' in data:
        passwords_list = data['passwords']
    else:
        print("Formato de arquivo desconhecido.")
        return
    
    # Inicializa o gerenciador de criptografia
    crypto = get_crypto_manager()
    
    # Verifica se já está criptografado
    if passwords_list:
        sample_password = passwords_list[0].get('Password', '') or passwords_list[0].get('password', '')
        if crypto.is_encrypted(sample_password):
            print("As senhas já parecem estar criptografadas. Nenhuma ação necessária.")
            return
    
    # Cria backup antes de migrar
    backup_file = 'passwords_backup.json'
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Backup criado em: {backup_file}")
    
    # Criptografa todas as senhas
    migrated_count = 0
    for entry in passwords_list:
        if 'Password' in entry:
            entry['Password'] = crypto.encrypt_password(entry['Password'])
            migrated_count += 1
        elif 'password' in entry:
            entry['password'] = crypto.encrypt_password(entry['password'])
            migrated_count += 1
    
    # Salva os dados criptografados
    if isinstance(data, list):
        encrypted_data = passwords_list
    else:
        data['passwords'] = passwords_list
        encrypted_data = data
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(encrypted_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Migração concluída com sucesso!")
    print(f"✓ {migrated_count} senha(s) foram criptografadas.")
    print(f"✓ Backup salvo em: {backup_file}")
    print(f"\nSuas senhas agora estão protegidas com criptografia AES!")


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRAÇÃO DE SENHAS PARA FORMATO CRIPTOGRAFADO")
    print("=" * 60)
    print("\nEste script irá criptografar todas as suas senhas existentes.")
    print("Um backup será criado antes da migração.")
    
    resposta = input("\nDeseja continuar? (s/n): ")
    
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        migrate_passwords()
    else:
        print("\nMigração cancelada.")
