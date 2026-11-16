from aiogram.utils.keyboard import InlineKeyboardBuilder


def subscription_buy(total_stars: int | str):

    builder = InlineKeyboardBuilder()
    builder.button(text=f"Pay {total_stars} ⭐️", pay=True)

    return builder.as_markup()