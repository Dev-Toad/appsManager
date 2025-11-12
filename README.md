# appsManager

![CI](https://github.com/Dev-Toad/appsManager/actions/workflows/ci.yml/badge.svg)

Aplicación Flask para el control de aplicaciones y sus versiones.

## Requisitos
- Python 3.8 (el virtualenv incluido `lardin` usa 3.8)
- pip
- virtualenv (opcional)

## Configurar el entorno (local)
1. Activar el virtualenv incluido (si existe):

```bash
source lardin/bin/activate
```

2. Instalar dependencias (si no están instaladas):

```bash
pip install -r requirements.txt
```

## Ejecutar la aplicación
Desde la raíz del proyecto:

```bash
export FLASK_APP=run.py
export FLASK_ENV=development
flask run --host=0.0.0.0
```

O usando el script wrapper incluida:

```bash
python run.py
```

## Formateo y linteo
Este proyecto usa Black y Flake8. Hay un archivo `.flake8` en la raíz que excluye el virtualenv y migraciones.

Formatear código con Black:

```bash
black .
```

Comprobar estilo con Flake8:

```bash
flake8
```

## CI
Se agregó un workflow de GitHub Actions en `.github/workflows/ci.yml` que ejecuta Black (en modo check) y Flake8 en pushes y pull requests.

## Tests
Se agregaron tests de ejemplo y el workflow de CI los ejecuta en cada push/PR.

- `tests/test_auth.py`: integración para el endpoint `/login`.
- `tests/test_user_loader.py`: test unitario para `load_user` (Flask-Login).
- `tests/test_app_controller.py`: tests para crear/editar/borrar `Application` usando `test_client()`.

Ejecutar tests localmente:

```bash
PYTHONPATH=. lardin/bin/pytest -q
```

## Contribuir
- Formatea con `black .` antes de enviar PR.
- Asegúrate de que `flake8` no reporte problemas en las partes del código que modificas.

## Notas
- El proyecto incluye un virtualenv `lardin` para desarrollo local.
- Si necesitas que monte bases de datos o variables de entorno, dime y añado un ejemplo `.env` y la documentación correspondiente.
