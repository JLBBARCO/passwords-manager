import customtkinter as ctk
from src.lib.uninstall import detect_installation_path, run_uninstall
import threading
from pathlib import Path
from tkinter import messagebox

program_title = 'Uninstall Passwords Manager'

class Uninstall(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(program_title)
        self.uninstalling = False
        self.installation_path = Path(detect_installation_path())

        self.label = ctk.CTkLabel(self, text=program_title)
        self.label.grid(padx=10, pady=5, row=0, columnspan=2)

        self.container_progress = ctk.CTkLabel(self, text='')
        self.container_progress.grid(padx=20, pady=50, row=1, columnspan=2)

        self.progress_bar = ctk.CTkProgressBar(self.container_progress, width=250)
        self.progress_bar.set(0)
        self.progress_bar.grid(padx=10, pady=50, row=0, columnspan=2)

        self.progress_counter = ctk.CTkLabel(self.container_progress, text='0%')
        self.progress_counter.grid(row=0, column=2)

        self.status = ctk.CTkLabel(self.container_progress, text='Pronto para desinstalar')
        self.status.grid(row=1, column=0, columnspan=3)

        self.container_buttons = ctk.CTkLabel(self, text='')
        self.container_buttons.grid(padx=10, pady=25, row=2, column=0, columnspan=2)

        self.uninstall_button = ctk.CTkButton(self.container_buttons, text='Uninstall', command=self.uninstall)
        self.uninstall_button.grid(padx=10, row=0, column=0)

        self.cancel_button = ctk.CTkButton(self.container_buttons, text='Cancel', command=self.cancel)
        self.cancel_button.grid(padx=10, row=0, column=1)

    def _update_progress(self, current, total, label):
        percent = int((current / total) * 100) if total > 0 else 100
        self.progress_bar.set(current / total if total > 0 else 1)
        self.progress_counter.configure(text=f'{percent}%')
        self.status.configure(text=f'Removendo: {label}')

    def _set_controls_state(self, state):
        self.uninstall_button.configure(state=state)
        self.cancel_button.configure(state=state)

    def uninstall(self):
        if self.uninstalling:
            return

        if not self.installation_path.exists():
            messagebox.showerror(
                program_title,
                f'Instalação não encontrada em:\n{self.installation_path}',
            )
            return

        self.uninstalling = True
        self._set_controls_state('disabled')
        self.status.configure(text='Iniciando desinstalação...')
        self.progress_bar.set(0)
        self.progress_counter.configure(text='0%')
        threading.Thread(target=self._uninstall_worker, daemon=True).start()

    def _uninstall_worker(self):
        try:
            target = detect_installation_path(self.installation_path)

            def callback(current, total, label):
                self.after(0, self._update_progress, current, total, label)

            result = run_uninstall(target, callback)

            self.after(0, self.progress_bar.set, 1)
            self.after(0, lambda: self.progress_counter.configure(text='100%'))
            self.after(0, lambda: self.status.configure(text='Desinstalação concluída'))
            self.after(
                0,
                messagebox.showinfo,
                program_title,
                (
                    f"Itens removidos: {result['removed']}\n"
                    f"Itens ignorados: {result.get('skipped', 0)}"
                    + (
                        '\nLimpeza final agendada em segundo plano.'
                        if result.get('cleanup_scheduled')
                        else ''
                    )
                ),
            )
            self.after(0, self.destroy)
        except Exception as exception:
            self.after(0, lambda: self.status.configure(text='Falha na desinstalação'))
            self.after(0, messagebox.showerror, program_title, f'Desinstalação falhou:\n{exception}')
        finally:
            self.uninstalling = False
            self.after(0, self._set_controls_state, 'normal')

    def cancel(self):
        if self.uninstalling:
            return
        self.destroy()

if __name__ == '__main__':
    app = Uninstall()
    app.mainloop()