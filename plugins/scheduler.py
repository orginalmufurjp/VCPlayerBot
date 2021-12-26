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
import re
import calendar
from datetime import datetime
from contextlib import suppress
import pytz
from config import Config
from PTN import parse
from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL

from pyrogram import(
    Client, 
    filters
    )
from pyrogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)
from utils import (
    delete_messages,
    is_admin,
    sync_to_db,
    is_audio,
    chat_filter,
    scheduler,
    is_ytdl_supported
)

from pyrogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)
from pyrogram.errors import (
    MessageIdInvalid, 
    MessageNotModified
)


IST = pytz.timezone(Config.TIME_ZONE)

admin_filter=filters.create(is_admin) 



@Client.on_message(filters.command(["schedule", f"schedule@{Config.BOT_USERNAME}"]) & chat_filter & admin_filter)
async def schedule_vc(bot, message):
    with suppress(MessageIdInvalid, MessageNotModified):
        type=""
        yturl=""
        ysearch=""
        msg = await message.reply_text("⚡️ **درحال بررسی ورودی دریافتی..**")
        if message.reply_to_message and message.reply_to_message.video:
            await msg.edit("⚡️ **بررسی رسانه تلگرامی...**")
            type='video'
            m_video = message.reply_to_message.video       
        elif message.reply_to_message and message.reply_to_message.document:
            await msg.edit("⚡️ **بررسی رسانه تلگرامی...**")
            m_video = message.reply_to_message.document
            type='video'
            if not "video" in m_video.mime_type:
                return await msg.edit("فایل داده شده نامعتبر است")
        elif message.reply_to_message and message.reply_to_message.audio:
            #if not Config.IS_VIDEO:
                #return await message.reply("Play from audio file is available only if Video Mode if turned off.\nUse /settings to configure ypur player.")
            await msg.edit("⚡️ **بررسی رسانه تلگرامی...**")
            type='audio'
            m_video = message.reply_to_message.audio       
        else:
            if message.reply_to_message and message.reply_to_message.text:
                query=message.reply_to_message.text
            elif " " in message.text:
                text = message.text.split(" ", 1)
                query = text[1]
            else:
                await msg.edit("• هیچ رسانه ای برای زمان بندی ارسال نشد.\n◂ لطفا بعد از نوشتن دستور یک فاصله گذاشته، سپس:\n➊ لینک یوتیوب یا لینک مستقیم رسانه نوشته و ارسال نمایید. یا\n➋ به لینک یوتیوب یا لینک مستقیم ریپلای کنید. یا\n➌ به فایل رسانه تلگرامی ریپلای کنید.\n✦")
                await delete_messages([message, msg])
                return
            regex = r"^(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?"
            match = re.match(regex,query)
            if match:
                type="youtube"
                yturl=query
            elif query.startswith("http"):
                has_audio_ = await is_audio(query)
                if not has_audio_:
                    if is_ytdl_supported(query):
                        type="ytdl_s"
                        url=query
                    else:
                        await msg.edit("این یک لینک نامعتبر است، یک لینک مستقیم یا یک لینک یوتیوب ارسال نمایید.")
                        await delete_messages([message, msg])
                        return
                type="direct"
                url=query
            else:
                type="query"
                ysearch=query
        if not message.from_user is None:
            user=f"[{message.from_user.first_name}](tg://user?id={message.from_user.id}) - (برنامه ریزی شده است)"
            user_id = message.from_user.id
        else:
            user="Anonymous - (Scheduled)"
            user_id = "anonymous_admin"
        now = datetime.now()
        nyav = now.strftime("%d-%m-%Y-%H:%M:%S")
        if type in ["video", "audio"]:
            if type == "audio":
                if m_video.title is None:
                    if m_video.file_name is None:
                        title_ = "Music"
                    else:
                        title_ = m_video.file_name
                else:
                    title_ = m_video.title
                if m_video.performer is not None:
                    title = f"{m_video.performer} - {title_}"
                else:
                    title=title_
                unique = f"{nyav}_{m_video.file_size}_audio"
            else:
                title=m_video.file_name
                unique = f"{nyav}_{m_video.file_size}_video"
                if Config.PTN:
                    ny = parse(title)
                    title_ = ny.get("title")
                    if title_:
                        title = title_
            if title is None:
                title = 'Music'
            data={'1':title, '2':m_video.file_id, '3':"telegram", '4':user, '5':unique}
            sid=f"{message.chat.id}_{msg.message_id}"
            Config.SCHEDULED_STREAM[sid] = data
            await sync_to_db()
        elif type in ["youtube", "query", "ytdl_s"]:
            if type=="youtube":
                await msg.edit("⚡️ **در حال دریافت ویدیو از یوتیوب...**")
                url=yturl
            elif type=="query":
                try:
                    await msg.edit("⚡️ **در حال دریافت ویدیو از یوتیوب...**")
                    ytquery=ysearch
                    results = YoutubeSearch(ytquery, max_results=1).to_dict()
                    url = f"https://youtube.com{results[0]['url_suffix']}"
                    title = results[0]["title"][:40]
                except Exception as e:
                    await msg.edit(
                        "Song not found.\nTry inline mode.."
                    )
                    LOGGER.error(str(e), exc_info=True)
                    await delete_messages([message, msg])
                    return
            elif type == "ytdl_s":
                url=url
            else:
                return
            ydl_opts = {
                "quite": True,
                "geo-bypass": True,
                "nocheckcertificate": True
            }
            ydl = YoutubeDL(ydl_opts)
            try:
                info = ydl.extract_info(url, False)
            except Exception as e:
                LOGGER.error(e, exc_info=True)
                await msg.edit(
                    f"YouTube Download Error ❌\nError:- {e}"
                    )
                LOGGER.error(str(e))
                await delete_messages([message, msg])
                return
            if type == "ytdl_s":
                title = "Music"
                try:
                    title=info['title']
                except:
                    pass
            else:
                title = info["title"]
            data={'1':title, '2':url, '3':"youtube", '4':user, '5':f"{nyav}_{user_id}"}
            sid=f"{message.chat.id}_{msg.message_id}"
            Config.SCHEDULED_STREAM[sid] = data
            await sync_to_db()
        elif type == "direct":
            data={"1":"Music", '2':url, '3':"url", '4':user, '5':f"{nyav}_{user_id}"}
            sid=f"{message.chat.id}_{msg.message_id}"
            Config.SCHEDULED_STREAM[sid] = data
            await sync_to_db()
        if message.chat.type!='private' and message.from_user is None:
            await msg.edit(
                text="شما نمی توانید از اینجا برنامه ریزی کنید زیرا شما یک مدیر ناشناس هستید. برای برنامه ریزی از طریق چت خصوصی، روی دکمه زمان بندی کلیک کنید.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(f"Schedule", url=f"https://telegram.dog/{Config.BOT_USERNAME}?start=sch_{sid}"),
                        ]
                    ]
                ),)
            await delete_messages([message, msg])
            return
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




