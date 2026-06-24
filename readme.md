# ADM

Aplicación de escritorio para revisar NCR/DEF, generar plantillas BCP y crear
archivos de facturación masiva para SAP.

## Preparar el entorno

```powershell
py -3.12 -m venv enviroment
.\enviroment\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Complete `.env` solamente si utilizará la conexión SAP. Las credenciales no
deben subirse a Git.

## Ejecutar y probar

```powershell
python main.py
python -m unittest discover -s tests -v
```

## Generar el ejecutable

El empaquetado reproducible está definido en `ADM.spec`:

```powershell
pyinstaller --clean --noconfirm ADM.spec
```

El resultado será `dist\ADM.exe`. `auto-py-to-exe` puede seguir utilizándose
como interfaz visual, pero el archivo `.spec` es la fuente oficial para evitar
que cada compilación use opciones distintas.

## Publicar una actualización

La aplicación consulta el último GitHub Release del repositorio configurado en
`UPDATE_REPOSITORY`. El flujo recomendado es:

1. Cambiar `APP_VERSION` en `core/app_info.py`, por ejemplo a `2.1.4`.
2. Confirmar los cambios en Git.
3. Crear y subir un tag con la misma versión:

```powershell
git tag v2.2.3
git push origin v2.2.3
```

GitHub Actions ejecutará las pruebas, construirá `ADM.exe`, generará
`ADM.exe.sha256` y creará el Release en el mismo repositorio. Al iniciar, las
instalaciones anteriores detectarán la versión, pedirán permiso y se
reemplazarán automáticamente.

El updater solo funciona dentro del `.exe`; al ejecutar `python main.py` se
desactiva para no interferir con desarrollo.

### Repositorios privados

No se debe incrustar un token de GitHub dentro del ejecutable: cualquiera
podría extraerlo. Para actualizaciones sin autenticación, los Releases deben
ser accesibles públicamente. Si el código debe permanecer privado, use un
repositorio público separado únicamente para binarios o un servidor de
descargas propio.

## Cambios en columnas de Excel

Los nombres aceptados están centralizados en:

- `DEF_ALIASES`, dentro de `modules/adm_ncr_def/model.py`.
- `COMMERCIAL_ALIASES`, dentro de
  `modules/fact_masivo_comercial/model.py`.

Si una fuente cambia `N° CUENTA` por `CUENTA BANCARIA`, normalmente basta con
añadir ese nombre como alias. Los procesadores trabajan después con nombres
internos estables.

Las cuentas, porcentajes, series y demás reglas están agrupadas en
`core/business_config.py`.
