import os
import requests
import subprocess
import sys

# 🔹 CONFIGURACIÓN
GITHUB_USER = "brayan19511"
GITHUB_REPO = "APLICACION-ADM"
BRANCH = "mvp"
APP_NAME = "main.py"  # Se ejecutará si no es un .exe
VERSION_FILE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}/output/version.txt"
APP_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}/output/main.exe"
LOCAL_VERSION_FILE = "output/version.txt"
LOCAL_APP = "output/main.exe"  # Si se usa como ejecutable

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
    return "0.0.0"  # Si no existe, asumimos que es muy antigua

def download_app():
    """Descarga la última versión de la aplicación"""
    try:
        response = requests.get(APP_URL, stream=True)
        response.raise_for_status()
        with open(LOCAL_APP, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print("✅ Descarga completada.")
        return True
    except requests.RequestException as e:
        print(f"❌ Error al descargar la aplicación: {e}")
        return False

def update_version_file(version):
    """Actualiza el archivo de versión local"""
    with open(LOCAL_VERSION_FILE, "w") as file:
        file.write(version)

def run_application():
    """Ejecuta la aplicación después de la verificación"""
    if os.path.exists(LOCAL_APP):
        print(f"🚀 Ejecutando {LOCAL_APP}...")
        subprocess.Popen([LOCAL_APP])
    else:
        print("⚠️ No se encontró el ejecutable, ejecutando main.py...")
        subprocess.Popen(["python", "main.py"])  # Si no es .exe, usa el script original

    sys.exit()

def main():
    """Lógica principal del launcher"""
    print("🔄 Verificando actualizaciones...")

    remote_version = get_remote_version()
    local_version = get_local_version()

    if not remote_version:
        print("❌ No se pudo obtener la versión remota. Ejecutando versión actual.")
        run_application()
        return

    if remote_version > local_version:
        print(f"🔄 Nueva versión disponible: {remote_version}. Descargando...")
        if download_app():
            update_version_file(remote_version)
            print("✅ Aplicación actualizada con éxito.")
        else:
            print("❌ Error en la actualización.")

    run_application()

if __name__ == "__main__":
    main()
