import os

class AppContext:
    _redis = None
    _db = None
    _routes = None

    def __init__(self):
        pass

    @classmethod
    def getAppPath(cls):
        return os.environ.get('DREEMA_APP_PATH')

    @classmethod
    def db(cls):
        from dreema.orm.database import Database
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
        from dreema.orm.database import Database
        from dreema.routing import Dispatcher

        """Initialize all connections at startup"""

        # import register
        try:
            import plug
        except ImportError:
            pass

        # Initialize Database connection
        try:
            import endpoints
            routes = getattr(endpoints, 'routes', [])
            cls._routes = Dispatcher.initRoutes(routes=routes)
            print(f'==> 🟢 {len(cls._routes["statics"]) + len(cls._routes["dynamics"])} routes loaded')
            
        except Exception as e:
            print("=> 🔴 Dreema startup failed: unable to load application endpoints.")
            raise e


        cls._db = Database()
        db = await cls._db.connect()
        if db.status < 0:
            print(f'==> 🔴 Database not connected')
        else:
            print(f'==> 🟢 Database connected')
        return cls

    @classmethod
    async def shutdown(cls):
        """Shutdown all connections at shutdown"""
        if cls._db:
            await cls._db.disconnect()
        return cls