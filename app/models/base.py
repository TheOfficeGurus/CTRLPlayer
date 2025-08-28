from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True  # Esto evita que SQLAlchemy cree tabla para BaseModel
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.today(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.today(), onupdate=datetime.today(), nullable=False)

    def save(self):
        """Guardar el objeto en la base de datos"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self):
        """Eliminar el objeto de la base de datos"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def to_dict(self):
        """Convertir el objeto a diccionario"""
        result = {}
        for column in self.__table__.columns: # type: ignore [Type hint para VS Code]
            value = getattr(self, column.name)
            # Convertir datetime a string para JSON serialization
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result
    
    def update(self, **kwargs):
        """Actualizar el objeto con nuevos valores"""
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def get_by_id(cls, id):
        """Obtener objeto por ID"""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls):
        """Obtener todos los objetos"""
        return cls.query.all()
    
    @classmethod
    def create(cls, **kwargs):
        """Crear y guardar un nuevo objeto"""
        try:
            instance = cls(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance
        except Exception as e:
            db.session.rollback()
            raise e
    
    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'