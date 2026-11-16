from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from database.models import User, Group
from database.exceptions import MaxRetriesExceededError
from datetime import datetime, timezone, timedelta
from loguru import logger


async def find_or_create(
        model_type: type[User | Group],
        name: str,
        id: int,
        session: AsyncSession,
        attempts: int,
        max_limit: int
) -> User | Group:
    now = datetime.now(timezone.utc)
    stmt = select(model_type).where(model_type.id == id)
    result = await session.execute(stmt)
    model_obj: Group | User | None = result.scalar_one_or_none()

    if model_obj is None:
        if model_type is User:
            model_obj: User = User(
                id=id,  # type: ignore
                username=name,  # type: ignore
                subscription_until=now  # type: ignore
            )
        elif model_type is Group:
            model_obj: Group = Group(
                id=id,  # type: ignore
                group_name=name,  # type: ignore
                subscription_until=now  # type: ignore
            )
        try:
            session.add(model_obj)
            await session.commit()
            await session.refresh(model_obj)
        except IntegrityError:
            await session.rollback()
            logger.error(f"IntegrityError: {model_type.__name__} (ID: {id}) already exists (race condition), attempt {attempts}/{max_limit}")
            if attempts > max_limit:
                logger.critical(f"Max retries limit ({max_limit}) reached for {model_type.__name__} (ID: {id})")
                raise MaxRetriesExceededError()
            return await find_or_create(
                model_type=model_type,
                id=id, name=name,
                session=session,
                attempts=attempts + 1,
                max_limit=max_limit
            )

    return model_obj  # type: ignore


async def subscription_check(
        model_type: type[User | Group],
        session: AsyncSession,
        id: int
) -> bool:
    now = datetime.now(timezone.utc)
    stmt = select(model_type.subscription_until).where(model_type.id == id)
    subscription: datetime | None = await session.scalar(stmt)  # type: ignore

    if subscription is None:
        user = await find_or_create(
            model_type=model_type,
            session=session,
            id=id,
            attempts=0,
            name=f"{model_type.__name__}: {id}",
            max_limit=3
        )

        if user and user.subscription_until > now:
            return True
        else:
            return False

    if subscription > now:
        return True
    else:
        return False


async def add_subscription_days(
        model_type: type[User | Group],
        session: AsyncSession,
        id: int,
        days: int,
        name: str,
        attempts: int,
        max_limit: int
):
    now = datetime.now(timezone.utc)

    user = await find_or_create(
        model_type=model_type,
        id=id,
        session=session,
        name=name,
        attempts=attempts,
        max_limit=max_limit
    )

    if not user:
        logger.error(f"Failed to find or create {model_type.__name__} (ID: {id}) for adding subscription.")
        return

    subscription_until = (max(now, user.subscription_until)) + timedelta(days=int(days))
    user.subscription_until = subscription_until
    await session.commit()


async def get_subscription_data(
        model_type: type[User | Group],
        session: AsyncSession,
        id: int
):
    stmt = select(model_type.subscription_until).where(model_type.id == id)
    date: datetime | None = await session.scalar(stmt)

    if date is None:
        logger.error(f"Subscription data not found for {model_type.__name__} (ID: {id})")
        return None

    local_data = date.strftime("%d %B %Y, %H:%M")
    return local_data