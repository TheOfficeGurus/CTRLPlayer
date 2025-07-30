import os
import importlib
from flask import Flask
from app.models.base import db, BaseModel

def register_models():
    """
    Registra automáticamente todos los modelos en la carpeta
    """
    models_dir = os.path.dirname(__file__)
    model_files = [f[:-3] for f in os.listdir(models_dir) if f.endswith('.py') and f != '__init__.py' and f != 'base.py']
    
    registered_models = {}
    
    for model_file in model_files:
        try:
            module = importlib.import_module(f'app.models.{model_file}')            
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseModel) and 
                    attr != BaseModel):
                    registered_models[attr_name] = attr
                    
        except ImportError as e:
            print(f"Error importing model {model_file}: {e}")
    
    return registered_models

# Registrar modelos automáticamente
_models = register_models()

# Hacer modelos disponibles en el namespace
globals().update(_models)

def init_db(app: Flask):
    """
    Inicializa la base de datos
    """
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

def get_all_models():
    """
    Retorna diccionario con todos los modelos registrados
    """
    return _models

# Exponer lo necesario
__all__ = ['db', 'BaseModel', 'init_db', 'get_all_models']