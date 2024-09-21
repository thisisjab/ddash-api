from fastapi import Depends
from api.database.setup import get_session
from typing import Annotated
from sqlalchemy.ext.asyncio import async_sessionmaker


AsyncSession = Annotated[async_sessionmaker, Depends(get_session)]
