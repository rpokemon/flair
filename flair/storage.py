import json
import uuid

from datetime import datetime, timedelta

from aiohttp_session import AbstractStorage, Session
from donphan import Column, MaybeAcquire, SQLType, Table


class _HTTP_Sessions(Table):
    key: SQLType.UUID = Column(primary_key=True)
    data: SQLType.JSONB
    expires: SQLType.Timestamp = Column(nullable=True, index=True)

    @classmethod
    async def load_session(cls, key, connection=None):
        async with MaybeAcquire(connection) as connection:
            return await connection.fetchrow(f"""SELECT * FROM {cls._name}
                WHERE key = $1 AND (expires IS NULL or expires > NOW() AT TIME ZONE 'UTC')
                """, key)

    @classmethod
    async def save_session(cls, key, data, expires, connection=None):
        async with MaybeAcquire(connection) as connection:
            await connection.execute(f"""INSERT INTO {cls._name}
                VALUES ($1, $2, $3)
                ON CONFLICT (key) DO UPDATE SET
                    data=EXCLUDED.data,
                    expires=EXCLUDED.expires
                """, key, data, expires)

    @classmethod
    async def delete_expired_sessions(cls, connection=None):
        async with MaybeAcquire(connection) as connection:
            await connection.execute(f"""DELETE FROM {cls._name}
                WHERE expires <= NOW() AT TIME ZONE 'UTC""")


class PostgresStorage(AbstractStorage):

    def __init__(self, *, cookie_name='AIOHTTP_SESSION',
                 domain=None, max_age=None, path='/',
                 secure=None, httponly=True,
                 key_factory=lambda: uuid.uuid4().hex,
                 encoder=json.dumps, decoder=json.loads):
        super().__init__(cookie_name=cookie_name, domain=domain,
                         max_age=max_age, path=path, secure=secure,
                         httponly=httponly,
                         encoder=encoder, decoder=decoder)

        self._key_factory = key_factory

    async def load_session(self, request):
        cookie = self.load_cookie(request)
        if cookie is None:
            return Session(None, data=None, new=True, max_age=self.max_age)

        else:
            # Load session from DB
            key = uuid.UUID(str(cookie))
            response = await _HTTP_Sessions.load_session(key)

            if response is None:
                return Session(None, data=None, new=True, max_age=self.max_age)
            else:
                return Session(key, data=response['data'], new=False, max_age=self.max_age)

    async def save_session(self, request, response, session):
        key = session.identity
        if key is None:
            key = self._key_factory()
            self.save_cookie(response, key, max_age=session.max_age)

        else:
            if session.empty:
                self.save_cookie(response, '', max_age=session.max_age)
            else:
                key = str(key)
                self.save_cookie(response, key, max_age=session.max_age)

        # Save session to DB
        data = self._get_session_data(session)
        expires = datetime.utcnow() + timedelta(seconds=session.max_age) if session.max_age else None
        await _HTTP_Sessions.save_session(key, data, expires)
