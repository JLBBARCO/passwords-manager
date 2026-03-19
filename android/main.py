# pyright: reportMissingImports=false

from kivy.app import App  # type: ignore
from kivy.metrics import dp  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.label import Label  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
from kivy.uix.textinput import TextInput  # type: ignore

from storage import AndroidPasswordStore


class PasswordsManagerMobile(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(8), padding=dp(10), **kwargs)

        self.store = AndroidPasswordStore()

        self.title_label = Label(
            text="Passwords Manager (Android)",
            font_size="22sp",
            size_hint=(1, None),
            height=dp(40),
        )
        self.add_widget(self.title_label)

        self.status_label = Label(
            text="Ready",
            size_hint=(1, None),
            height=dp(28),
            color=(0.15, 0.65, 0.2, 1),
        )
        self.add_widget(self.status_label)

        form_scroll = ScrollView(size_hint=(1, None), height=dp(184), do_scroll_x=False)
        form_box = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        form_box.bind(minimum_height=form_box.setter("height"))

        self.address_input = TextInput(
            hint_text="Address",
            multiline=False,
            size_hint=(1, None),
            height=dp(42),
        )
        form_box.add_widget(self.address_input)

        self.user_input = TextInput(
            hint_text="User",
            multiline=False,
            size_hint=(1, None),
            height=dp(42),
        )
        form_box.add_widget(self.user_input)

        self.password_input = TextInput(
            hint_text="Password",
            multiline=False,
            password=True,
            size_hint=(1, None),
            height=dp(42),
        )
        form_box.add_widget(self.password_input)

        buttons = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint=(1, None), height=dp(44))
        self.save_button = Button(text="Save")
        self.save_button.bind(on_press=self._on_save)
        buttons.add_widget(self.save_button)

        self.remove_button = Button(text="Remove")
        self.remove_button.bind(on_press=self._on_remove)
        buttons.add_widget(self.remove_button)

        self.refresh_button = Button(text="Refresh")
        self.refresh_button.bind(on_press=self._refresh_list)
        buttons.add_widget(self.refresh_button)
        form_box.add_widget(buttons)

        form_scroll.add_widget(form_box)
        self.add_widget(form_scroll)

        self.list_title = Label(
            text="Stored passwords",
            size_hint=(1, None),
            height=dp(26),
        )
        self.add_widget(self.list_title)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.list_label = Label(text="", valign="top", halign="left", size_hint_y=None)
        self.list_label.bind(texture_size=self._update_list_height)
        self.scroll.bind(width=self._update_list_height)
        self.scroll.add_widget(self.list_label)
        self.add_widget(self.scroll)

        self._refresh_list()

    def _update_list_height(self, *_args):
        self.list_label.height = max(self.list_label.texture_size[1], 1)
        self.list_label.text_size = (max(self.scroll.width - dp(20), dp(80)), None)

    def _set_status(self, text):
        self.status_label.text = text

    def _on_save(self, *_args):
        result = self.store.add_password(
            self.address_input.text,
            self.user_input.text,
            self.password_input.text,
        )
        if isinstance(result, tuple):
            ok = bool(result[0]) if result else False
            message = str(result[1]) if len(result) > 1 else "Operation finished."
        else:
            ok = bool(result)
            message = "Operation finished."

        self._set_status(message)
        if ok:
            self.password_input.text = ""
            self._refresh_list()

    def _on_remove(self, *_args):
        result = self.store.remove_password(
            self.address_input.text,
            self.user_input.text,
        )
        if isinstance(result, tuple):
            ok = bool(result[0]) if result else False
            message = str(result[1]) if len(result) > 1 else "Operation finished."
        else:
            ok = bool(result)
            message = "Operation finished."

        self._set_status(message)
        if ok:
            self._refresh_list()

    def _refresh_list(self, *_args):
        entries = self.store.load_passwords()
        if not entries:
            self.list_label.text = "No passwords saved yet."
            return

        lines = []
        for idx, item in enumerate(entries, start=1):
            lines.append(
                f"{idx}. {item.get('Address', '')} | {item.get('User', '')} | {item.get('Password', '')}"
            )
        self.list_label.text = "\n".join(lines)


class PasswordsManagerMobileApp(App):
    def build(self):
        self.title = "Passwords Manager"
        return PasswordsManagerMobile()


if __name__ == "__main__":
    PasswordsManagerMobileApp().run()
