import os
import sys
import time
import requests
import subprocess
from PySide6.QtWidgets import QApplication
from modules.main.presenter import MainPresenter

# 🔹 CONFIGURACIÓN DE GITHUB
GITHUB_USER = "brayan19511"
GITHUB_REPO = "APLICACION-ADM"
BRANCH = "mvp"
VERSION_FILE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}/output/version.txt"
APP_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/raw/{BRANCH}/output/main.exe"  # Link directo
LOCAL_VERSION_FILE = "version.txt"
LOCAL_APP = sys.argv[0]  # Nombre del ejecutable actual
NEW_APP = "main_new.exe"

def get_remote_version():
    """Obtiene la versión más reciente desde GitHub"""
    try:
        response = requests.get(VERSION_FILE_URL)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException:
        return None

def get_local_version():
    """Obtiene la versión actual en el equipo"""
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, "r") as file:
            return file.read().strip()
    return "0.0.0"

def download_new_version():
    """Descarga la nueva versión del ejecutable"""
    try:
        response = requests.get(APP_URL, stream=True)
        response.raise_for_status()
        with open(NEW_APP, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return True
    except requests.RequestException as e:
        print(f"❌ Error al descargar la actualización: {e}")
        return False

def update_and_restart():
    """Cierra la aplicación, reemplaza el ejecutable y reinicia"""
    print("🔄 Actualizando aplicación...")

    # Cerrar la aplicación si está abierta
    new_process = subprocess.Popen([NEW_APP])
    time.sleep(2)  # Espera a que el nuevo proceso se inicie

    # Eliminar el ejecutable antiguo
    try:
        os.remove(LOCAL_APP)
    except Exception as e:
        print(f"⚠️ No se pudo eliminar el archivo antiguo: {e}")
    
    # Renombrar el nuevo ejecutable
    os.rename(NEW_APP, LOCAL_APP)

    # Reiniciar la aplicación
    subprocess.Popen([LOCAL_APP])
    sys.exit()

def check_for_update():
    """Verifica si hay una nueva versión disponible y la actualiza"""
    remote_version = get_remote_version()
    local_version = get_local_version()

    if not remote_version:
        print("❌ No se pudo obtener la versión remota. Ejecutando versión actual.")
        return

    if remote_version > local_version:
        print(f"🔄 Nueva versión {remote_version} disponible. Descargando...")

        if download_new_version():
            with open(LOCAL_VERSION_FILE, "w") as file:
                file.write(remote_version)
            update_and_restart()
        else:
            print("❌ Fallo al descargar actualización.")

# 🔹 Verificar actualización antes de ejecutar la app
check_for_update()

# 🔹 Ahora arranca la aplicación PySide6
app = QApplication(sys.argv)
main = MainPresenter()
main.run()
sys.exit(app.exec())
