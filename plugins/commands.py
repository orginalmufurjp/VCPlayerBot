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
from contextlib import suppress
from config import Config
import calendar
import pytz
from datetime import datetime
import asyncio
import os
from pyrogram.errors.exceptions.bad_request_400 import (
    MessageIdInvalid, 
    MessageNotModified
)
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from utils import (
    cancel_all_schedules,
    edit_config, 
    is_admin, 
    leave_call, 
    restart,
    restart_playout,
    stop_recording, 
    sync_to_db,
    update, 
    is_admin, 
    chat_filter,
    sudo_filter,
    delete_messages,
    seek_file
)
from pyrogram import (
    Client, 
    filters
)

IST = pytz.timezone(Config.TIME_ZONE)
if Config.DATABASE_URI:
    from utils import db

HOME_TEXT = "<b>سلام  [{}](tg://user?id={}) 🙋‍♂️\n\nمن یک ربات پخش کننده موسیقی، فایل صوتی ویدیوها در چت های صوتی تلگرام (کانال،گروه)  هستم. همچنین من میتوانم می توانم هر ویدیوی یوتیوب یا یک فایل تلگرام یا حتی یک یوتیوب زنده را نیز پخش کنم.\n\nامکانات بسیار زیادی دارم. برای نصب و فعالسازی ربات روی دکمه 🧩 درخواست نصب ربات کلیک کرده و با سازنده من، مکاتبه نمایید.</b>"
admin_filter=filters.create(is_admin) 

