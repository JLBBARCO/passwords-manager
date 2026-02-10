
import tkinter as _tk

def copy_to_clipboard(text: str) -> bool:
	"""Copia o texto para a área de transferência usando tkinter.

	Retorna True se a cópia for bem-sucedida, caso contrário False.
	"""
	try:
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
