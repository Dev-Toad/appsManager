import os
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename, allowed_extensions=None):
    """Verifica si la extensión del archivo es permitida."""
    if allowed_extensions is None:
        allowed_extensions = current_app.config["ALLOWED_EXTENSIONS"]

    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def save_version_file(file, version_number, file_type="executable"):
    """
    Guarda un archivo de versión y retorna la ruta relativa.

    Args:
        file: FileStorage object de Flask
        version_number: Número de versión (ej: v1.0.0)
        file_type: Tipo de archivo ('executable' o 'docker_compose')

    Returns:
        str: Ruta relativa del archivo guardado
    """
    if not file or file.filename == "":
        return None

    if not allowed_file(file.filename):
        raise ValueError(f"Tipo de archivo no permitido: {file.filename}")

    filename = secure_filename(file.filename)

    version_folder = os.path.join(
        current_app.config["UPLOAD_FOLDER"], secure_filename(version_number), file_type
    )

    os.makedirs(version_folder, exist_ok=True)

    file_path = os.path.join(version_folder, filename)

    file.save(file_path)

    relative_path = os.path.relpath(file_path, current_app.config["UPLOAD_FOLDER"])

    return relative_path


def delete_version_file(file_path):
    """Elimina un archivo de versión si existe."""
    if not file_path:
        return

    full_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file_path)

    if os.path.exists(full_path):
        try:
            os.remove(full_path)
        except Exception as e:
            print(f"Error al eliminar archivo: {e}")
