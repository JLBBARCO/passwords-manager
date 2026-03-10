from typing import Tuple

from src.lib.external_libs import ctk

program_title = 'Uninstall Passwords Manager'
progress = 20

class Uninstall(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(program_title)

        self.label = ctk.CTkLabel(self, text=program_title)
        self.label.grid(padx=10, pady=5, row=0, columnspan=3)

        self.container_progress = ctk.CTkLabel(self, text='')
        self.container_progress.grid(padx=20, pady=50, row=1, columnspan=3)

        self.progress_bar = ctk.CTkProgressBar(self.container_progress, width=250)
        self.progress_bar.set(progress)
        self.progress_bar.grid(padx=10, pady=50, row=0, columnspan=2)

        self.progress_counter = ctk.CTkLabel(self.container_progress, text=f'{progress}%')
        self.progress_counter.grid(row=0, column=2)

        self.container_buttons = ctk.CTkLabel(self, text='')
        self.container_buttons.grid(padx=10, pady=25, row=2, column=1, columnspan=2)

        self.uninstall_button = ctk.CTkButton(self.container_buttons, text='Uninstall', command=self.uninstall)
        self.uninstall_button.grid(padx=10, row=0, column=0)

        self.cancel_button = ctk.CTkButton(self.container_buttons, text='Cancel', command=self.cancel)
        self.cancel_button.grid(padx=10, row=0, column=1)

    def uninstall(self):
        self.destroy()

    def cancel(self):
        self.destroy()

if __name__ == '__main__':
    app = Uninstall()
    app.mainloop()