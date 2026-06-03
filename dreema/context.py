# Import registers if available (auth handler, custom codes, etc.)
import os


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
        # Initialize Database connection
        cls._db = Database()
        db = await cls._db.connect()
        if db.status < 0:
            print(f'==> ❌ Database connection failed: {db.message}')
        else:
            print(f'==> ✔️ Database connected')

        # Initialize and cache routes 
        routePath = os.path.join(AppContext.getAppPath(), 'views', 'endpoints.py')
        if os.path.exists(routePath):
            import importlib.util
            spec = importlib.util.spec_from_file_location('routes', routePath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            routes = getattr(module, 'routes', None)
        cls._routes = Dispatcher.initRoutes()

        # print(cls._routes)
        print(f'==> ✔️ {len(cls._routes["statics"]) + len(cls._routes["dynamics"])} routes loaded')
        return cls

    @classmethod
    async def shutdown(cls):
        """Shutdown all connections at shutdown"""
        if cls._db:
            await cls._db.disconnect()
        return cls