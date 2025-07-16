from flask import Flask

def register_blueprints(app: Flask):
    """
    Registra todos los blueprints de la aplicación
    """
    # Importar blueprints
    from app.routes.auth import auth_bp
    # from app.routes.users import users_bp
    # from app.routes.products import products_bp
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    # app.register_blueprint(users_bp)
    # app.register_blueprint(products_bp)
    
    # Blueprint para rutas de salud/status
    # from app.routes.health import health_bp
    # app.register_blueprint(health_bp)