# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['api_server.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/upi_transactions_2024.csv', 'data'),
        ('.env', '.'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'pandas',
        'numpy',
        'flask',
        'flask_cors',
        'google.generativeai',
        'openai',
        'dotenv',
        'sklearn',
        'scipy',
        'sqlite3',
        'json',
  