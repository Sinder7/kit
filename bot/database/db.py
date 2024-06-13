from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, Boolean
from config import DATABASE_URI, admins

engine = create_engine(DATABASE_URI)
engine: AsyncEngine = create_async_engine(
    url=url,
    echo=echo,
    echo_pool=echo_pool,
    pool_size=pool_size,
    max_overflow=max_overflow,
)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()


class User(Base):

    tablename = "users"
    id = Column(
        BigInteger, primary_key=True
    )  #! Обязательно BigInteger поскольку id tg может содержать большое количество символов
    name = Column(String(50))
    username = Column(String(50))
    group = Column(String(32))
    status = Column(String(32))
    notify = Column(Boolean, default=True)

    def __init__(
        self,
        id=None,
        name=None,
        username=None,
        group=None,
        status="студент",
        notify=False,
    ):
        self.id = id
        self.name = name.lower() if name else None
        self.username = username
        self.group = group.lower() if group else None
        self.status = str(status).lower()
        self.notify = notify

    @classmethod
    async def if_user_exists(cls, id: int) -> Optional["User"]:
        async with async_session() as session:
            user = await session.execute(select(User).where(User.id == id))
            return user.scalar_one_or_none()

    async def add(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()

    @classmethod
    async def get_user(cls, id: int) -> Optional["User"]:
        async with async_session() as session:
            user = await session.execute(select(User).where(User.id == id))
            return user.scalar_one_or_none()

    @classmethod
    async def get_all_group(cls, group: str) -> list["User"]:
        group = group.lower()
        async with async_session() as session:
            users = await session.execute(select(User).where(User.group == group))
            return users.scalars().all()

    @classmethod
    async def get_all(cls) -> list["User"]:
        async with async_session() as session:
            users = await session.execute(select(User))
            return users.scalars().all()

    @classmethod
    async def get_all_notify(cls) -> list["User"]:
        async with async_session() as session:
            users = await session.execute(select(User).where(User.notify == True))
            return users.scalars().all()

    async def update(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()

    async def delete(self):
        async with async_session() as session:
            await session.delete(self)
            await session.commit()

    def is_teacher(self) -> bool:
        return self.status == "преподаватель" or self.id in admins

    async def reverse_notify(self):
        self.notify = not self.notify
        async with async_session() as session:
            session.add(self)
            await session.commit()
