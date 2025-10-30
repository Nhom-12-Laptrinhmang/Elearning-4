from app.database import SessionLocal, Base, engine, Blog, User
from app.services.auth_service import hash_password


def seed():
    # Ensure tables created
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # create demo user if not exists
        if not db.query(User).filter(User.username == 'alice').first():
            user = User(username='alice', hashed_password=hash_password('secret'))
            db.add(user)
            db.commit()
            print('Created user: alice / secret')
        else:
            print('User alice already exists')

        # create sample blogs if none
        if db.query(Blog).count() == 0:
            b1 = Blog(title='Hello world', content='This is the first sample post')
            b2 = Blog(title='Second post', content='Another sample blog')
            db.add_all([b1, b2])
            db.commit()
            print('Created 2 sample blogs')
        else:
            print('Blogs already exist, skipping blog creation')
    finally:
        db.close()


if __name__ == '__main__':
    seed()
