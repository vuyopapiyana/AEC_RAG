import asyncio
from src.db.database import init_db
from src.db.models import * # Import all models to ensure they are registered

if __name__ == "__main__":
    asyncio.run(init_db())
