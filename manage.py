from PhotoShare import app, db
from flask_script import Manager
from PhotoShare.models import User, Image, Comment
import random
from sqlalchemy import or_, and_
import unittest

manager = Manager(app)


@manager.command
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(100):
        db.session.add(User('user' + str(i), 'password' + str(i)))
        for j in range(3):
            db.session.add(Image('https://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png', i+1))
            for k in range(3):
                db.session.add(Comment('comment' + str(k), i + 1, i * 3 + j + 1))
    db.session.commit()

    print(User.query.all())
    print(User.query.get(5))
    print(User.query.filter_by(id=5).all())
    print(User.query.filter(User.username.endswith('0')).all())
    print(User.query.order_by(User.id.desc()).offset(2).limit(5).all())
    print(User.query.filter(or_(User.id == 20, User.id == 30)).all())
    print(User.query.filter(and_(User.id < 30, User.id > 20)).all())
    print(User.query.paginate(page=1, per_page=10).items)
    user = User.query.get(1)
    print(user, user.images.all())
    image = Image.query.get(1)
    print(image, image.user)


@manager.command
def add_image():
    for i in range(5):
        db.session.add(Image('https://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png', 100))
    db.session.commit()


@manager.command
def test():
    print(Image.query.filter_by(user_id=101).first())


@manager.command
def delete_image():
    img = Image.query.filter_by(user_id=101).first()
    db.session.delete(img)
    db.session.commit()

@manager.command
def run_test():
    db.drop_all()
    db.create_all()
    tests = unittest.TestLoader().discover('./')
    unittest.TextTestRunner().run(tests)


if __name__ == '__main__':
    manager.run()