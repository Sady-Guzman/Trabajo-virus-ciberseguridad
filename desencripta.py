import os
from cryptography.fernet import Fernet
import json
import hashlib

# Extensiones que NO deben ser tocadas
EXTENSIONES_PROHIBIDAS = [
    '.so', '.bin', '.exe', '.dll', '.o', '.a', '.ko', '.img', '.iso', '.tmp'
]

def cargar_key(path="key.key"):
    with open(path, "rb") as f:
        return f.read()

def calcular_hash(data):
    return hashlib.sha256(data).hexdigest()

def es_oculto(path):
    partes = path.split(os.sep)
    return any(p.startswith('.') for p in partes if p)

def encontrar_archivos(ruta_home):
    archivos = []
    for dirpath, _, filenames in os.walk(ruta_home):
        if es_oculto(dirpath):
            continue
        for nombre in filenames:
            if nombre.startswith('.'):
                continue
            _, ext = os.path.splitext(nombre)
            if ext.lower() not in EXTENSIONES_PROHIBIDAS:
                archivos.append(os.path.join(dirpath, nombre))
    return archivos

def desencriptar_archivos(archivos, key, hashes):
    f = Fernet(key)
    errores = []

    for archivo in archivos:
        try:
            with open(archivo, "rb") as file:
                datos_cifrados = file.read()
            datos_original = f.decrypt(datos_cifrados)
            hash_actual = calcular_hash(datos_original)

            hash_guardado = hashes.get(archivo)
            if hash_guardado and hash_guardado != hash_actual:
                print(f"⚠ Hash no coincide en: {archivo}")

            with open(archivo, "wb") as file:
                file.write(datos_original)
            print(f"✔ Desencriptado: {archivo}")
        except Exception as e:
            print(f"✘ Error con {archivo}: {e}")
            errores.append(archivo)
    
    return errores

if __name__ == "__main__":
    ruta_home = os.path.expanduser("~")
    print(f"[🔓] Buscando archivos en: {ruta_home}")

    key = cargar_key()
    archivos = encontrar_archivos(ruta_home)

    with open("hashes.json", "r") as f:
        hashes = json.load(f)

    errores = desencriptar_archivos(archivos, key, hashes)

    print("\n[✅] Desencriptación finalizada.")
    if errores:
        print("[⚠] Archivos con errores:", errores)
