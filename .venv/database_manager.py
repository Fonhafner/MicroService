import asyncpg

class PostgreSQLDatabase:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.connection = None

    async def connect(self):
        if self.connection is None or self.connection.is_closed():
            self.connection = await asyncpg.connect(self.dsn)

    async def close(self):
        if self.connection and not self.connection.is_closed():
            await self.connection.close()

    async def get_user_by_username(self, username: str):
        await self.connect()
        async with self.connection.transaction():
            query = "SELECT * FROM users WHERE username = $1"
            return await self.connection.fetchrow(query, username)

    async def get_all_usernames(self):
        await self.connect()
        async with self.connection.transaction():
            query = "SELECT username FROM users"
            return [record['username'] for record in await self.connection.fetch(query)]

    async def check_password(self, username: str, password: str):
        user = await self.get_user_by_username(username)
        if user:
            return user['passwd'] == password
        return False

    async def create_user(self, username: str, email: str, passwd: str):
        await self.connect()
        async with self.connection.transaction():
            query = "INSERT INTO users (username, email, passwd) VALUES ($1, $2, $3)"
            await self.connection.execute(query, username, email, passwd)
