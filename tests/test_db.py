from dataclasses import asdict

from sqlalchemy import select

from aris_api.models import User


def test_create_user(db_session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='Julio',
            email='julio@gmail.com',
            password='123412341234',
        )
        db_session.add(new_user)
        db_session.commit()

        user = db_session.scalar(select(User).where(User.username == 'Julio'))

        assert asdict(user) == {
            'id': 1,
            'username': 'Julio',
            'email': 'julio@gmail.com',
            'password': '123412341234',
            'created_at': time,
        }
