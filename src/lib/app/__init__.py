import customtkinter as ctk
import tkinter as tk
from src.lib.read_passwords import PasswordLoader
from src.lib.type_window import TypeWindow
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

padMain = 10
REPO_SLUG = 'JLBBARCO/passwords-manager'


def _sanitize_version(version_text):
    return str(version_text or '').strip().lstrip('v')


def _read_version_file(base_path):
    for filename in ('VERSION', 'version.txt'):
        candidate = Path(base_path) / filename
        if candidate.exists():
            return _sanitize_version(candidate.read_text(encoding='utf-8').strip())
    return ''


def _get_app_version():
    for env_name in ('PASSWORDS_MANAGER_VERSION', 'APP_VERSION'):
        env_value = _sanitize_version(os.environ.get(env_name, ''))
        if env_value:
            return env_value

    if getattr(sys, 'frozen', False):
        runtime_dir = Path(sys.executable).resolve().parent
        runtime_version = _read_version_file(runtime_dir)
        if runtime_version:
            return runtime_version

    source_version = _read_version_file(Path(__file__).resolve().parent)
    if source_version:
        return source_version

    try:
        repo_root = Path(__file__).resolve().parent
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return _sanitize_version(result.stdout)
    except Exception:
        pass

    return '0.0.0'


