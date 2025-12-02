from app.config import create_app, db


from app.models.application import ApplicationType, Stack, Framework

from run_seed import run_seed


def execute_seed():
    """
    Inicializa la aplicación Flask y ejecuta la siembra dentro del contexto necesario.
    """
    # Inicializar la aplicación
    app = create_app()

    # Entrar al contexto de la aplicación
    with app.app_context():
        print("--------------------------------------------------")
        print("  INICIANDO PROCESO DE SIEMBRA DE DATOS DE CATÁLOGO")
        print("--------------------------------------------------")

        # Llamar a la función de siembra, pasando todas las dependencias:
        # la instancia de la DB y las clases de los modelos.
        run_seed(db, ApplicationType, Stack, Framework)

        print("\nPROCESO DE SIEMBRA FINALIZADO.")


if __name__ == "__main__":
    execute_seed()
