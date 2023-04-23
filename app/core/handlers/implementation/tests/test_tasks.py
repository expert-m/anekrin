import pytest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from emoji import emojize

from ....constants import BotCommand, CallbackCommands
from ....services.tasks import TaskManager
from ....services.telegram import TelegramMessageHandler
from ....tests.utils import create_mocked_class_for_message
from ..... import models
from .....common.tests.dto import ExpectedCall, ExpectedCalls
from .....common.tests.utils import generate_random_raw_user, generate_random_string, generate_telegram_update_for_text


@pytest.mark.asyncio
async def test_show_tasks_without_tasks() -> None:
    sender = generate_random_raw_user()
    await models.User.create(telegram_user_id=sender['id'])
    telegram_update = generate_telegram_update_for_text(
        BotCommand.SHOW_TASKS,
        sender=sender,
    )

    message_class, calls = create_mocked_class_for_message()
    handler = TelegramMessageHandler(message_class=message_class)

    await handler.process_update(telegram_update, immediately=True)

    ExpectedCalls(
        ExpectedCall(
            name='answer',
            args__0__contains='You don\'t have tasks',
            args__len=1,
            kwargs__keys={'reply_markup'},
        ),
    ).compare_with(calls)


@pytest.mark.asyncio
async def test_show_tasks() -> None:
    sender = generate_random_raw_user()
    user = await models.User.create(telegram_user_id=sender['id'])
    task_manager = TaskManager(user=user)
    first_task = await task_manager.create_task(name=generate_random_string(10), reward=20)
    second_task = await task_manager.create_task(name=generate_random_string(10), reward=20)
    await task_manager.create_work_log(task=second_task)
    await task_manager.create_work_log(task=second_task)

    telegram_update = generate_telegram_update_for_text(
        BotCommand.SHOW_TASKS,
        sender=sender,
    )
    message_class, calls = create_mocked_class_for_message()
    handler = TelegramMessageHandler(message_class=message_class)

    await handler.process_update(telegram_update, immediately=True)

    ExpectedCalls(
        ExpectedCall(
            name='answer',
            args=('Your current tasks:',),
            kwargs__len=0,
        ),
        ExpectedCall(
            name='answer',
            args__0__contains=first_task.name,
            args__len=1,
            kwargs__keys={'reply_markup', 'parse_mode'},
            kwargs__reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    f'{emojize(":check_box_with_check:")} Complete',
                    callback_data=f'{CallbackCommands.COMPLETE_TASK} {first_task.id}',
                ),
                InlineKeyboardButton(
                    f'{emojize(":pencil:")} Edit',
                    callback_data=f'{CallbackCommands.EDIT_TASK} {first_task.id}',
                ),
            ]])
        ),
        ExpectedCall(
            name='answer',
            args__0__contains=second_task.name,
            args__len=1,
            kwargs__keys={'reply_markup', 'parse_mode'},
            kwargs__reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    f'{emojize(":check_mark_button:")} Complete (2)',
                    callback_data=f'{CallbackCommands.COMPLETE_TASK} {second_task.id}',
                ),
                InlineKeyboardButton(
                    f'{emojize(":pencil:")} Edit',
                    callback_data=f'{CallbackCommands.EDIT_TASK} {second_task.id}',
                ),
            ]])
        ),
        ExpectedCall(
            name='answer',
            args=('Or do you want to do something else?',),
        ),
    ).compare_with(calls)