APP_VERSION = _get_app_version()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Passwords Manager')

        # Make the main window responsive
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.password_loader = PasswordLoader(self)

        self.status_var = ctk.StringVar(value=self.password_loader.status_message)

        self.textTitle = ctk.CTkLabel(self, textvariable=self.status_var)
        self.textTitle.grid(row=0, column=0, columnspan=3, padx=padMain, pady=padMain, sticky="ew")

        self.SearchBar = ctk.CTkEntry(self, placeholder_text='Search')
        self.SearchBar.grid(row=1, column=0, columnspan=2, padx=padMain, pady=padMain, sticky="ew")
        self.SearchButton = ctk.CTkButton(self, text='Search', command=self.search)
        self.SearchButton.grid(row=1, column=2, padx=padMain, pady=padMain)

        # Table area with both vertical and horizontal scrolling
        self.table_container = ctk.CTkFrame(self)
        self.table_container.grid(row=2, column=0, columnspan=3, padx=padMain, pady=padMain, sticky="nsew")

        # Use the same background color as the table frame to avoid white canvas gaps
        table_bg = self._apply_appearance_mode(self.table_container.cget("fg_color"))
        self.table_canvas = tk.Canvas(
            self.table_container,
            height=120,
            highlightthickness=0,
            bd=0,
            bg=table_bg,
        )
        self.table_canvas.grid(row=0, column=0, sticky="nsew")

        self.table_scroll_y = ctk.CTkScrollbar(self.table_container, orientation="vertical",
                               command=self.table_canvas.yview)
        self.table_scroll_y.grid(row=0, column=1, sticky="ns")

        self.table_scroll_x = ctk.CTkScrollbar(self.table_container, orientation="horizontal",
                               command=self.table_canvas.xview)
        self.table_scroll_x.grid(row=1, column=0, sticky="ew")

        self.table_container.grid_rowconfigure(0, weight=1)
        self.table_container.grid_columnconfigure(0, weight=1)

        self.table_canvas.configure(yscrollcommand=self.table_scroll_y.set, xscrollcommand=self.table_scroll_x.set)

        self.table_content = ctk.CTkFrame(self.table_canvas)
        self.table_window_id = self.table_canvas.create_window((0, 0), window=self.table_content, anchor="nw")
        self.table_content.bind("<Configure>", self._update_table_scrollregion)
        self.table_canvas.bind("<Configure>", self._on_table_canvas_configure)

        # Keep table columns expanding consistently
        self.table_content.grid_columnconfigure(0, weight=1)
        self.table_content.grid_columnconfigure(1, weight=1)
        self.table_content.grid_columnconfigure(2, weight=1)

        # Keep compatibility with existing rendering code
        self.showTable = self.table_content

        self.showTableTitleAddress = ctk.CTkLabel(self.showTable, text='Address')
        self.showTableTitleAddress.grid(row=0, column=0, padx=padMain, pady=padMain)
        self.showTableTitleUser = ctk.CTkLabel(self.showTable, text='User')
        self.showTableTitleUser.grid(row=0, column=1, padx=padMain, pady=padMain)
        self.showTableTitlePassword = ctk.CTkLabel(self.showTable, text='Password')
        self.showTableTitlePassword.grid(row=0, column=2, padx=padMain, pady=padMain)

        self.loading_label = ctk.CTkLabel(self.showTable, text="Changing Data...")
        self.loading_label.grid(row=1, column=0, columnspan=3, padx=padMain, pady=padMain)

        self.buttonRemove = ctk.CTkButton(self, text='Remove', command=self.remove, state="disabled")
        self.buttonAdd = ctk.CTkButton(self, text='Add', command=self.add, state="disabled")
        self.buttonRemove.grid(row=3, column=0, padx=padMain, pady=padMain)
        self.buttonAdd.grid(row=3, column=2, padx=padMain, pady=padMain)

        self.areaGenerate = ctk.CTkFrame(self)
        self.areaGenerate.grid(row=4, column=0, columnspan=3, padx=padMain, pady=padMain, sticky="ew")
        # Keep action buttons centered while the container adapts
        self.areaGenerate.grid_columnconfigure(0, weight=1)
        self.areaGenerate.grid_columnconfigure(1, weight=0)
        self.areaGenerate.grid_columnconfigure(2, weight=1)
        self.buttonGenerateSimplePassword = ctk.CTkButton(
            self.areaGenerate, text='Generate a Simple Password', command=self.simplePassword)
        self.buttonGenerateSimplePassword.grid(row=0, column=1, padx=padMain, pady=padMain)
        self.buttonGenerateComplexPassword = ctk.CTkButton(
            self.areaGenerate, text='Generate a Complex Password', command=self.complexPassword)
        self.buttonGenerateComplexPassword.grid(row=1, column=1, padx=padMain, pady=padMain)

        # Non-GUI generation controls removed to avoid overlapping widgets

        self.areaPrintPassword = None

        self._bind_table_mousewheel_events()

        self.check_loading_status()

    def _parse_version(self, version_text):
        cleaned = (version_text or '').strip().lower().replace('v', '')
        parts = []
        for token in cleaned.split('.'):
            digits = ''.join(character for character in token if character.isdigit())
            parts.append(int(digits) if digits else 0)
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:3])

    def _latest_release_version(self):
        api_url = f'https://api.github.com/repos/{REPO_SLUG}/releases/latest'
        request = Request(api_url, headers={'User-Agent': 'passwords-manager'})
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode('utf-8'))
        tag_name = str(payload.get('tag_name', '')).strip()
        if not tag_name:
            raise ValueError('Versão mais recente não encontrada no GitHub.')
        return tag_name.replace('v', '')

    def check_for_updates(self):
        latest_version = self._latest_release_version()
        has_update = self._parse_version(latest_version) > self._parse_version(APP_VERSION)
        return has_update, latest_version

    def run_update(self):
        system_name = platform.system()

        if system_name == 'Windows':
            if not shutil.which('winget'):
                raise RuntimeError('winget não encontrado neste sistema.')
            subprocess.Popen(['winget', 'upgrade', 'JLBBARCO.PasswordsManager'])
            return 'winget'

        if system_name in ('Darwin', 'Linux'):
            if not shutil.which('brew'):
                raise RuntimeError('Homebrew não encontrado neste sistema.')
            subprocess.Popen(['brew', 'upgrade', 'passwords-manager'])
            return 'brew'

        raise RuntimeError(f'Sistema não suportado para atualização automática: {system_name}')

    def check_updates_and_prompt(self):
        from tkinter import messagebox
        try:
            has_update, latest_version = self.check_for_updates()
            if not has_update:
                messagebox.showinfo('Passwords Manager', f'Você já está na versão mais recente ({APP_VERSION}).')
                return

            should_update = messagebox.askyesno(
                'Passwords Manager',
                (
                    f'Nova versão encontrada: {latest_version}\n'
                    f'Versão atual: {APP_VERSION}\n\n'
                    'Deseja iniciar a atualização agora?'
                ),
            )
            if not should_update:
                return

            updater = self.run_update()
            messagebox.showinfo(
                'Passwords Manager',
                f'Comando de atualização disparado via {updater}.',
            )
        except (URLError, HTTPError, ValueError, RuntimeError) as exception:
            messagebox.showerror('Passwords Manager', f'Não foi possível atualizar:\n{exception}')
        except Exception as exception:
            messagebox.showerror('Passwords Manager', f'Erro inesperado:\n{exception}')

    def _update_table_scrollregion(self, _event=None):
        self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))

    def _on_table_canvas_configure(self, event):
        # Expand with the window, but keep horizontal scroll for wide content
        required_width = self.table_content.winfo_reqwidth()
        self.table_canvas.itemconfigure(self.table_window_id, width=max(event.width, required_width))
        self._update_table_scrollregion()

    def _bind_table_mousewheel_events(self):
        for widget in (self.table_container, self.table_canvas, self.table_content):
            widget.bind("<Enter>", self._on_table_mouse_enter)
            widget.bind("<Leave>", self._on_table_mouse_leave)

    def _on_table_mouse_enter(self, _event=None):
        self.bind_all("<MouseWheel>", self._on_table_mousewheel)
        self.bind_all("<Shift-MouseWheel>", self._on_table_shift_mousewheel)
        self.bind_all("<Button-4>", self._on_table_mousewheel)
        self.bind_all("<Button-5>", self._on_table_mousewheel)
        self.bind_all("<Shift-Button-4>", self._on_table_shift_mousewheel)
        self.bind_all("<Shift-Button-5>", self._on_table_shift_mousewheel)

    def _on_table_mouse_leave(self, _event=None):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Shift-MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")
        self.unbind_all("<Shift-Button-4>")
        self.unbind_all("<Shift-Button-5>")

    def _on_table_mousewheel(self, event):
        if getattr(event, 'num', None) == 4:
            step = -1
        elif getattr(event, 'num', None) == 5:
            step = 1
        else:
            delta = int(getattr(event, 'delta', 0))
            if delta == 0:
                return
            step = -int(delta / 120) if abs(delta) >= 120 else (-1 if delta > 0 else 1)
        self.table_canvas.yview_scroll(step, "units")

    def _on_table_shift_mousewheel(self, event):
        if getattr(event, 'num', None) == 4:
            step = -1
        elif getattr(event, 'num', None) == 5:
            step = 1
        else:
            delta = int(getattr(event, 'delta', 0))
            if delta == 0:
                return
            step = -int(delta / 120) if abs(delta) >= 120 else (-1 if delta > 0 else 1)
        self.table_canvas.xview_scroll(step, "units")

    def _copy_table_value(self, value):
        from src.lib.copy import Copy
        text = str(value)
        if Copy.copy_to_clipboard(text):
            self.status_var.set(f"Copied: {text}")
        else:
            self.status_var.set("Error copying value")

    def _create_clickable_cell(self, row, column, value):
        label = ctk.CTkLabel(self.showTable, text=str(value))
        label.grid(row=row, column=column, padx=padMain, pady=padMain)
        label.bind("<Button-1>", lambda _event, v=value: self._copy_table_value(v))
        return label

    def check_loading_status(self):
        if self.password_loader.loading_thread and self.password_loader.loading_thread.is_alive():
            self.after(100, self.check_loading_status)
        else:
            # Executa o callback na thread principal
            self.on_data_loaded()

    def update_status(self, message):
        self.status_var.set(message)

    def on_data_loaded(self):
        self.status_var.set(self.password_loader.status_message)
        # Habilita botões se carregado
        if self.password_loader.data_loaded:
            self.buttonRemove.configure(state="normal")
            self.buttonAdd.configure(state="normal")
            self.reload_table()
        else:
            if getattr(self, 'loading_label', None) and self.loading_label.winfo_exists():
                self.loading_label.destroy()
            self.ShowError = ctk.CTkLabel(self.showTable, text=self.password_loader.status_message)
            self.ShowError.grid(row=1, column=0, columnspan=3, padx=padMain, pady=padMain)

    def search(self):
        q = (self.SearchBar.get() or '').strip().lower()
        for widget in self.showTable.winfo_children()[3:]:
            widget.destroy()

        results = []
        for record in self.password_loader.all_data:
            addr = str(record.get('Address', record.get('address', ''))).strip()
            user = str(record.get('User', record.get('user', ''))).strip()
            pwd = str(record.get('Password', record.get('password', ''))).strip()
            if not q or q in addr.lower() or q in user.lower() or q in pwd.lower():
                results.append((addr, user, pwd))

        if not results:
            ctk.CTkLabel(self.showTable, text='No results found').grid(
                row=1, column=0, columnspan=3, padx=padMain, pady=padMain)
            return

        for idx, (addr, user, pwd) in enumerate(results, start=1):
            self._create_clickable_cell(idx, 0, addr)
            self._create_clickable_cell(idx, 1, user)
            self._create_clickable_cell(idx, 2, pwd)

    def add(self):
        add_window = TypeWindow(TitleWindow='Add Password', Address=True, User=True, Password=True)
        add_window.focus()
        self.wait_window(add_window)
        if add_window.address and add_window.user and add_window.password:
            from src.lib.add import AddPassword
            if AddPassword().add_password(add_window.address, add_window.user, add_window.password):
                # reload data asynchronously
                self.password_loader.start_loading()
            else:
                # still refresh to reflect any external changes
                self.password_loader.start_loading()

    def remove(self):
        remove_window = TypeWindow(TitleWindow='Remove Password', Address=True, User=True, Password=False)
        self.wait_window(remove_window)
        if remove_window.address and remove_window.user:
            from src.lib.remove import RemovePassword
            if RemovePassword().remove_password(remove_window.address, remove_window.user):
                self.password_loader.start_loading()
            else:
                self.password_loader.start_loading()

    def simplePassword(self):
        from src.lib.generate_password import GenerateSimplePassword
        app = GenerateSimplePassword()
        if app.password:
            self.show_generated_password(app.password)

    def complexPassword(self):
        from src.lib.generate_password import GenerateComplexPassword
        app = GenerateComplexPassword()
        if app.password:
            self.show_generated_password(app.password)

    def show_generated_password(self, password):
        if self.areaPrintPassword and self.areaPrintPassword.winfo_exists():
            self.areaPrintPassword.destroy()
        self.areaPrintPassword = ctk.CTkFrame(self.areaGenerate)
        self.areaPrintPassword.grid(row=0, rowspan=2, column=2, padx=padMain, pady=padMain, sticky="w")
        ctk.CTkLabel(self.areaPrintPassword, text=password, fg_color='gray30', padx=10, pady=5)\
            .grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        ctk.CTkButton(self.areaPrintPassword, text='Copy', width=60,
                      command=lambda: self.copy_password(password))\
            .grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(self.areaPrintPassword, text='Save', width=60,
                      command=lambda: self.save_password(password))\
            .grid(row=1, column=1, padx=5, pady=5)

    def copy_password(self, password):
        from src.lib.copy import Copy
        if Copy.copy_to_clipboard(password):
            print("Copy password successfully!")
        else:
            print("Error on copy password")

    def save_password(self, password):
        save_window = TypeWindow(TitleWindow='Save Generated Password', Address=True, User=True, Password=False)
        self.wait_window(save_window)
        if save_window.address and save_window.user:
            from src.lib.add import AddPassword
            if AddPassword().add_password(save_window.address, save_window.user, password):
                print("Saved password successfully!")
                self.password_loader.start_loading()
            else:
                print("Password already exists!")

    def reload_table(self):
        if getattr(self, 'loading_label', None) and self.loading_label.winfo_exists():
            self.loading_label.destroy()
        if getattr(self, 'ShowError', None) and self.ShowError.winfo_exists():
            self.ShowError.destroy()
        # Clear only data lines
        for widget in self.showTable.winfo_children()[3:]:
            widget.destroy()
        if not self.password_loader.data_loaded:
            self.ShowError = ctk.CTkLabel(self.showTable, text=self.password_loader.status_message)
            self.ShowError.grid(row=1, column=0, columnspan=3, padx=padMain, pady=padMain)
            return
        try:
            for idx, record in enumerate(self.password_loader.all_data, start=1):
                self._create_clickable_cell(idx, 0, record['Address'].strip())
                self._create_clickable_cell(idx, 1, record['User'].strip())
                self._create_clickable_cell(idx, 2, record['Password'].strip())
        except Exception as e:
            ctk.CTkLabel(self.showTable, text=f'Error: {str(e)}').grid(row=1, column=0, columnspan=3, padx=padMain, pady=padMain)

if __name__ == '__main__':
    app = App()
    app.mainloop()