from app import app
from models import db, User

with app.app_context():
    try: 
        db.drop_all()
        db.create_all()
        
        u1 = User(
            username = 'test',
            password = 'demo'
        )        
        u2 = User(
            username = 'username',
            password = 'password'
        )
        
        db.session.add_all([u1, u2])
        db.session.commit()
        
        print("it worked")
        
    except Exception as e:
        print(f"It didn't work, here's where it/you messed up {str(e)}")