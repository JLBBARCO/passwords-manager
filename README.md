# Password Manager

This program manages passwords saved in a `passwords.json` or `passwords.csv` file.

It can generate simple and complex passwords and save them to a `passwords.json` file, and also allows the addition or removal of external passwords.

If your passwords saved in a `passwords.csv` file, the last version of the system converts to `passwords.json` automatically.

## Structure of `passwords.json`

- The passwords saved in a dict named `passwords`
- In the list, the itens have this sintaxe: `{"address": "", "user": "", "password": ""}`

## Structure of `passwords.csv`

- Lines are separated by Enter;

- Columns are separated by `;`;

- The first line contains the column names, which are:

1. Address

2. Username

3. Password

## Downloads

[Releases](https://github.com/JLBBARCO/passwords-manager/releases)
