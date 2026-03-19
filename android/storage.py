import json
import os
from pathlib import Path


def _android_data_dir():
	try:
		from android.storage import app_storage_path  # type: ignore

		return Path(app_storage_path())
	except Exception:
		pass

	private_dir = os.environ.get("ANDROID_PRIVATE")
	if private_dir:
		return Path(private_dir)

	home_dir = os.environ.get("HOME")
	if home_dir:
		return Path(home_dir)

	return Path.cwd() / "data"


class AndroidPasswordStore:
	def __init__(self):
		self.base_dir = _android_data_dir() / "Passwords Manager"
		self.base_dir.mkdir(parents=True, exist_ok=True)
		self.passwords_file = self.base_dir / "passwords.json"
		self.key_file = self.base_dir / "encryption.key"
		self._cipher = self._init_cipher()

	def _init_cipher(self):
		try:
			from cryptography.fernet import Fernet
		except Exception:
			return None

		if self.key_file.exists():
			key = self.key_file.read_bytes()
		else:
			key = Fernet.generate_key()
			self.key_file.write_bytes(key)

		return Fernet(key)

	def _encrypt(self, plain_text):
		text = str(plain_text or "")
		if not self._cipher or not text:
			return text
		return self._cipher.encrypt(text.encode("utf-8")).decode("utf-8")

	def _decrypt(self, cipher_text):
		text = str(cipher_text or "")
		if not self._cipher or not text:
			return text

		try:
			return self._cipher.decrypt(text.encode("utf-8")).decode("utf-8")
		except Exception:
			return text

	def _read_raw(self):
		if not self.passwords_file.exists():
			return []

		with open(self.passwords_file, "r", encoding="utf-8") as handle:
			data = json.load(handle)

		if isinstance(data, dict) and "passwords" in data:
			return data["passwords"]
		if isinstance(data, list):
			return data
		return []

	def _write_raw(self, entries):
		payload = []
		for entry in entries:
			payload.append(
				{
					"Address": str(entry.get("Address", "")).strip(),
					"User": str(entry.get("User", "")).strip(),
					"Password": self._encrypt(entry.get("Password", "")),
				}
			)

		with open(self.passwords_file, "w", encoding="utf-8") as handle:
			json.dump(payload, handle, indent=2, ensure_ascii=False)

	def load_passwords(self):
		decrypted = []
		for entry in self._read_raw():
			decrypted.append(
				{
					"Address": str(entry.get("Address", entry.get("address", ""))).strip(),
					"User": str(entry.get("User", entry.get("user", ""))).strip(),
					"Password": self._decrypt(entry.get("Password", entry.get("password", ""))),
				}
			)
		return decrypted

	def add_password(self, address, user, password):
		address = str(address or "").strip()
		user = str(user or "").strip()
		password = str(password or "").strip()

		if not address or not user or not password:
			return False, "Address, user and password are required."

		current = self.load_passwords()
		for entry in current:
			if entry["Address"] == address and entry["User"] == user:
				return False, "Entry already exists for this address and user."

		current.append({"Address": address, "User": user, "Password": password})
		self._write_raw(current)
		return True, "Password saved."

	def remove_password(self, address, user):
		address = str(address or "").strip()
		user = str(user or "").strip()

		if not address or not user:
			return False, "Address and user are required to remove."

		current = self.load_passwords()
		filtered = [
			item for item in current if not (item["Address"] == address and item["User"] == user)
		]

		if len(filtered) == len(current):
			return False, "No matching entry found."

		self._write_raw(filtered)
		return True, "Password removed."


__all__ = ["AndroidPasswordStore"]
