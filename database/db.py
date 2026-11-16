from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

def create_engine_and_session(db_url):
    engine = create_async_engine(url=db_url, pool_pre_ping=True, echo=False)

    async_session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    return engine, async_session_maker