@Client.on_message(filters.command(['start', f"start@{Config.BOT_USERNAME}"]))
async def start(client, message):
    if len(message.command) > 1:
        if message.command[1] == 'help':
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(f"• پخش", callback_data='help_play'),
                        InlineKeyboardButton(f"• تنظیمات", callback_data=f"help_settings"),
                        InlineKeyboardButton(f"• ضبط", callback_data='help_record'),
                    ],
                    [
                        InlineKeyboardButton("• زمان بندی", callback_data="help_schedule"),
                        InlineKeyboardButton("• کنترل", callback_data='help_control'),
                        InlineKeyboardButton("• مدیریت", callback_data="help_admin"),
                    ],
                    [
                        InlineKeyboardButton(f"• تنظیمات بیشتر", callback_data='help_misc'),
                        InlineKeyboardButton("• تایید و خروج", callback_data="close"),
                    ],
                ]
                )
            await message.reply("◂ بخش مورد نظر را انتخاب نمایید :\n─┅━ صفحه راهنما ━┅─",
                reply_markup=reply_markup,
                disable_web_page_preview=True
                )
        elif 'sch' in message.command[1]:
            msg=await message.reply("Checking schedules..")
            you, me = message.command[1].split("_", 1)
            who=Config.SCHEDULED_STREAM.get(me)
            if not who:
                return await msg.edit("Something gone somewhere.")
            del Config.SCHEDULED_STREAM[me]
            whom=f"{message.chat.id}_{msg.message_id}"
            Config.SCHEDULED_STREAM[whom] = who
            await sync_to_db()
            if message.from_user.id not in Config.ADMINS:
                return await msg.edit("OK da")
            today = datetime.now(IST)
            smonth=today.strftime("%B")
            obj = calendar.Calendar()
            thisday = today.day
            year = today.year
            month = today.month
            m=obj.monthdayscalendar(year, month)
            button=[]
            button.append([InlineKeyboardButton(text=f"{str(smonth)}  {str(year)}",callback_data=f"sch_month_choose_none_none")])
            days=["Mon", "Tues", "Wed", "Thu", "Fri", "Sat", "Sun"]
            f=[]
            for day in days:
                f.append(InlineKeyboardButton(text=f"{day}",callback_data=f"day_info_none"))
            button.append(f)
            for one in m:
                f=[]
                for d in one:
                    year_=year
                    if d < int(today.day):
                        year_ += 1
                    if d == 0:
                        k="\u2063"   
                        d="none"   
                    else:
                        k=d    
                    f.append(InlineKeyboardButton(text=f"{k}",callback_data=f"sch_month_{year_}_{month}_{d}"))
                button.append(f)
            button.append([InlineKeyboardButton("Close", callback_data="schclose")])
            await msg.edit(f"◂ روزی را که می‌خواهید چت صوتی را برنامه‌ ریزی کنید، انتخاب کنید.\nامروز {thisday} {smonth} {year} است. انتخاب تاریخ قبل از امروز به عنوان سال آینده در نظر گرفته می شود {year+1}", reply_markup=InlineKeyboardMarkup(button))



        return
    buttons = [
        [
            InlineKeyboardButton('⚙️ کانال دیجی گرام 24', url='https://t.me/DigiGram24'),
            InlineKeyboardButton('🧩 درخواست نصب ربات', url='https://t.me/DIGRM')
        ],
        [
            InlineKeyboardButton('👨🏼‍🦯 راهنما', callback_data='help_main'),
            InlineKeyboardButton('🗑 بستن', callback_data='close'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    k = await message.reply(HOME_TEXT.format(message.from_user.first_name, message.from_user.id), reply_markup=reply_markup)
    await delete_messages([message, k])



@Client.on_message(filters.command(["help", f"help@{Config.BOT_USERNAME}"]))
async def show_help(client, message):
    reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("• پخش", callback_data='help_play'),
                InlineKeyboardButton("• تنظیمات", callback_data=f"help_settings"),
                InlineKeyboardButton("• ضبط", callback_data='help_record'),
            ],
            [
                InlineKeyboardButton("• زمان بندی", callback_data="help_schedule"),
                InlineKeyboardButton("• کنترل", callback_data='help_control'),
                InlineKeyboardButton("• مدیریت", callback_data="help_admin"),
            ],
            [
                InlineKeyboardButton("• تنظیمات بیشتر", callback_data='help_misc'),
                InlineKeyboardButton("• پیکربندی", callback_data='help_env'),
                InlineKeyboardButton("• تایید و خروج", callback_data="close"),
            ],
        ]
        )
    if message.chat.type != "private" and message.from_user is None:
        k=await message.reply(
            text="من نمی توانم در اینجا به شما کمک کنم، زیرا شما یک مدیر ناشناس هستید.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(f"Help", url=f"https://telegram.dog/{Config.BOT_USERNAME}?start=help"),
                    ]
                ]
            ),)
        await delete_messages([message, k])
        return
    if Config.msg.get('help') is not None:
        await Config.msg['help'].delete()
    Config.msg['help'] = await message.reply_text(
        "◂ بخش مورد نظر را انتخاب نمایید :\n─┅━ صفحه راهنما ━┅─",
        reply_markup=reply_markup,
        disable_web_page_preview=True
        )
    #await delete_messages([message])
