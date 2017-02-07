from werkzeug.security import generate_password_hash, check_password_hash
from mongoengine import Document, StringField, EmailField

class User(Document):
    username = StringField(max_length=24, require=True, unique=True)
    password_hash = StringField(max_length=255, require=True)
    email = EmailField()

    def __init__(self, username='', password='', email='', **kwargs):
        Document.__init__(self, **kwargs)
        self.username = username
        self.password = password
        self.email = email

    @property
    def password(self):
        raise AttributeError('password is not a readable field')


    @password.setter
    def password(self, password):
        if password and password != '':
            self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
