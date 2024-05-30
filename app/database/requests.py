from app.database.models import async_session
from app.database.models import User, Photo
from sqlalchemy import select


async def save_user(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def user_photo_in_base(photo_bytes, user_id):
    async with async_session() as session:
        result = await session.execute(
            select(Photo).filter_by(user_id=user_id, photo_data=photo_bytes)
        )
        photo = result.scalars().first()
        return True if photo else False


async def save_photo(user_photo: bytes, user_id: int, photo_id: str, ):
    async with async_session() as session:
        photo = Photo(photo_data=user_photo, photo_id=photo_id, user_id=user_id)
        session.add(photo)
        await session.commit()


async def get_user_photos(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(Photo).filter(Photo.user_id == user_id))
        photos = result.scalars().all()
        return photos


async def delete_photo_by_bytes(user_id: int, photo_bytes: bytes):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Photo).filter(Photo.user_id == user_id, Photo.photo_data == photo_bytes))
            photo = result.scalars().first()

            if photo:
                await session.delete(photo)
                await session.commit()
                print(f"------------Photo with has been deleted-------------")
