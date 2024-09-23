from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker

from api.database.setup import get_session

AsyncSession = Annotated[async_sessionmaker, Depends(get_session)]
