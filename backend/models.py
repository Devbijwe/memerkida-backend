from main import db
from datetime import datetime
from sqlalchemy import inspect
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Users(db.Model):
    __tablename__ = 'users'
    userId=db.Column(db.String(50),primary_key=True,nullable=False,unique=True)
    name=db.Column(db.String(30),nullable=False)
    mobile=db.Column(db.String(15),nullable=False)
    email=db.Column(db.String(75),nullable=True,unique=True)
    password=db.Column(db.String(100),nullable=False)
    date=db.Column(db.DateTime, default=datetime.now(),nullable=True)
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }
    def toDictExceptPassword(self):
        excluded_fields = ['password']  
        columns = inspect(self.__class__).mapper.column_attrs
        fields = [c.key for c in columns if c.key not in excluded_fields]
        return {field: getattr(self, field) for field in fields}
    
class Addresses(db.Model):
    __tablename__ = 'addresses'
    addressId=db.Column(db.String(50),primary_key=True,nullable=False,unique=True)
    userId=db.Column(db.String(50),ForeignKey('users.userId'),nullable=False)
    address1=db.Column(db.String(200),nullable=False)
    address2=db.Column(db.String(200),nullable=True)
    city=db.Column(db.String(50),nullable=False)
    state=db.Column(db.String(75),nullable=False)
    zipcode=db.Column(db.Integer,nullable=False)
    date=db.Column(db.DateTime, default=datetime.now(),nullable=True)
    user = relationship('Users', backref='addresses')
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

class TShirts(db.Model):
    __tablename__ = 'tshirts'
    tshirtId = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    template_image = db.Column(db.String(100), nullable=False)
    tshirt_image = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    brand = db.Column(db.String(50))
    color = db.Column(db.String(20), nullable=False)
    size = db.Column(db.String(10), nullable=False)
    gender = db.Column(db.String(10))
    stock_quantity = db.Column(db.Integer, nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50), nullable=False)
    keywords = db.Column(db.String(100), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

class Admin(db.Model):
    __tablename__ = 'admin'
    adminId = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    dateTime = db.Column(db.DateTime, default=datetime.utcnow)

    
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }
     
    def __repr__(self):
        return f"Admin(username='{self.username}', email='{self.email}')"
    
class Banners(db.Model):
    __tablename__ = 'banners'
    bannerId = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(300))
    image_url1 = db.Column(db.String(200))
    image_url2 = db.Column(db.String(200))
    link = db.Column(db.String(300))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }
