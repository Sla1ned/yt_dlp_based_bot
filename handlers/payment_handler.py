from aiogram import Router, F
from aiogram.types import LabeledPrice, PreCheckoutQuery, Message
from aiogram.filters import Command, CommandObject
from aiogram.enums import ChatType
from keyboards.keyboard import subscription_buy
from database.requests import add_subscription_days
from database.models import Group, User
from database.exceptions import MaxRetriesExceededError
from sqlalchemy.ext.asyncio import AsyncSession
from settings import settings
from loguru import logger
import html

rt = Router()

STARS_PER_DAY = settings.stars_per_day
MAX_DAYS = 365

@rt.message(Command("buy"))
async def buy_subscription_handler(message: Message, command: CommandObject):
    user_id = message.from_user.id if message.from_user else "Unknown"

    if not command.args or not command.args.isdigit():
        logger.error(f"User {user_id} entered invalid days format: {command.args}")
        await message.answer(
            "❌ <b>Invalid format!</b>\n\n"
            "Make sure you entered the command correctly:\n"
            "<code>/buy number_of_days</code> (e.g., <code>/buy 32</code>)"
        )
        return

    days = int(command.args)

    if days <= 0:
        logger.error(f"User {user_id} entered negative or zero days: {days}")
        await message.answer("⚠️ <b>The number of days must be greater than 0.</b>")
        return

    if days > MAX_DAYS:
        logger.error(f"User {user_id} requested too many days: {days} (max {MAX_DAYS})")
        await message.answer(f"⚠️ <b>Maximum subscription length is {MAX_DAYS} days.</b>")
        return

    days_price = days * STARS_PER_DAY
    prices = [LabeledPrice(label="Premium subscription", amount=days_price)]

    await message.answer_invoice(
        title="⭐ Premium Subscription",
        description=f"Unlock video downloads for {days} days. Fast and without limits!",
        payload=f"sub:{days}",
        provider_token="",
        currency="XTR",
        prices=prices,
        reply_markup=subscription_buy(total_stars=days_price),
    )


@rt.pre_checkout_query()
async def checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@rt.message(F.successful_payment)
async def process_successful_payment(message: Message, session: AsyncSession):
    invoice = message.successful_payment.invoice_payload
    charge_id = message.successful_payment.telegram_payment_charge_id

    if not invoice.startswith("sub:"):
        logger.error(f"Received payment with unknown payload: {invoice}, charge_id: {charge_id}")
        return

    if not message.from_user: return

    days = int(invoice.split(":")[1])
    user_id = message.from_user.id

    try:
        if message.chat.type == ChatType.PRIVATE:
            user_name = message.from_user.username or message.from_user.first_name or f"User: {message.from_user.id}"
            await add_subscription_days(
                model_type=User,
                session=session,
                id=message.from_user.id,
                days=days,
                name=user_name,
                attempts=0,
                max_limit=3
            )
            await message.answer(
                f"🎉 <b>Payment successful!</b>\n\n"
                f"Your premium subscription has been activated for <b>{days} days</b>.\n"
                f"<i>You can now download videos without limits!</i>"
            )

        elif message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            title = message.chat.title or f"Base_Group: {message.chat.id}"
            await add_subscription_days(
                model_type=Group,
                session=session,
                id=message.chat.id,
                days=days,
                name=title,
                attempts=0,
                max_limit=3
            )

            buyer_name = message.from_user.username or message.from_user.first_name
            safe_name = html.escape(buyer_name)
            await message.answer(
                f"🚀 <b>Group Subscription Extended!</b>\n\n"
                f"User <b>{safe_name}</b> has extended the group's subscription for <b>{days} days</b>.\n"
                f"<i>Thank you for supporting the bot!</i>"
            )

    except MaxRetriesExceededError:
        logger.critical(f"Activation failed after retries. Charge ID: {charge_id}, User: {user_id}, Days: {days}")

        try:
            await message.bot.refund_star_payment(
                user_id=message.from_user.id,
                telegram_payment_charge_id=charge_id
            )

            await message.answer(
                "⚠️ <b>Technical Error</b>\n\n"
                "Something went wrong while activating your subscription.\n"
                "Your stars have been <b>successfully refunded</b> to your balance. Please try again later."
            )
        except Exception as refund_err:
            logger.critical(f"Refund failed. Charge ID: {charge_id}, User: {user_id}, Error: {refund_err}")
            await message.answer(
                "❌ <b>Critical Error</b>\n\n"
                "An error occurred while activating the subscription, and the automatic refund of stars failed.\n"
                "Please contact support for assistance."
            )