from random import choice
import src.lib.type_window as type_window


def generate_simple_password(length: int) -> str:
    """Gera uma senha simples (letras + dígitos) sem usar GUI."""
    try:
        length = int(length)
        if length <= 0:
            raise ValueError
    except Exception:
        return 'Invalid length'
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(choice(characters) for _ in range(length))


def generate_complex_password(length: int) -> str:
    """Gera uma senha complexa (inclui símbolos) sem usar GUI."""
    try:
        length = int(length)
        if length <= 0:
            raise ValueError
    except Exception:
        return 'Invalid length'
    caracteres = (
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e', 'F', 'f', 'G', 'g',
        'H', 'h', 'I', 'i', 'J', 'j', 'K', 'k', 'L', 'l', 'M', 'm', 'N', 'n',
        'O', 'o', 'P', 'p', 'Q', 'q', 'R', 'r', 'S', 's', 'T', 't', 'U', 'u',
        'V', 'v', 'W', 'w', 'X', 'x', 'Y', 'y', 'Z', 'z',
        '?', '!', '@', '#', '$', '%', '/', '+', '-', '_', '=', '*', '&', '<',
        '>', '(', ')', '[', ']', '{', '}', 'Ç', 'ç'
    )
    return ''.join(choice(caracteres) for _ in range(length))


class GenerateSimplePassword(type_window.TypeWindow):
    def __init__(self, length=None):
        # Se length for fornecido, não abrir GUI — gera direto
        if length is not None:
            self.password = generate_simple_password(length)
            return
        super().__init__(Address=False, User=False, Password=False, TitleWindow='Generate Simple Password', Characters=True)
        self.password = None

    def submit(self):
        length = self.charactersEntry.get()
        try:
            length = int(length)
            if length <= 0:
                raise ValueError
            characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            self.password = ''.join(choice(characters) for _ in range(length))
        except ValueError:
            self.password = 'Invalid length'
        # Instead of destroying the window, show generated area with actions
        try:
            self.display_generated_section(self.password)
        except Exception:
            # Fallback: destroy if display is not available
            self.destroy()


class GenerateComplexPassword(type_window.TypeWindow):
    def __init__(self, length=None):
        if length is not None:
            self.password = generate_complex_password(length)
            return
        super().__init__(Address=False, User=False, Password=False, TitleWindow='Generate Complex Password', Characters=True)
        self.password = None

    def submit(self):
        length = self.charactersEntry.get()
        try:
            length = int(length)
            if length <= 0:
                raise ValueError
            caracteres = (
                '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                'A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e', 'F', 'f', 'G', 'g',
                'H', 'h', 'I', 'i', 'J', 'j', 'K', 'k', 'L', 'l', 'M', 'm', 'N', 'n',
                'O', 'o', 'P', 'p', 'Q', 'q', 'R', 'r', 'S', 's', 'T', 't', 'U', 'u',
                'V', 'v', 'W', 'w', 'X', 'x', 'Y', 'y', 'Z', 'z',
                '?', '!', '@', '#', '$', '%', '/', '+', '-', '_', '=', '*', '&', '<',
                '>', '(', ')', '[', ']', '{', '}', 'Ç', 'ç'
            )
            self.password = ''.join(choice(caracteres) for _ in range(length))
        except ValueError:
            self.password = 'Invalid length'
        try:
            self.display_generated_section(self.password)
        except Exception:
            self.destroy()