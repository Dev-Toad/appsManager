APPLICATION_TYPES = [
    "Frontend Web",
    "Mobile App (Nativa)",
    "Backend / API",
    "Microservicio",
    "API Gateway",
    "Servicio de Colas/Mensajería",
    "Servicio de Cache",
    "Base de Datos",
    "Integración / ETL",
    "Servicio de Autenticación",
    "Computación sin Servidor (Serverless)",
    "Legacy / Monolito",
]

STACKS_AND_FRAMEWORKS = {
    "Python": ["Flask", "Django", "FastAPI", "Pandas", "Pyramid"],
    "JavaScript/Node.js": [
        "React",
        "Vue.js",
        "Angular",
        "Express.js",
        "Next.js",
        "NestJS",
        "Nuxt.js",
    ],
    "Java": ["Spring Boot", "Spring MVC", "Jakarta EE", "Hibernate", "JAX-RS"],
    "C# / .NET": [".NET Core", "ASP.NET MVC", "Xamarin", "Blazor"],
    "PHP": ["Laravel", "Symfony", "CodeIgniter"],
    "Go": ["Gin", "Echo", "Revel", "Gorilla Mux"],
    "Mobile Nativo": [
        "Swift",
        "Kotlin",
        "Objective-C",
        "Java (Android)",
        "Flutter",
        "React Native",
    ],
}


def run_seed(db, ApplicationType, Stack, Framework):
    """
    Función principal para insertar todos los datos de catálogo (Tipos, Stacks y Frameworks)
    en la base de datos de forma atómica si no existen.
    """

    db.session.begin()
    print("--- INICIANDO PROCESO DE SIEMBRA DE DATOS DE CATÁLOGO ---")

    try:

        print("\n[A] Sembrando Tipos de Aplicación...")
        for type_name in APPLICATION_TYPES:

            existing_type = ApplicationType.query.filter_by(name=type_name).first()
            if not existing_type:
                db.session.add(ApplicationType(name=type_name))
                print(f"  ✅ Agregado Tipo: {type_name}")

        print("\n[B] Sembrando Stacks y Frameworks...")
        stack_objects = {}

        for stack_name in STACKS_AND_FRAMEWORKS.keys():
            existing_stack = Stack.query.filter_by(name=stack_name).first()

            if not existing_stack:
                current_stack = Stack(name=stack_name)
                db.session.add(current_stack)
                db.session.flush()
                print(f"  ** Stack: {stack_name} (Nuevo) **")
            else:
                current_stack = existing_stack

            stack_objects[stack_name] = current_stack

        for stack_name, framework_list in STACKS_AND_FRAMEWORKS.items():
            current_stack = stack_objects[stack_name]

            for framework_name in framework_list:
                existing_framework = Framework.query.filter_by(
                    name=framework_name, stack_id=current_stack.id
                ).first()

                if not existing_framework:
                    new_framework = Framework(name=framework_name, stack=current_stack)
                    db.session.add(new_framework)
                    print(f"    > Framework: {framework_name}")

        db.session.commit()
        print(
            "\n🎉 SIEMBRA GLOBAL COMPLETADA EXITOSAMENTE. Tablas de catálogo pobladas."
        )
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR CRÍTICO DURANTE LA SIEMBRA. Se revirtió todo: {e}")
        print("Asegúrese de que la base de datos esté accesible y las tablas creadas.")
