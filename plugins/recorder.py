#!/usr/bin/env python3
# Copyright (C) @subinps
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from utils import LOGGER
from config import Config
from pyrogram import (
    Client, 
    filters
)
from utils import (
    chat_filter, 
    is_admin, 
    is_admin, 
    delete_messages, 
    recorder_settings,
    sync_to_db
)
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)

admin_filter=filters.create(is_admin) 


@Client.on_message(filters.command(["record", f"record@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def record_vc(bot, message):
    await message.reply("• بخش مورد نظر را انتخاب کنید :\n─┅━ صفحه ضبط ━┅─ㅤㅤ ㅤ", reply_markup=(await recorder_settings()))
    await delete_messages([message])

@Client.on_message(filters.command(["rtitle", f"rtitle@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def recording_title(bot, message):
    m=await message.reply("•  درحال بررسی ...")
    if " " in message.text:
        cmd, title = message.text.split(" ", 1)
    else:
        await m.edit("•  عنوان جدید از الگوی زیر استفاده نمایید.\n<code>/rtitle عنوان سفارشی</code>\n◂برای برگشت به حالت پیشفرض از عبارت False بعد از توشتن  دستور استفاده کنید.")
        await delete_messages([message, m])
        return

    if Config.DATABASE_URI:
        await m.edit("دیتابیس یافت شد. درحال تنظیم عنوان ضبط ...") 
        if title == "False":
            await m.edit(f"عنوان ضبط سفارشی با موفقیت حذف شد.")
            Config.RECORDING_TITLE=False
            await sync_to_db()
            await delete_messages([message, m])           
            return
        else:
            Config.RECORDING_TITLE=title
            await sync_to_db()
            await m.edit(f"• عنوان ضبط با موفقیت تغییر یافت به  {title}")
            await delete_messages([message, m])
            return
    else:
        if not Config.HEROKU_APP:
            buttons = [[InlineKeyboardButton('Heroku API_KEY', url='https://dashboard.heroku.com/account/applications/authorizations/new'), InlineKeyboardButton('🗑 Close', callback_data='close'),]]
            await m.edit(
                text="No heroku app found, this command needs the following heroku vars to be set.\n\n1. <code>HEROKU_API_KEY</code>: Your heroku account api key.\n2. <code>HEROKU_APP_NAME</code>: Your heroku app name.", 
                reply_markup=InlineKeyboardMarkup(buttons)) 
            await delete_messages([message])
            return     
        config = Config.HEROKU_APP.config()
        if title == "False":
            if "RECORDING_TITLE" in config:
                await m.edit(f"• عنوان ضبط سفارشی با موفقیت حذف شد.درحال راه اندازی مجدد ...")
                await delete_messages([message])
                del config["RECORDING_TITLE"]                
                config["RECORDING_TITLE"] = None
            else:
                await m.edit(f"• در حال حاضر عنوان پیش فرض تنظیم شده است. تغییراتی ایجاد نشده است.")
                Config.RECORDING_TITLE=False
                await delete_messages([message, m])
        else:
            await m.edit(f"عنوان ضبط با موفقیت به {title} تغییر کرد، درحال راه اندازی مجدد ...")
            await delete_messages([message])
            config["RECORDING_TITLE"] = title
