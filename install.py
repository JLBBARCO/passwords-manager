from src.lib.external_libs import ctk
from src.lib.system import path as system_path, select_installation_directory
from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import sys
import threading
from datetime import datetime
from tkinter import filedialog, messagebox

program_name = 'Install Passwords Manager'
installation_path = system_path()

class Install(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(program_name)
        self.installation_path = installation_path
        self.installing = False
        self.last_installation_destination = None

        self.label = ctk.CTkLabel(self, text=program_name)
        self.label.grid(padx=25, pady=25, row=0, columnspan=2)

        self.container_url = ctk.CTkLabel(self, text='')
        self.container_url.grid(padx=25, pady=25, row=1, columnspan=2)

        self.url_title = ctk.CTkLabel(self.container_url, text='Caminho de instalação: ')
        self.url_title.grid(padx=10, row=0, column=0)

        self.url_path = ctk.CTkLabel(
            self.container_url,
            text=self.installation_path,
            bg_color='green',
            corner_radius=8,
        )
        self.url_path.grid(padx=10, row=0, column=1)
        self.url_path.bind('<Button-1>', self.url_select)

        self.url_select_button = ctk.CTkButton(self.container_url, text='Escolher pasta', command=self.url_select)
        self.url_select_button.grid(padx=10, row=0, column=2)

        self.container_progress = ctk.CTkLabel(self, text='')
        self.container_progress.grid(padx=25, pady=25, row=2, columnspan=2)

        self.progress_bar = ctk.CTkProgressBar(self.container_progress)
        self.progress_bar.grid(padx=10, pady=10, row=0, column=0)
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.set(0)

        self.progress_counter = ctk.CTkLabel(self.container_progress, text='Pronto para instalar')
        self.progress_counter.grid(padx=10, pady=10, row=0, column=1)

        self.log_text = ctk.CTkTextbox(self, width=680, height=180)
        self.log_text.grid(padx=25, pady=(0, 15), row=3, column=0, columnspan=2, sticky='nsew')
        self.log_text.insert('end', 'Logs de instalação aparecerão aqui.\n')
        self.log_text.configure(state='disabled')

        self.container_buttons = ctk.CTkLabel(self, text='')
        self.container_buttons.grid(pady=25, row=4, column=1)

        self.install_button = ctk.CTkButton(self.container_buttons, text='Instalar / Atualizar', command=self.install)
        self.install_button.grid(padx=10, row=0, column=1)

        self.open_folder_button = ctk.CTkButton(
            self.container_buttons,
            text='Abrir pasta instalada',
            command=self.open_install_folder,
            state='disabled',
        )
        self.open_folder_button.grid(padx=10, row=0, column=2)

        self.save_log_button = ctk.CTkButton(self.container_buttons, text='Salvar logs', command=self.save_logs)
        self.save_log_button.grid(padx=10, row=0, column=3)

        self.cancel_button = ctk.CTkButton(self.container_buttons, text='Cancelar', command=self.cancel)
        self.cancel_button.grid(padx=10, row=0, column=4)

    def url_select(self, _event=None):
        if self.installing:
            return

        selected_path = select_installation_directory(self.installation_path, self)

        if selected_path:
            self.installation_path = selected_path
            self.url_path.configure(text=selected_path)
            self.url_path.update()

    def install(self):
        if self.installing:
            return

        destination = self._resolve_destination()

        self.last_installation_destination = str(destination)
        is_update = self._is_existing_installation(destination)
        mode_label = 'Atualizando' if is_update else 'Instalando'

        self.installing = True
        self._set_controls_state('disabled')
        self.open_folder_button.configure(state='disabled')
        self._clear_log()
        self._append_log(f'{mode_label} em: {destination}')
        self.progress_counter.configure(text='Compilando projeto...')
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start()
        threading.Thread(target=self._install_worker, args=(destination, is_update), daemon=True).start()

    def _workspace_root(self):
        return Path(__file__).resolve().parent

    def _resolve_destination(self):
        selected_path = Path(self.installation_path).expanduser()

        if selected_path.name.lower() != 'passwords manager':
            selected_path = selected_path / 'Passwords Manager'

        return selected_path

    def _fallback_destination(self):
        return Path.home() / 'Passwords Manager'

    def _prepare_destination_with_fallback(self, destination):
        try:
            destination.mkdir(parents=True, exist_ok=True)
            self._probe_destination_write(destination)
            return destination, False
        except PermissionError:
            fallback = self._fallback_destination()
            fallback.mkdir(parents=True, exist_ok=True)
            self._probe_destination_write(fallback)
            return fallback, True

    def _probe_destination_write(self, destination):
        probe_file = destination / '.install_write_test.tmp'
        with open(probe_file, 'w', encoding='utf-8') as probe:
            probe.write('ok')
        probe_file.unlink(missing_ok=True)

    def _file_sha256(self, file_path):
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as file_descriptor:
            while True:
                chunk = file_descriptor.read(1024 * 1024)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()

    def _should_copy_file(self, source_file, destination_file):
        if not destination_file.exists():
            return True
        return self._file_sha256(source_file) != self._file_sha256(destination_file)

    def _is_existing_installation(self, destination):
        if not destination.exists():
            return False

        executable = destination / 'passwords-manager.exe'
        if executable.exists():
            return True

        return any(destination.iterdir())

    def _clear_log(self):
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.configure(state='disabled')

    def _append_log(self, message):
        self.log_text.configure(state='normal')
        self.log_text.insert('end', f'{message}\n')
        self.log_text.see('end')
        self.log_text.configure(state='disabled')

    def _run_build_script(self):
        workspace = self._workspace_root()
        script_path = workspace / 'build-local.ps1'

        if not script_path.exists():
            raise FileNotFoundError(f'Script de build não encontrado: {script_path}')

        process = subprocess.Popen(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-File', str(script_path)],
            cwd=str(workspace),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors='replace',
        )

        if process.stdout is not None:
            for output_line in process.stdout:
                line = output_line.rstrip()
                if line:
                    self.after(0, self._append_log, line)

        return_code = process.wait()

        if return_code != 0:
            raise RuntimeError('Falha na compilação. Verifique os logs para mais detalhes.')

    def _release_files(self):
        release_dir = self._workspace_root() / 'release'

        if not release_dir.exists():
            raise FileNotFoundError(f'Pasta de release não encontrada: {release_dir}')

        files = [file_path for file_path in release_dir.rglob('*') if file_path.is_file()]
        if not files:
            raise FileNotFoundError('Nenhum arquivo gerado foi encontrado na pasta release.')

        return release_dir, files

    def _set_controls_state(self, state):
        self.install_button.configure(state=state)
        self.cancel_button.configure(state=state)
        self.url_select_button.configure(state=state)
        self.save_log_button.configure(state=state)

    def _prepare_copy_progress(self, total_files):
        self.progress_bar.stop()
        self.progress_bar.configure(mode='determinate')
        self.progress_bar.set(0)
        self.progress_counter.configure(text=f'Copiando 0/{total_files} arquivos...')

    def _update_copy_progress(self, current, total, filename, changed):
        if total > 0:
            self.progress_bar.set(current / total)
        action = 'copiado' if changed else 'inalterado'
        self.progress_counter.configure(text=f'Analisando {current}/{total}: {filename} ({action})')

    def _on_install_success(self, destination, is_update, updated_files, skipped_files):
        self.installing = False
        self._set_controls_state('normal')
        self.open_folder_button.configure(state='normal')
        self.progress_bar.stop()
        self.progress_bar.configure(mode='determinate')
        self.progress_bar.set(1)
        self.progress_counter.configure(text='Atualização concluída' if is_update else 'Instalação concluída')
        self._append_log(
            f'Processo concluído com sucesso. Copiados: {updated_files}. Inalterados: {skipped_files}.'
        )
        status_text = 'atualizados' if is_update else 'instalados'
        messagebox.showinfo(
            program_name,
            (
                f'Arquivos {status_text} em:\n{destination}\n\n'
                f'Copiados: {updated_files}\nInalterados: {skipped_files}'
            ),
        )

    def _on_install_error(self, error_message):
        self.installing = False
        self._set_controls_state('normal')
        self.progress_bar.stop()
        self.progress_bar.configure(mode='determinate')
        self.progress_bar.set(0)
        self.progress_counter.configure(text='Falha na instalação')
        self._append_log(f'Erro: {error_message}')
        messagebox.showerror(program_name, f'Falha na instalação:\n{error_message}')

    def _install_worker(self, destination, is_update):
        try:
            self.after(0, self._append_log, 'Iniciando build local...')
            self._run_build_script()
            self.after(0, self._append_log, 'Build concluído. Preparando cópia...')
            release_dir, files = self._release_files()

            destination, used_fallback = self._prepare_destination_with_fallback(destination)
            self.last_installation_destination = str(destination)
            if used_fallback:
                self.after(
                    0,
                    self._append_log,
                    (
                        'Sem permissão no destino selecionado. '
                        f'Usando fallback automático: {destination}'
                    ),
                )

            total_files = len(files)
            self.after(0, self._prepare_copy_progress, total_files)

            updated_files = 0
            skipped_files = 0

            for index, source_file in enumerate(files, start=1):
                relative_path = source_file.relative_to(release_dir)
                destination_file = destination / relative_path
                destination_file.parent.mkdir(parents=True, exist_ok=True)
                changed = self._should_copy_file(source_file, destination_file)
                if changed:
                    shutil.copy2(source_file, destination_file)
                    updated_files += 1
                else:
                    skipped_files += 1

                self.after(0, self._update_copy_progress, index, total_files, relative_path.name, changed)

            self.after(0, self._on_install_success, str(destination), is_update, updated_files, skipped_files)

            if used_fallback:
                self.after(
                    0,
                    messagebox.showwarning,
                    program_name,
                    (
                        'A pasta selecionada exigia permissão elevada.\n'
                        f'Os arquivos foram instalados em:\n{destination}'
                    ),
                )
        except Exception as exception:
            self.after(0, self._on_install_error, str(exception))

    def save_logs(self):
        default_name = f'install-log-{datetime.now().strftime("%Y%m%d-%H%M%S")}.txt'
        file_path = filedialog.asksaveasfilename(
            title='Salvar logs da instalação',
            defaultextension='.txt',
            initialfile=default_name,
            filetypes=[('Arquivo de texto', '*.txt'), ('Todos os arquivos', '*.*')],
            parent=self,
        )

        if not file_path:
            return

        self.log_text.configure(state='normal')
        logs = self.log_text.get('1.0', 'end-1c')
        self.log_text.configure(state='disabled')

        try:
            with open(file_path, 'w', encoding='utf-8') as log_file:
                log_file.write(logs)
        except Exception as exception:
            messagebox.showerror(program_name, f'Não foi possível salvar os logs:\n{exception}')
            return

        messagebox.showinfo(program_name, f'Logs salvos em:\n{file_path}')

    def open_install_folder(self):
        if not self.last_installation_destination:
            return

        destination = Path(self.last_installation_destination)
        if not destination.exists():
            messagebox.showwarning(program_name, 'A pasta de instalação não foi encontrada.')
            return

        path_str = str(destination)
        if hasattr(os, 'startfile'):
            os.startfile(path_str)
            return

        if sys.platform == 'darwin':
            subprocess.run(['open', path_str], check=False)
            return

        subprocess.run(['xdg-open', path_str], check=False)

    def cancel(self):
        if self.installing:
            return
        self.destroy()

if __name__ == '__main__':
    app = Install()
    app.mainloop()