import asyncpg

class Database:
    def __init__(self, dsn):
        self.dsn = dsn
        self.pool = None

    async def init(self, min, max):
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.dsn,
                min_size=min,
                max_size=max
            )
            print("Database connection pool initialized.")
        except Exception as e:
            print(f"Error initializing database pool: {e}")

    async def close(self):
        if self.pool:
            await self.pool.close()
            print("Database connection pool closed.")

    async def fetchval(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def fetchrow(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetch(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def execute(self, query, *args):
        if not self.pool:
            raise RuntimeError("Database pool not initialized.")
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
