"""
基础模型类
"""
from datetime import datetime
from app.extensions import db


class BaseModel(db.Model):
    """基础模型，提供通用字段和方法"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def save(self):
        """保存到数据库"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """从数据库删除"""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        """转换为字典"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    @classmethod
    def get_by_id(cls, id):
        """根据ID获取"""
        return cls.query.get(id)

    @classmethod
    def get_all(cls):
        """获取所有"""
        return cls.query.all()

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'
