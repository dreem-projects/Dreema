from dreema.orm.database import Database
from dreema.redis.actions import Redis
from dreema.routing import Dispatcher

# Import registers if available (auth handler, custom codes, etc.)
try:
    import registers
except ImportError:
    # registers.py not created yet - that's okay
    pass 

class AppContext:
    _redis = None
    _db = None
    _routes = None

    def __init__(self):
        pass

    @classmethod
    def redis(cls):
        """Get or create Redis instance (singleton)"""
        if not cls._redis:
            cls._redis = Redis()
        return cls._redis

    @classmethod
    def db(cls):
        """Get or create Database instance (singleton)"""
        if not cls._db:
            cls._db = Database()
            
        return cls._db

    @classmethod
    def routes(cls):
        """Get cached routes"""
        return cls._routes

    @classmethod
    async def init(cls):
        """Initialize all connections at startup"""
        # Initialize Redis
        cls._redis = Redis()
        rd = cls._redis.connect()
        if rd.status < 0:
            print(f'==> ❌ Redis connection failed: {rd.message}')
        else:
            print(f'==> ✔️ Redis connected')
        
        # Initialize Database connection
        cls._db = Database()
        db = await cls._db.connect()
        if db.status < 0:
            print(f'==> ❌ Database connection failed: {db.message}')
        else:
            print(f'==> ✔️ Database connected')

        # Initialize and cache routes
        cls._routes = Dispatcher.initRoutes()

        # print(cls._routes)
        print(f'==> ✔️ {len(cls._routes["statics"]) + len(cls._routes["dynamics"])} routes loaded')
        return cls

    @classmethod
    async def shutdown(cls):
        """Shutdown all connections at shutdown"""
        if cls._redis:
            await cls._redis.disconnect()
        if cls._db:
            await cls._db.disconnect()
        return cls