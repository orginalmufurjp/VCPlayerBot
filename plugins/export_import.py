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
import json
import os
from pyrogram.types import Message
from contextlib import suppress
from config import Config
from utils import (
    get_buttons, 
    is_admin, 
    get_playlist_str, 
    shuffle_playlist, 
    import_play_list, 
    delete_messages,
    chat_filter
)
from pyrogram import (
    Client, 
    filters
)
from pyrogram.errors import (
    MessageNotModified, 
    MessageIdInvalid
)


admin_filter=filters.create(is_admin)   


@Client.on_message(filters.command(["export", f"export@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def export_play_list(client, message: Message):
    if not Config.playlist:
        k=await message.reply_text("» لیست پخش خالی است.")
        await delete_messages([message, k])
        return
    file=f"{message.chat.id}_{message.message_id}.json"
    with open(file, 'w+') as outfile:
        json.dump(Config.playlist, outfile, indent=4)
    await client.send_document(chat_id=message.chat.id, document=file, file_name="PlayList.json", caption=f"فایل لیست پخش\n\nتعداد رسانه های موجود: <code>{len(Config.playlist)}</code>\n\nعضویت [DigiGram24](https://t.me/DigiGram24)\n🅳🅸🅶🆁🅼")
    try:
        os.remove(file)
    except:
        pass
    await delete_messages([message])

@Client.on_message(filters.command(["import", f"import@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def import_playlist(client, m: Message):
    with suppress(MessageIdInvalid, MessageNotModified):
        if m.reply_to_message is not None and m.reply_to_message.document:
            if m.reply_to_message.document.file_name != "PlayList.json":
                k=await m.reply("» فایلِ لیست پخش ریپلای شده نامعتبر است. لیست پخش فعلی خود را با استفاده از دستور /export استخراج کنید.")
                await delete_messages([m, k])
                return
            myplaylist=await m.reply_to_message.download()
            status=await m.reply(" » درحال دریافت جزئیات از لیست پخش...")
            n=await import_play_list(myplaylist)
            if not n:
                await status.edit("هنگام وارد کردن لیست پخش، خطاهایی رخ داد.")
                await delete_messages([m, status])
                return
            if Config.SHUFFLE:
                await shuffle_playlist()
            pl=await get_playlist_str()
            if m.chat.type == "private":
                await status.edit(pl, disable_web_page_preview=True, reply_markup=await get_buttons())        
            elif not Config.LOG_GROUP and m.chat.type == "supergroup":
                if Config.msg.get('playlist'):
                    await Config.msg['playlist'].delete()
                Config.msg['playlist'] = await status.edit(pl, disable_web_page_preview=True, reply_markup=await get_buttons())
                await delete_messages([m])
            else:
                await delete_messages([m, status])
        else:
            k = await m.reply("» خطا - روی فایلِ لیست پخش، ریپلای کرده و دستور /import را وارد کنید.")
            await delete_messages([m, k])
