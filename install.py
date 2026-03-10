from typing import Tuple

import customtkinter as ctk

program_name = 'Install Passwords Manager'
installation_path = 'C:\Program Files\Passwords Manager'

class Install(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(program_name)

        self.label = ctk.CTkLabel(self, text=program_name)
        self.label.grid(padx=25, pady=25, row=0, columnspan=2)

        self.container_url = ctk.CTkLabel(self, text='')
        self.container_url.grid(padx=25, pady=25, row=1, columnspan=2)

        self.url_title = ctk.CTkLabel(self.container_url, text='Installation path: ')
        self.url_title.grid(padx=10, row=0, column=0)

        self.url_path = ctk.CTkLabel(self.container_url, text=installation_path, bg_color='green', corner_radius=8)
        self.url_path.grid(padx=10, row=0, column=1)

        self.url_select_button = ctk.CTkButton(self.container_url, text='Path', command=self.url_select)
        self.url_select_button.grid(padx=10, row=0, column=2)

        self.container_buttons = ctk.CTkLabel(self, text='')
        self.container_buttons.grid(pady=25, row=2, column=1)

        self.install_button = ctk.CTkButton(self.container_buttons, text='Install', command=self.install)
        self.install_button.grid(padx=10, row=0, column=1)

        self.cancel_button = ctk.CTkButton(self.container_buttons, text='Cancel', command=self.cancel)
        self.cancel_button.grid(padx=10, row=0, column=2)

    def url_select(self):
        self.test = ctk.CTkInputDialog(title=program_name, text=program_name)
        installation_path = self.test.get_input()
        self.url_path.configure(text=installation_path)
        self.url_path.update()

    def install(self):
        self.destroy()

    def cancel(self):
        self.destroy()

if __name__ == '__main__':
    app = Install()
    app.mainloop()