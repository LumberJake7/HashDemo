from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):

    db.app = app
    db.init_app(app)
    
    
class User(db.Model):

    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password=db.Column(db.Text, nullable=False)
    
    @classmethod
    def register(cls, username,password):
        
        hashed= bcrypt.generate_password_hash(password)
        
        hashed_utf8 = hashed.decode("utf8")
        
        return cls(username=username, password = hashed_utf8)
    
    @classmethod
    def authenticate(cls, username,password):
        
        u = User.query.filter_by(username=username). first()
        
        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False
        
class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(100), db.ForeignKey('users.username'), nullable=False)

    user = db.relationship('User', backref='feedback')

    def __repr__(self):
        return f'<Feedback id={self.id} title={self.title} username={self.username}>'
