from .base import db, BaseModel


class EmployeeChangeLog(BaseModel):
    __tablename__  = "EmployeeUpdatesLog"

    employee_id = db.Column(db.String(50),  nullable=False, index=True)
    username = db.Column(db.String(80), nullable=False, index=True)
    full_name = db.Column(db.String(200), nullable=False)
    updated_by = db.Column(db.String(80), nullable=False)
    change_desc = db.Column(db.String(500), nullable=False)

    def __init__(self, username, employeeId, full_name, updated_by, change_desc):
        self.employee_id = employeeId
        self.username = username
        self.full_name = full_name
        self.updated_by = updated_by
        self.change_desc = change_desc
        

    def __repr__(self):
        return f"<User {self.username}>"

    @classmethod
    def find_by_username(cls, username):
        """Buscar usuario por username"""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_EmployeeId(cls, employeeId):
        """Buscar usuario por username"""
        return cls.query.filter_by(employee_id=employeeId).first()

    def to_dict(self):
        """Convertir a diccionario"""
        data = super().to_dict()
        return data