@Client.on_message(filters.command(["slist", f"slist@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def list_schedule(bot, message):
    k=await message.reply("Checking schedules...")
    if not Config.SCHEDULE_LIST:
        await k.edit("◂ برنامه پخش زمان بندی شده ای وجود ندارد.")
        await delete_messages([k, message])
        return
    text="زمانبندی های فعلی:\n\n"
    s=Config.SCHEDULE_LIST
    f=1
    for sch in s:
        details=Config.SCHEDULED_STREAM.get(sch['job_id'])
        if not details['3']=="telegram":
            text+=f"<b>{f}.</b> عنوان: [{details['1']}]({details['2']}) توسط {details['4']}\n"
        else:
            text+=f"<b>{f}.</b> عنوان: {details['1']} توسط {details['4']}\n"
        date = sch['date']
        f+=1
        date_=((pytz.utc.localize(date, is_dst=None).astimezone(IST)).replace(tzinfo=None)).strftime("%b %d %Y, %I:%M %p")
        text+=f"شناسه زمانبندی : <code>{sch['job_id']}</code>\nزمان پخش برنامه: : <code>{date_}</code>\n✦"

    await k.edit(text, disable_web_page_preview=True)
    await delete_messages([message])


@Client.on_message(filters.command(["cancel", f"cancel@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def delete_sch(bot, message):
    with suppress(MessageIdInvalid, MessageNotModified):
        m = await message.reply("◂درحال یافتن پخش های برنامه ریزی شده...")
        if " " in message.text:
            cmd, job_id = message.text.split(" ", 1)
        else:
            buttons = [
                [
                    InlineKeyboardButton('لغو کردن همه', callback_data='schcancel'),
                    InlineKeyboardButton('خیر', callback_data='schclose'),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await m.edit("هیچ شناسه زمان بندی شده ای مشخص نشده است!! آیا می خواهید همه پخش های زمانبندی شده را لغو کنید؟\nشما می توانید با استفاده از دستور /slist شناسه زمانبندی شده، را پیدا کنید.", reply_markup=reply_markup)
            await delete_messages([message])
            return
        data=Config.SCHEDULED_STREAM.get(job_id)
        if not data:
            await m.edit("◂ شما یک شناسه زمانبندی نا معتبر، ارسال کرده اید، دوباره بررسی و شناسه صحیح را ارسال کنید.")
            await delete_messages([message, m])
            return
        del Config.SCHEDULED_STREAM[job_id]
        k=scheduler.get_job(job_id, jobstore=None)
        if k:
            scheduler.remove_job(job_id, jobstore=None)
        old=list(filter(lambda k: k['job_id'] == job_id, Config.SCHEDULE_LIST))
        if old:
            for old_ in old:
                Config.SCHEDULE_LIST.remove(old_)
        await sync_to_db()
        await m.edit(f"◂برنامه {data['1']} با موفقیت از لیست برنامه‌ریزی‌ شده حذف شد.")
        await delete_messages([message, m])
        
@Client.on_message(filters.command(["cancelall", f"cancelall@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def delete_all_sch(bot, message):
    buttons = [
        [
            InlineKeyboardButton('لغو کردن همه', callback_data='schcancel'),
            InlineKeyboardButton('خیر', callback_data='schclose'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply("آیا می‌خواهید همه پخش‌های زمانبندی شده را لغو کنید؟ㅤㅤㅤㅤ ㅤ", reply_markup=reply_markup)
    await delete_messages([message])


