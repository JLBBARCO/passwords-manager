import customtkinter as ctk
import tkinter as tk
from src.lib.read_passwords import PasswordLoader
from src.lib.type_window import TypeWindow

padMain = 10

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Passwords Manager')

        self.password_loader = PasswordLoader(self)

        self.status_var = ctk.StringVar(value=self.password_loader.status_message)

        self.main_frame = ctk.CTkFrame(self, width=250, height=250)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10)

        self.textTitle = ctk.CTkLabel(self.main_frame, textvariable=self.status_var)
        self.textTitle.grid(row=0, column=0, columnspan=3, padx=padMain, pady=padMain)

        self.SearchBar = ctk.CTkEntry(self.main_frame, placeholder_text='Search')
        self.SearchBar.grid(row=1, column=0, columnspan=2, pady=padMain)
        self.SearchButton = ctk.CTkButton(self.main_frame, text='Search', command=self.search)
        self.SearchButton.grid(row=1, column=2, pady=padMain)

        # Table area with both vertical and horizontal scrolling
        self.table_container = ctk.CTkFrame(self.main_frame)
        self.table_container.grid(row=2, column=0, columnspan=3, padx=padMain, pady=padMain, sticky="nsew")

        # Use the same background color as the table frame to avoid white canvas gaps
        table_bg = self._apply_appearance_mode(self.table_container.cget("fg_color"))
        self.table_canvas = tk.Canvas(
            self.table_container,
            width=500,
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

        self.buttonRemove = ctk.CTkButton(self.main_frame, text='Remove', command=self.remove, state="disabled")
        self.buttonAdd = ctk.CTkButton(self.main_frame, text='Add', command=self.add, state="disabled")
        self.buttonRemove.grid(row=3, column=0, padx=padMain, pady=padMain)
        self.buttonAdd.grid(row=3, column=2, padx=padMain, pady=padMain)

        self.areaGenerate = ctk.CTkFrame(self)
        self.areaGenerate.grid(row=1, column=0, columnspan=3, padx=padMain, pady=padMain)
        self.buttonGenerateSimplePassword = ctk.CTkButton(
            self.areaGenerate, text='Generate a Simple Password', command=self.simplePassword)
        self.buttonGenerateSimplePassword.grid(row=0, column=0, padx=padMain, pady=padMain)
        self.buttonGenerateComplexPassword = ctk.CTkButton(
            self.areaGenerate, text='Generate a Complex Password', command=self.complexPassword)
        self.buttonGenerateComplexPassword.grid(row=1, column=0, padx=padMain, pady=padMain)

        # Non-GUI generation controls removed to avoid overlapping widgets

        self.areaPrintPassword = None

        self.check_loading_status()

    def _update_table_scrollregion(self, _event=None):
        self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))

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
        self.areaPrintPassword.grid(row=0, rowspan=2, column=1, padx=padMain, pady=padMain)
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