@Client.on_message(filters.command(['repo', f"repo@{Config.BOT_USERNAME}"]))
async def repo_(client, message):
    buttons = [
        [
            InlineKeyboardButton('🧩 سازنده ربات', url='https://t.me/DIGRM'),
            InlineKeyboardButton('⚙️ کانال ربات', url='https://t.me/DigiGram24'),     
        ],
        [
            InlineKeyboardButton("🎞 نحوه فعالسازی ربات", url='https://t.me/DIGRM'),
            InlineKeyboardButton('🗑 خروج', callback_data='close'),
        ]
    ]
    await message.reply("<b>برای اطلاع  بیشتر و نصب ربات پخش کننده موزیک و ویدیو در گروهتان با آیدی سازنده ربات در ارتباط باشید. <a href=https://t.me/DIGRM>DigiGram24.</a>\n هم ویدیو هم موزیک قابل پخش است.\n\nبدون محدویت حجم فایل 🙃.</b>", reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
    await delete_messages([message])

@Client.on_message(filters.command(['restart', 'update', f"restart@{Config.BOT_USERNAME}", f"update@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def update_handler(client, message):
    if Config.HEROKU_APP:
        k = await message.reply("✅ فایل برنامه DIGI پیدا شد، ربات برای بروزرسانی مجدد راه‌اندازی می‌شود.")
        if Config.DATABASE_URI:
            msg = {"msg_id":k.message_id, "chat_id":k.chat.id}
            if not await db.is_saved("RESTART"):
                db.add_config("RESTART", msg)
            else:
                await db.edit_config("RESTART", msg)
            await sync_to_db()
    else:
        k = await message.reply("😥 هیچ فایل برنامه DIGI یافت نشد، در حال تلاش برای راه اندازی مجدد.")
        if Config.DATABASE_URI:
            msg = {"msg_id":k.message_id, "chat_id":k.chat.id}
            if not await db.is_saved("RESTART"):
                db.add_config("RESTART", msg)
            else:
                await db.edit_config("RESTART", msg)
    try:
        await message.delete()
    except:
        pass
    await update()

@Client.on_message(filters.command(['logs', f"logs@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def get_logs(client, message):
    m=await message.reply("Checking logs..")
    if os.path.exists("botlog.txt"):
        await message.reply_document('botlog.txt', caption="Bot Logs")
        await m.delete()
        await delete_messages([message])
    else:
        k = await m.edit("◂ هیچ فایل گزارشی یافت نشد.")
        await delete_messages([message, k])

@Client.on_message(filters.command(['env', f"env@{Config.BOT_USERNAME}", "config", f"config@{Config.BOT_USERNAME}"]) & sudo_filter & chat_filter)
async def set_heroku_var(client, message):
    with suppress(MessageIdInvalid, MessageNotModified):
        m = await message.reply("◂ در حال بررسی تنظیمات پیکربندی...")
        if " " in message.text:
            cmd, env = message.text.split(" ", 1)
            if "=" in env:
                var, value = env.split("=", 1)
            else:
                if env == "STARTUP_STREAM":
                    env_ = "STREAM_URL"
                elif env == "QUALITY":
                    env_ = "CUSTOM_QUALITY" 
                else:
                    env_ = env
                ENV_VARS = ["ADMINS", "SUDO", "CHAT", "LOG_GROUP", "STREAM_URL", "SHUFFLE", "ADMIN_ONLY", "REPLY_MESSAGE", 
                        "EDIT_TITLE", "RECORDING_DUMP", "RECORDING_TITLE", "IS_VIDEO", "IS_LOOP", "DELAY", "PORTRAIT", 
                        "IS_VIDEO_RECORD", "PTN", "CUSTOM_QUALITY"]
                if env_ in ENV_VARS:
                    await m.edit(f"Current Value for `{env}`  is `{getattr(Config, env_)}`")
                    await delete_messages([message])
                    return
                else:
                    await m.edit("ورودی ارسالی نامعتبر است. از سازنده ربات (@DIGRM) درخواست کمک نمایید.")
                    await delete_messages([message, m])
                    return     
            
        else:
            await m.edit("شما دسترسی لازم برای تغییر تنظیمات پیکربندی اصلی را ندارید.")
            await delete_messages([message, m])
            return

        if Config.DATABASE_URI and var in ["STARTUP_STREAM", "CHAT", "LOG_GROUP", "REPLY_MESSAGE", "DELAY", "RECORDING_DUMP", "QUALITY"]:      
            await m.edit("◂ دیتابیس یافت شد. درحال انجام تنظیمات پیکربندی ربات...")
            await asyncio.sleep(2)  
            if not value:
                await m.edit(f"◂ هیچ مقداری برای پیکربندی مشخص نشده است. در حال تلاش برای حذف پیکربندی {var}.")
                await asyncio.sleep(2)
                if var in ["STARTUP_STREAM", "CHAT", "DELAY"]:
                    await m.edit("◂این یک نسخه اجباری است و نمی توان آن را حذف کرد.")
                    await delete_messages([message, m]) 
                    return
                await edit_config(var, False)
                await m.edit(f"Sucessfully deleted {var}")
                await delete_messages([message, m])           
                return
            else:
                if var in ["CHAT", "LOG_GROUP", "RECORDING_DUMP", "QUALITY"]:
                    try:
                        value=int(value)
                    except:
                        if var == "QUALITY":
                            if not value.lower() in ["low", "medium", "high"]:
                                await m.edit("◂ شما باید مقداری بین 10 - 100 مشخص کنید.")
                                await delete_messages([message, m])
                                return
                            else:
                                value = value.lower()
                                if value == "high":
                                    value = 100
                                elif value == "medium":
                                    value = 66.9
                                elif value == "low":
                                    value = 50
                        else:
                            await m.edit("◂ شما باید یک آیدی گروه را وارد کنید. آیدی عددی باید یک عدد صحیح باشد.")
                            await delete_messages([message, m])
                            return
                    if var == "CHAT":
                        await leave_call()
                        Config.ADMIN_CACHE=False
                        if Config.IS_RECORDING:
                            await stop_recording()
                        await cancel_all_schedules()
                        Config.CHAT=int(value)
                        await restart()
                    await edit_config(var, int(value))
                    if var == "QUALITY":
                        if Config.CALL_STATUS:
                            data=Config.DATA.get('FILE_DATA')
                            if not data \
                                or data.get('dur', 0) == 0:
                                await restart_playout()
                                return
                            k, reply = await seek_file(0)
                            if k == False:
                                await restart_playout()
                    await m.edit(f"◂ با موفقیت تغییر کرد {var} به {value}")
                    await delete_messages([message, m])
                    return
                else:
                    if var == "STARTUP_STREAM":
                        Config.STREAM_SETUP=False
                    await edit_config(var, value)
                    await m.edit(f"◂ با موفقیت تغییر کرد {var} به {value}")
                    await delete_messages([message, m])
                    await restart_playout()
                    return
        else:
            if not Config.HEROKU_APP:
                buttons = [[InlineKeyboardButton('Heroku API_KEY', url='https://dashboard.heroku.com/account/applications/authorizations/new'), InlineKeyboardButton('🗑 Close', callback_data='close'),]]
                await m.edit(
                    text="◂ هیچ برنامه DIGI یافت نشد، این دستور نیاز تنظیم از سرور دارد.", 
                    reply_markup=InlineKeyboardMarkup(buttons)) 
                await delete_messages([message])
                return     
            config = Config.HEROKU_APP.config()
            if not value:
                await m.edit(f"هیچ مقداری برای پیکربندی مشخص نشده است. تلاش برای حذف پیکربندی {var}.")
                await asyncio.sleep(2)
                if var in ["STARTUP_STREAM", "CHAT", "DELAY", "API_ID", "API_HASH", "BOT_TOKEN", "SESSION_STRING", "ADMINS"]:
                    await m.edit("◂ این ها متغیرهای اجباری هستند و نمی توان آنها را حذف کرد.")
                    await delete_messages([message, m])
                    return
                if var in config:
                    await m.edit(f"◂ با موفقیت حذف شد {var}")
                    await asyncio.sleep(2)
                    await m.edit("◂ اکنون برنامه را مجدداً راه اندازی کنید تا تغییرات ایجاد شود.")
                    if Config.DATABASE_URI:
                        msg = {"msg_id":m.message_id, "chat_id":m.chat.id}
                        if not await db.is_saved("RESTART"):
                            db.add_config("RESTART", msg)
                        else:
                            await db.edit_config("RESTART", msg)
                    del config[var]                
                    config[var] = None               
                else:
                    k = await m.edit(f"No env named {var} found. Nothing was changed.")
                    await delete_messages([message, k])
                return
            if var in config:
                await m.edit(f"متغیر قبلاً پیدا شده است. در حال حاضر ویرایش شده است به {value}")
            else:
                await m.edit(f"◂متغیر یافت نشد، اکنون به عنوان پیکربندی جدید تنظیم می شود.")
            await asyncio.sleep(2)
            await m.edit(f"Succesfully set {var} with value {value}, Now Restarting to take effect of changes...")
            if Config.DATABASE_URI:
                msg = {"msg_id":m.message_id, "chat_id":m.chat.id}
                if not await db.is_saved("RESTART"):
                    db.add_config("RESTART", msg)
                else:
                    await db.edit_config("RESTART", msg)
            config[var] = str(value)




