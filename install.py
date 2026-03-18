import customtkinter as ctk
from src.lib.system import (
    DATA_FILENAMES,
    compatibility_installation_paths,
    local_data_path,
    migrate_legacy_data_files,
    path as system_path,
    select_installation_directory,
)
from src.lib.uninstall import run_uninstall
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
        is_update = self._is_existing_installation(destination) or self._has_legacy_installation()
        mode_label = 'Atualizando' if is_update else 'Instalando'

        self.installing = True
        self._set_controls_state('disabled')
        self.open_folder_button.configure(state='disabled')
        self._clear_log()
        self._append_log(f'{mode_label} em: {destination}')
        self.progress_counter.configure(text='Preparando instalação...')
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start()
        threading.Thread(target=self._install_worker, args=(destination, is_update), daemon=True).start()

    def _workspace_root(self):
        return Path(__file__).resolve().parent

    def _runtime_root(self):
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).resolve().parent
        return self._workspace_root()

    def _resolve_destination(self):
        selected_path = Path(self.installation_path).expanduser()

        if selected_path.name.lower() != 'passwords manager':
            selected_path = selected_path / 'Passwords Manager'

        return selected_path

    def _fallback_destination(self):
        return Path(system_path())

    def _legacy_installation_paths(self):
        destination = self._resolve_destination()
        legacy_paths = []
        for candidate in compatibility_installation_paths():
            candidate_path = Path(candidate)
            try:
                if candidate_path.resolve() == destination.resolve():
                    continue
            except Exception:
                pass
            legacy_paths.append(candidate_path)
        return legacy_paths

    def _prepare_destination_with_fallback(self, destination):
        try:
            destination.mkdir(parents=True, exist_ok=True)
            self._probe_destination_write(destination)
            return destination, False
        except PermissionError:
            fallback = self._fallback_destination()
            if fallback.resolve() == destination.resolve():
                raise PermissionError(
                    'Sem permissão para instalar na pasta configurada. Execute o instalador com privilégios elevados.'
                )
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

    def _has_legacy_installation(self):
        for legacy_path in self._legacy_installation_paths():
            if not legacy_path.exists():
                continue

            legacy_executable = legacy_path / 'passwords-manager.exe'
            if legacy_executable.exists():
                return True

            if any(legacy_path.iterdir()):
                return True

        return False

    def _migrate_legacy_installation(self, destination):
        migrated_files, skipped_files = migrate_legacy_data_files(DATA_FILENAMES)
        uninstall_results = []

        if migrated_files:
            self.after(
                0,
                self._append_log,
                'Arquivos migrados para dados do usuário: ' + ', '.join(Path(path).name for path in migrated_files),
            )
        if skipped_files:
            self.after(
                0,
                self._append_log,
                'Arquivos de dados já existentes foram preservados: '
                + ', '.join(Path(path).name for path in skipped_files),
            )

        for legacy_path in self._legacy_installation_paths():
            if not legacy_path.exists():
                continue

            try:
                if legacy_path.resolve() == destination.resolve():
                    continue
            except Exception:
                pass

            self.after(0, self._append_log, f'Removendo instalação antiga em: {legacy_path}')
            uninstall_result = run_uninstall(legacy_path)
            uninstall_results.append((str(legacy_path), uninstall_result))
            self.after(
                0,
                self._append_log,
                (
                    'Instalação antiga removida. '
                    f"Itens removidos: {uninstall_result.get('removed', 0)}. "
                    f"Ignorados: {uninstall_result.get('skipped', 0)}."
                ),
            )

        return migrated_files, skipped_files, uninstall_results

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

    def _release_candidates(self):
        candidates = [self._runtime_root() / 'release']

        if getattr(sys, 'frozen', False):
            meipass = getattr(sys, '_MEIPASS', None)
            if meipass:
                candidates.append(Path(meipass) / 'release')

        candidates.append(self._workspace_root() / 'release')

        unique_candidates = []
        seen = set()
        for candidate in candidates:
            normalized = str(candidate.resolve())
            if normalized not in seen:
                seen.add(normalized)
                unique_candidates.append(candidate)

        return unique_candidates

    def _validate_release_structure(self, release_dir):
        required_files = [
            release_dir / 'passwords-manager.exe',
            release_dir / 'uninstall' / 'uninstall.exe',
        ]
        missing = [str(file_path) for file_path in required_files if not file_path.exists()]
        if missing:
            raise FileNotFoundError(
                'Estrutura de release incompleta. Arquivos ausentes: ' + ', '.join(missing)
            )

    def _release_files(self):
        checked_paths = []
        for release_dir in self._release_candidates():
            checked_paths.append(str(release_dir))
            if not release_dir.exists():
                continue

            files = [file_path for file_path in release_dir.rglob('*') if file_path.is_file()]
            if not files:
                continue

            self._validate_release_structure(release_dir)
            return release_dir, files

        raise FileNotFoundError(
            'Pasta de release não encontrada ou incompleta. Caminhos verificados: '
            + '; '.join(checked_paths)
        )

    def _start_menu_shortcut_path(self):
        appdata = os.environ.get('APPDATA')
        if not appdata:
            raise EnvironmentError('APPDATA não encontrado para criar atalho no Menu Iniciar.')
        return Path(appdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs'

    def _create_start_menu_shortcuts(self, destination):
        if os.name != 'nt':
            return []

        destination_path = Path(destination)
        main_exe = destination_path / 'passwords-manager.exe'
        uninstall_exe = destination_path / 'uninstall' / 'uninstall.exe'

        if not main_exe.exists():
            raise FileNotFoundError(f'Executável principal não encontrado para atalho: {main_exe}')

        if not uninstall_exe.exists():
            raise FileNotFoundError(f'Desinstalador não encontrado para atalho: {uninstall_exe}')

        start_menu_dir = self._start_menu_shortcut_path()
        start_menu_dir.mkdir(parents=True, exist_ok=True)

        shortcuts = [
            ('Passwords Manager.lnk', main_exe, 'Passwords Manager'),
            ('Uninstall Passwords Manager.lnk', uninstall_exe, 'Uninstall Passwords Manager'),
        ]

        created_paths = []
        for shortcut_name, target_exe, description in shortcuts:
            shortcut_path = start_menu_dir / shortcut_name

            shortcut_path_ps = str(shortcut_path).replace("'", "''")
            target_exe_ps = str(target_exe).replace("'", "''")
            working_dir_ps = str(destination_path).replace("'", "''")
            description_ps = description.replace("'", "''")

            script = (
                "$shell = New-Object -ComObject WScript.Shell;"
                f"$shortcut = $shell.CreateShortcut('{shortcut_path_ps}');"
                f"$shortcut.TargetPath = '{target_exe_ps}';"
                f"$shortcut.WorkingDirectory = '{working_dir_ps}';"
                f"$shortcut.IconLocation = '{target_exe_ps},0';"
                f"$shortcut.Description = '{description_ps}';"
                "$shortcut.Save();"
            )

            result = subprocess.run(
                ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', script],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    'Falha ao criar atalho no Menu Iniciar: '
                    + (result.stderr.strip() or result.stdout.strip() or 'erro desconhecido')
                )

            created_paths.append(str(shortcut_path))

        return created_paths

    def _register_windows_uninstall_entry(self, destination):
        if os.name != 'nt':
            return None

        destination_path = Path(destination)
        uninstall_exe = destination_path / 'uninstall' / 'uninstall.exe'
        display_icon = destination_path / 'passwords-manager.exe'

        if not uninstall_exe.exists():
            raise FileNotFoundError(f'Desinstalador não encontrado para registro: {uninstall_exe}')

        uninstall_string = f'"{uninstall_exe}"'
        app_name = 'Passwords Manager'
        publisher = 'JLBBARCO'
        install_date = datetime.now().strftime('%Y%m%d')
        install_location_ps = str(destination_path).replace("'", "''")
        display_icon_ps = str(display_icon).replace("'", "''")
        uninstall_string_ps = uninstall_string.replace("'", "''")

        reg_path = r'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\PasswordsManager'

        script = (
            f"$path = '{reg_path}';"
            "if (!(Test-Path $path)) { New-Item -Path $path -Force | Out-Null };"
            f"Set-ItemProperty -Path $path -Name 'DisplayName' -Value '{app_name}';"
            f"Set-ItemProperty -Path $path -Name 'Publisher' -Value '{publisher}';"
            f"Set-ItemProperty -Path $path -Name 'InstallLocation' -Value '{install_location_ps}';"
            f"Set-ItemProperty -Path $path -Name 'DisplayIcon' -Value '{display_icon_ps}';"
            f"Set-ItemProperty -Path $path -Name 'UninstallString' -Value '{uninstall_string_ps}';"
            f"Set-ItemProperty -Path $path -Name 'QuietUninstallString' -Value '{uninstall_string_ps}';"
            "Set-ItemProperty -Path $path -Name 'NoModify' -Type DWord -Value 1;"
            "Set-ItemProperty -Path $path -Name 'NoRepair' -Type DWord -Value 1;"
            f"Set-ItemProperty -Path $path -Name 'InstallDate' -Value '{install_date}';"
        )

        result = subprocess.run(
            ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', script],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                'Falha ao registrar desinstalação no Windows: '
                + (result.stderr.strip() or result.stdout.strip() or 'erro desconhecido')
            )

        return reg_path

    def _linux_shortcut_dir(self):
        return Path.home() / '.local' / 'share' / 'applications'

    def _create_linux_desktop_shortcuts(self, destination):
        desktop_dir = self._linux_shortcut_dir()
        desktop_dir.mkdir(parents=True, exist_ok=True)

        app_exec = Path(destination) / 'passwords-manager'
        uninstall_exec = Path(destination) / 'uninstall' / 'uninstall.sh'

        if not app_exec.exists():
            return []

        app_entry = desktop_dir / 'passwords-manager.desktop'
        uninstall_entry = desktop_dir / 'passwords-manager-uninstall.desktop'

        app_content = (
            '[Desktop Entry]\n'
            'Type=Application\n'
            'Version=1.0\n'
            'Name=Passwords Manager\n'
            f'Exec="{app_exec}"\n'
            'Terminal=false\n'
            'Categories=Utility;Security;\n'
        )

        app_entry.write_text(app_content, encoding='utf-8')
        created = [str(app_entry)]

        if uninstall_exec.exists():
            uninstall_content = (
                '[Desktop Entry]\n'
                'Type=Application\n'
                'Version=1.0\n'
                'Name=Uninstall Passwords Manager\n'
                f'Exec="{uninstall_exec}"\n'
                'Terminal=true\n'
                'Categories=Utility;\n'
            )
            uninstall_entry.write_text(uninstall_content, encoding='utf-8')
            created.append(str(uninstall_entry))

        return created

    def _create_macos_shortcuts(self, destination):
        apps_dir = Path.home() / 'Applications'
        apps_dir.mkdir(parents=True, exist_ok=True)

        app_exec = Path(destination) / 'passwords-manager'
        uninstall_exec = Path(destination) / 'uninstall' / 'uninstall.sh'

        if not app_exec.exists():
            return []

        app_launcher = apps_dir / 'Passwords Manager.command'
        app_launcher.write_text(f'#!/bin/bash\n"{app_exec}"\n', encoding='utf-8')
        app_launcher.chmod(0o755)

        created = [str(app_launcher)]

        if uninstall_exec.exists():
            uninstall_launcher = apps_dir / 'Uninstall Passwords Manager.command'
            uninstall_launcher.write_text(f'#!/bin/bash\n"{uninstall_exec}"\n', encoding='utf-8')
            uninstall_launcher.chmod(0o755)
            created.append(str(uninstall_launcher))

        return created

    def _create_platform_shortcuts(self, destination):
        if os.name == 'nt':
            return self._create_start_menu_shortcuts(destination)

        if sys.platform.startswith('linux'):
            return self._create_linux_desktop_shortcuts(destination)

        if sys.platform == 'darwin':
            return self._create_macos_shortcuts(destination)

        return []

        shortcut_path = self._start_menu_shortcut_path()
        shortcut_path.parent.mkdir(parents=True, exist_ok=True)

        shortcut_path_ps = str(shortcut_path).replace("'", "''")
        target_exe_ps = str(target_exe).replace("'", "''")
        working_dir_ps = str(Path(destination)).replace("'", "''")

        script = (
            "$shell = New-Object -ComObject WScript.Shell;"
            f"$shortcut = $shell.CreateShortcut('{shortcut_path_ps}');"
            f"$shortcut.TargetPath = '{target_exe_ps}';"
            f"$shortcut.WorkingDirectory = '{working_dir_ps}';"
            f"$shortcut.IconLocation = '{target_exe_ps},0';"
            "$shortcut.Description = 'Passwords Manager';"
            "$shortcut.Save();"
        )

        result = subprocess.run(
            ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', script],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                'Falha ao criar atalho no Menu Iniciar: '
                + (result.stderr.strip() or result.stdout.strip() or 'erro desconhecido')
            )

        return str(shortcut_path)

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

    def _on_install_success(self, destination, is_update, updated_files, skipped_files, shortcuts=None):
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
        if shortcuts:
            for shortcut in shortcuts:
                self._append_log(f'Atalho criado/atualizado: {shortcut}')
        status_text = 'atualizados' if is_update else 'instalados'
        shortcuts_text = ''
        if shortcuts:
            shortcuts_text = '\nAtalhos criados:\n' + '\n'.join(shortcuts)
        messagebox.showinfo(
            program_name,
            (
                f'Arquivos {status_text} em:\n{destination}\n\n'
                f'Dados do usuário em:\n{local_data_path()}\n\n'
                f'Copiados: {updated_files}\nInalterados: {skipped_files}'
                f'{shortcuts_text}'
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
            self.after(0, self._append_log, 'Procurando arquivos de deploy pré-compilados...')
            try:
                release_dir, files = self._release_files()
                self.after(0, self._append_log, f'Payload encontrado em: {release_dir}')
            except FileNotFoundError:
                self.after(0, self._append_log, 'Payload não encontrado. Iniciando build local...')
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

            self.after(0, self._append_log, f'Dados do usuário serão armazenados em: {local_data_path()}')
            self._migrate_legacy_installation(destination)

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

            shortcuts = []
            self.after(0, self._append_log, 'Criando atalhos do sistema...')
            try:
                shortcuts = self._create_platform_shortcuts(destination)
            except Exception as shortcut_error:
                self.after(0, self._append_log, f'Aviso: {shortcut_error}')

            if os.name == 'nt':
                try:
                    reg_path = self._register_windows_uninstall_entry(destination)
                    self.after(0, self._append_log, f'Registro de desinstalação criado: {reg_path}')
                except Exception as registry_error:
                    self.after(0, self._append_log, f'Aviso: {registry_error}')

            self.after(
                0,
                self._on_install_success,
                str(destination),
                is_update,
                updated_files,
                skipped_files,
                shortcuts,
            )

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