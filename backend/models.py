from main import db
from datetime import datetime
from sqlalchemy import inspect
from sqlalchemy.orm import relationship, validates

class Banners(db.Model):
    __tablename__ = 'banners'
    bannerId = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(500))
    file_url = db.Column(db.String(500))
    page = db.Column(db.String(20))
    position = db.Column(db.String(20))  # Add a field for banner position
    link = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    @classmethod
    def get_by_id(cls, bannerId):
        return cls.query.get(bannerId)


class Users(db.Model):
    __tablename__ = 'users'
    userId = db.Column(db.String(50), primary_key=True, nullable=False, unique=True)
    name = db.Column(db.String(30), nullable=False)
    mobile = db.Column(db.String(15), nullable=True, unique=True)
    email = db.Column(db.String(75), nullable=True, unique=True)
    password = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    @validates('email', 'mobile')
    def validate_email_or_mobile(self, key, value):
        if not (value or self.email or self.mobile):
            raise ValueError("At least email or mobile must be provided.")
        return value
    
    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def toDictExceptPassword(self):
        excluded_fields = ['password']
        columns = inspect(self.__class__).mapper.column_attrs
        fields = [c.key for c in columns if c.key not in excluded_fields]
        return {field: getattr(self, field) for field in fields}

    @classmethod
    def get_by_id(cls, userId):
        return cls.query.get(userId)

class Addresses(db.Model):
    __tablename__ = 'addresses'
    addressId = db.Column(db.String(50), primary_key=True, nullable=False, unique=True)
    userId = db.Column(db.String(50), db.ForeignKey('users.userId'), nullable=False)
    address1 = db.Column(db.String(200), nullable=False)
    address2 = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(75), nullable=False)
    zipcode = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(), nullable=True)
    user = relationship('Users', backref='addresses')

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
    
    def get_full_address(self):
        address_fields = [str(self.address1), str(self.address2), str(self.city), str(self.state), str(self.zipcode)]
        full_address = ', '.join(filter(None, address_fields))
        return full_address

    
    @classmethod
    def get_by_id(cls, addressId):
        return cls.query.get(addressId)
    
    @classmethod
    def get_by_id(cls, tshirtId):
        return cls.query.get(tshirtId)

class Files(db.Model):
    __tablename__ = 'files'
    fileId = db.Column(db.String(50), primary_key=True)
    filepath = db.Column(db.String(500), nullable=False)
    fileUrl= db.Column(db.String(500), nullable=False)
    fileType=db.Column(db.String(25), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
    def toDictWithExceptFields(self):
        excluded_fields = ['fileId','date']
        columns = inspect(self.__class__).mapper.column_attrs
        fields = [c.key for c in columns if c.key not in excluded_fields]
        file_dict = {field: getattr(self, field) for field in fields}
        return file_dict
    
    @classmethod
    def get_by_id(cls, fileId):
        return cls.query.get(fileId)
    

class TShirts(db.Model):
    __tablename__ = 'tshirts'
    tshirtId = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    template_image = db.Column(db.String(100), nullable=False)
    tshirt_image = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    brand = db.Column(db.String(50))
    color = db.Column(db.JSON, nullable=False)
    size = db.Column(db.JSON, nullable=False)
    gender = db.Column(db.String(10))
    stock_quantity = db.Column(db.Integer, nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    discount = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(50), nullable=False)
    keywords = db.Column(db.String(100), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
    def toDictWithExceptFields(self):
        excluded_fields = ['date']
        columns = inspect(self.__class__).mapper.column_attrs
        fields = [c.key for c in columns if c.key not in excluded_fields]
        item_dict = {field: getattr(self, field) for field in fields}
        return item_dict
    
    
    @classmethod
    def get_by_id(cls, tshirtId):
        return cls.query.get(tshirtId)
    @classmethod
    def get_unique_categories(cls):
        categories = cls.query.with_entities(cls.category).distinct().all()
        unique_categories = [category[0] for category in categories]
        return unique_categories
    


class Admin(db.Model):
    __tablename__ = 'admin'
    adminId = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    dateTime = db.Column(db.DateTime, default=datetime.utcnow)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return f"Admin(username='{self.username}', email='{self.email}')"



class Carts(db.Model):
    __tablename__ = 'carts'
    cartId = db.Column(db.String(50), primary_key=True)
    userId = db.Column(db.String(50), db.ForeignKey('users.userId'), nullable=False)
    tshirtId = db.Column(db.String(50), db.ForeignKey('tshirts.tshirtId'), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    size = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user = relationship('Users', backref='carts')
    tshirt = relationship('TShirts', backref='carts')
    
    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def toDictWithTshirtDetails(self):
        cart_dict = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

        # Fetch the associated T-Shirt for the cart
        tshirt = TShirts.query.filter_by(tshirtId=self.tshirtId).first()
        if tshirt:
            cart_dict['tshirt'] = tshirt.toDict()

        return cart_dict
    @classmethod
    def get_by_id(cls, cartId):
        return cls.query.get(cartId)

class OrderItems(db.Model):
    __tablename__ = 'order_items'
    itemId = db.Column(db.String(50), primary_key=True)
    tshirtId = db.Column(db.String(50), db.ForeignKey('tshirts.tshirtId'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    size = db.Column(db.String(10), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    tshirt = relationship('TShirts', backref='order_items')
    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
    def toDictWithTshirtDetails(self):
        item_dict =self.toDictExceptFields() 
        # Fetch the associated T-Shirt for the cart
        tshirt = TShirts.query.filter_by(tshirtId=self.tshirtId).first()
        if tshirt:
            item_dict['tshirt'] = tshirt.toDict()

        return item_dict
    def toDictExceptFields(self):
        excluded_fields = ['itemId','tshirtId','date']
        columns = inspect(self.__class__).mapper.column_attrs
        fields = [c.key for c in columns if c.key not in excluded_fields]
        item_dict = {field: getattr(self, field) for field in fields}
        return item_dict

    @classmethod
    def get_by_id(cls, itemId):
        return cls.query.get(itemId)
    
class Orders(db.Model):
    __tablename__ = 'orders'
    orderId = db.Column(db.String(50), primary_key=True)
    itemId = db.Column(db.String(50), db.ForeignKey('order_items.itemId'), nullable=False)
    userId = db.Column(db.String(50), db.ForeignKey('users.userId'), nullable=False)
    addressId = db.Column(db.String(50), db.ForeignKey('addresses.addressId'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    user = relationship('Users', backref='orders')
    address = relationship('Addresses', backref='orders')
    items = relationship('OrderItems', backref='order')

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
    def toDictWithAllFields(self):
        excluded_fields = ['itemId','userId','addressId']
        columns = inspect(self.__class__).mapper.column_attrs
        fields = [c.key for c in columns if c.key not in excluded_fields]
        order_dict = {field: getattr(self, field) for field in fields}


        # Add related objects data
        # order_dict['user'] = Users.get_by_id(self.userId).toDictExceptPassword() if self.user else None
        order_dict['address'] = Addresses.get_by_id(self.addressId).get_full_address() if self.address else None
        order_dict['items'] = OrderItems.get_by_id(self.itemId).toDictWithTshirtDetails()  if self.items else None

        return order_dict


    @classmethod
    def get_by_id(cls, orderId):
        return cls.query.get(orderId)




