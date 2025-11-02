from dataclasses import asdict

from sqlalchemy import Select

from aris_api.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='Julio',
            email='julio@gmail.com',
            password='123412341234',
        )
        session.add(new_user)
        session.commit()

        user = session.scalar(Select(User).where(User.username == 'Julio'))

        assert asdict(user) == {
            'id': 1,
            'username': 'Julio',
            'email': 'julio@gmail.com',
            'password': '123412341234',
            'created_at': time,
        }
