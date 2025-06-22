import os
import json
from cryptography.fernet import Fernet
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ========================
# CONFIGURACIÓN DE GOOGLE
# ========================
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Pega aquí tu contenido de credentials.json
cred_json_str = """{
  "installed": {
    "client_id": "TU_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "tu-proyecto",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "TU_CLIENT_SECRET",
    "redirect_uris": [
      "urn:ietf:wg:oauth:2.0:oob",
      "http://localhost"
    ]
  }
}"""

# Guardar archivo de credenciales
with open("credentials.json", "w") as f:
    f.write(cred_json_str)

# ========================
# FUNCIONES DE GOOGLE
# ========================
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

def subir_archivo(nombre_archivo_local, nombre_en_drive):
    creds = autenticar()
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': nombre_en_drive}
    media = MediaFileUpload(nombre_archivo_local, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"[📤] Archivo subido a Drive: {nombre_en_drive} (ID: {file['id']})")
    return file['id']

# ========================
# ENCRIPTAR Y GUARDAR CLAVE
# ========================
def generar_clave():
    key = Fernet.generate_key()
    with open("clave.key", "wb") as f:
        f.write(key)
    return key

def encriptar_archivo(path, key):
    fernet = Fernet(key)
    with open(path, "rb") as file:
        contenido = file.read()
    contenido_encriptado = fernet.encrypt(contenido)
    with open(path, "wb") as file:
        file.write(contenido_encriptado)

# ========================
# EJECUCIÓN PRINCIPAL
# ========================
if __name__ == "__main__":
    # Ruta al archivo que se va a encriptar (por ejemplo, imagen en Escritorio)
    archivo_a_encriptar = os.path.expanduser("~/Desktop/clave.txt")

    # 1. Generar clave
    clave = generar_clave()

    # 2. Encriptar archivo
    encriptar_archivo(archivo_a_encriptar, clave)
    print("[🔐] Archivo encriptado correctamente.")

    # 3. Guardar clave temporalmente
    with open("clave_temporal.txt", "wb") as f:
        f.write(clave)

    # 4. Subir clave a Google Drive
    subir_archivo("clave_temporal.txt", "clave_remota.txt")

    # 5. Eliminar archivo temporal de la clave
    os.remove("clave_temporal.txt")
    print("[🗑️] Archivo local de clave eliminado.")

    # 6. Crear archivo de saludo en Escritorio
    ruta_saludo = os.path.expanduser("~/Desktop/saludo.txt")
    with open(ruta_saludo, "w") as f:
        f.write("hola como estas?")
    print(f"[📄] Archivo de saludo creado en: {ruta_saludo}")
