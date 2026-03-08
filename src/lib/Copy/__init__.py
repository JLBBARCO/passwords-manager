
import sys
import tkinter as _tk

def copy_to_clipboard(text: str) -> bool:
	"""Copia o texto para a área de transferência.
	
	Tenta usar xclip no Linux para evitar criar janelas Tk desnecessárias.
	Retorna True se a cópia for bem-sucedida, caso contrário False.
	"""
	try:
		# Tenta usar xclip no Linux primeiro (mais confiável)
		if sys.platform == 'linux':
			try:
				import subprocess
				process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
										stdin=subprocess.PIPE, 
										stdout=subprocess.DEVNULL, 
										stderr=subprocess.DEVNULL)
				process.communicate(input=str(text).encode('utf-8'))
				if process.returncode == 0:
					return True
			except (FileNotFoundError, Exception):
				# xclip not available, fallback to tk
				pass
		
		# Fallback para tkinter em todos os sistemas ou se xclip falhar
		root = _tk.Tk()
		root.withdraw()
		root.clipboard_clear()
		root.clipboard_append(str(text))
		# força a atualização da clipboard para que persista após destruir a janela
		root.update()
		root.destroy()
		return True
		
	except Exception as e:
		print(f"Erro ao copiar para clipboard: {e}")
		return False


class Copy:
	"""Compat layer: fornece a API `Copy.copy_to_clipboard(...)` usada no código legado."""
	@staticmethod
	def copy_to_clipboard(text: str) -> bool:
		return copy_to_clipboard(text)
