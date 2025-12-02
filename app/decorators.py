from functools import wraps
from flask import abort, redirect, url_for, current_app
from flask_login import current_user


def roles_required(role_names):
    """Restringe el acceso si el rol del usuario no está en la lista."""

    if not isinstance(role_names, (list, tuple)):
        role_names = [role_names]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(
                    url_for(current_app.config.get("LOGIN_VIEW", "auth.login"))
                )
            user_role_name = current_user.role.name
            if user_role_name not in role_names:
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def permissions_required(permission_names):
    """
    Restringe el acceso a la ruta.

    Implementa lógica OR: El usuario necesita tener AL MENOS UNO de los permisos
    listados para obtener acceso.
    """

    if not isinstance(permission_names, (list, tuple)):
        permission_names = [permission_names]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(
                    url_for(current_app.config.get("LOGIN_VIEW", "auth.login"))
                )

            # --- Lógica OR implementada aquí ---
            # Comprueba si el usuario tiene *cualquiera* de los permisos.
            # current_user.can(perm) devuelve True o False.
            # La función 'any()' devuelve True si AL MENOS UNO de los resultados es True.

            has_permission = any(current_user.can(perm) for perm in permission_names)

            if not has_permission:
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator
