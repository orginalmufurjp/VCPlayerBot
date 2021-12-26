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
try:
   import os
   import heroku3
   from dotenv import load_dotenv
   from ast import literal_eval as is_enabled

except ModuleNotFoundError:
    import os
    import sys
    import subprocess
    file=os.path.abspath("requirements.txt")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', file, '--upgrade'])
    os.execl(sys.executable, sys.executable, *sys.argv)


class Config:
    #Telegram API Stuffs
    load_dotenv()  # load enviroment variables from .env file
    ADMIN = os.environ.get("ADMINS", '')
    SUDO = [int(admin) for admin in (ADMIN).split()] # Exclusive for heroku vars configuration.
    ADMINS = [int(admin) for admin in (ADMIN).split()] #group admins will be appended to this list.
    API_ID = int(os.environ.get("API_ID", ''))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")     
    SESSION = os.environ.get("SESSION_STRING", "")

    #Stream Chat and Log Group
    CHAT = int(os.environ.get("CHAT", ""))
    LOG_GROUP=os.environ.get("LOG_GROUP", "")

    #Stream 
    STREAM_URL=os.environ.get("STARTUP_STREAM", "https://www.youtube.com/watch?v=gpZnHXSbOoE")
   
    #Database
    DATABASE_URI=os.environ.get("DATABASE_URI", None)
    DATABASE_NAME=os.environ.get("DATABASE_NAME", "VCPlayerBot")


    #heroku
    API_KEY=os.environ.get("HEROKU_API_KEY", None)
    APP_NAME=os.environ.get("HEROKU_APP_NAME", None)


    #Optional Configuration
    SHUFFLE=is_enabled(os.environ.get("SHUFFLE", 'True'))
    ADMIN_ONLY=is_enabled(os.environ.get("ADMIN_ONLY", "False"))
    REPLY_MESSAGE=os.environ.get("REPLY_MESSAGE", False)
    EDIT_TITLE = os.environ.get("EDIT_TITLE", True)
    #others
    
    RECORDING_DUMP=os.environ.get("RECORDING_DUMP", False)
    RECORDING_TITLE=os.environ.get("RECORDING_TITLE", False)
    TIME_ZONE = os.environ.get("TIME_ZONE", "Asia/Kolkata")    
    IS_VIDEO=is_enabled(os.environ.get("IS_VIDEO", 'True'))
    IS_LOOP=is_enabled(os.environ.get("IS_LOOP", 'True'))
    DELAY=int(os.environ.get("DELAY", '120'))
    PORTRAIT=is_enabled(os.environ.get("PORTRAIT", 'False'))
    IS_VIDEO_RECORD=is_enabled(os.environ.get("IS_VIDEO_RECORD", 'True'))
    DEBUG=is_enabled(os.environ.get("DEBUG", 'False'))
    PTN=is_enabled(os.environ.get("PTN", "False"))

    #Quality vars
    E_BITRATE=os.environ.get("BITRATE", False)
    E_FPS=os.environ.get("FPS", False)
    CUSTOM_QUALITY=os.environ.get("QUALITY", "100")

    #Search filters for cplay
    FILTERS =  [filter.lower() for filter in (os.environ.get("FILTERS", "video document")).split(" ")]


    #Dont touch these, these are not for configuring player
    GET_FILE={}
    DATA={}
    STREAM_END={}
    SCHEDULED_STREAM={}
    DUR={}
    msg = {}

    SCHEDULE_LIST=[]
    playlist=[]
    CONFIG_LIST = ["ADMINS", "IS_VIDEO", "IS_LOOP", "REPLY_PM", "ADMIN_ONLY", "SHUFFLE", "EDIT_TITLE", "CHAT", 
    "SUDO", "REPLY_MESSAGE", "STREAM_URL", "DELAY", "LOG_GROUP", "SCHEDULED_STREAM", "SCHEDULE_LIST", 
    "IS_VIDEO_RECORD", "IS_RECORDING", "WAS_RECORDING", "RECORDING_TITLE", "PORTRAIT", "RECORDING_DUMP", "HAS_SCHEDULE", 
    "CUSTOM_QUALITY"]

    STARTUP_ERROR=None

    ADMIN_CACHE=False
    CALL_STATUS=False
    YPLAY=False
    YSTREAM=False
    CPLAY=False
    STREAM_SETUP=False
    LISTEN=False
    STREAM_LINK=False
    IS_RECORDING=False
    WAS_RECORDING=False
    PAUSE=False
    MUTED=False
    HAS_SCHEDULE=None
    IS_ACTIVE=None
    VOLUME=100
    CURRENT_CALL=None
    BOT_USERNAME=None
    USER_ID=None

    if LOG_GROUP:
        LOG_GROUP=int(LOG_GROUP)
    else:
        LOG_GROUP=None
    if not API_KEY or \
       not APP_NAME:
       HEROKU_APP=None
    else:
       HEROKU_APP=heroku3.from_key(API_KEY).apps()[APP_NAME]


    if EDIT_TITLE in ["NO", 'False']:
        EDIT_TITLE=False
        LOGGER.info("Title Editing turned off")
    if REPLY_MESSAGE:
        REPLY_MESSAGE=REPLY_MESSAGE
        REPLY_PM=True
        LOGGER.info("Reply Message Found, Enabled PM MSG")
    else:
        REPLY_MESSAGE=False
        REPLY_PM=False

    if E_BITRATE:
       try:
          BITRATE=int(E_BITRATE)
       except:
          LOGGER.error("Invalid bitrate specified.")
          E_BITRATE=False
          BITRATE=48000
       if not BITRATE >= 48000:
          BITRATE=48000
    else:
       BITRATE=48000
    
    if E_FPS:
       try:
          FPS=int(E_FPS)
       except:
          LOGGER.error("Invalid FPS specified")
          E_FPS=False
       if not FPS >= 30:
          FPS=30
    else:
       FPS=30
    try:
       CUSTOM_QUALITY=int(CUSTOM_QUALITY)
       if CUSTOM_QUALITY > 100:
          CUSTOM_QUALITY = 100
          LOGGER.warning("maximum quality allowed is 100, invalid quality specified. Quality set to 100")
       elif CUSTOM_QUALITY < 10:
          LOGGER.warning("Minimum Quality allowed is 10., Qulaity set to 10")
          CUSTOM_QUALITY = 10
       if  66.9  < CUSTOM_QUALITY < 100:
          if not E_BITRATE:
             BITRATE=48000
       elif 50 < CUSTOM_QUALITY < 66.9:
          if not E_BITRATE:
             BITRATE=36000
       else:
          if not E_BITRATE:
             BITRATE=24000
    except:
       if CUSTOM_QUALITY.lower() == 'high':
          CUSTOM_QUALITY=100
       elif CUSTOM_QUALITY.lower() == 'medium':
          CUSTOM_QUALITY=66.9
       elif CUSTOM_QUALITY.lower() == 'low':
          CUSTOM_QUALITY=50
       else:
          LOGGER.warning("Invalid QUALITY specified.Defaulting to High.")
          CUSTOM_QUALITY=100



    #help strings 
    PLAY_HELP="""
__شما می توانید با استفاده از هر یک از  دستورات زیر رسانه مورد نظر خود را پخش کنید.__

**1. پخش فیلم از یوتیوب**
دستور: **/play**
➊  روی لینک یوتیوب ریپلای کرده و دستور مربوطه را نوشته و ارسال نمایید. یا\n➋ لینک یوتیوب را در امتداد دستور، با یک فاصله ارسال کنید.یا\n➌ برای جست و جو خودکار ربات در یوتیوب دستور مربوطه را نوشته و با یک فاصله، عنوان رسانه درخواستی تایپ و ارسال شود..یا\n➍ به فایل رسانه تلگرامی ریپلای کنید..یا\n➎ از حالت اینلاین ربات استفاده کنید به طوری که  ابتدا یوزنیم  ربات را نوشته و سپس یک فاصله سپس  عنوان دلخواه خود را نوشته و رسانه مد نظر خود را انتخاب کنید.

**2. پخش از فایل تلگرام.**
دستور: **/play**
__به یک رسانه (ویدئو و اسناد یا فایل صوتی) رپلای کنید.__
نکته: __از دستور /fplay می توانید برای پخش آهنگ بلافاصله بدون انتظار برای پایان لیست پخش استفاده کنید.__

**3. پخش از لیست پخش**
دستور: **/yplay**
__با دستور /export لیست پخش دلخواه خود را  استخراج نمایید سپس دستور مربوطه روی فایل لیست پخش ریپلای کنید.__

**4. پخش زنده**
دستور: **/stream**
__یک لینک پخش زنده یوتبوب یا هر نشانی اینترنتی مستقیمی را برای پخش زنده ارسال کنید.__

**5. وارد کردن یک لیست پخش قدیمی.**
دستور: **/import**
__به فایل لیست پخش  استخراج شده قبلی ریپلای کنید.__

**6. پخش کانال**
دستور: **/cplay**
◂ برای پخش همه فایل‌ها از یک کانال خاص، از دستور\n<code>/cplay channel username or channel id</code>\nاستفاده کنید.\nبه طور پیش فرض فایل های ویدئویی و اسناد پخش می شوند. شما می‌توانید با استفاده از  دستور FILTERS نوع فایل را تعین کنید.\nبه عنوان مثال، برای پخش زنده صدا، ویدیو و سند از کانال از دستور \n<code>/env FILTERS=video document audio</code>\nاستفاده کنید.\nاگر فقط به پخش فایل صوتی نیاز دارید، می‌توانید از دستور\n<code>/env FILTERS=video audio</code>\n◂ برای تنظیم فایل ها از یک کانال به عنوان پخش پیش فرض، به طوری که فایل ها به طور خودکار به لیست پخش در هنگام راه اندازی ربات اضافه شوند. از\n<code>/env STARTUP_STREAM=channel username or channel id</code>
استفاده کنید.\n\n◂ توجه داشته باشید که برای کانال های عمومی باید از نام کاربری کانال به همراه '@' و برای کانال های خصوصی از شناسه عددی کانال استفاده کنید.\n\n◂ برای کانال های خصوصی، مطمئن شوید که هم ربات و هم حساب USER عضو کانال باشند.\n🅳🅸🅶🆁🅼
"""
    SETTINGS_HELP="""
**شما به راحتی می توانید پخش کننده را مطابق با نیاز خود با دکمه  شیشه ای سفارشی کنید.**

🔹دستور: **/settings**

🔹توضیحات:

**حالت پخش** -  __این به شما امکان می دهد پخش کننده را، به عنوان پخش کننده رسانه 24/7 یا فقط زمانی که آهنگ در لیست پخش وجود دارد اجرا کنید.
اگر غیرفعال باشد، وقتی لیست پخش خالی باشد، پخش کننده رسانه از ویس چت خارج می شود.
در غیر این صورت، اگر لیست پخش خالی باشد، STARTUP_STREAM (رسانه پیشفرض) پخش می شود.__

**پخش ویدئویی فعال** -  __این به شما امکان می دهد که آیا در رسانه مورد نظر فیلم همزمان با صوت پخش داده شود یا  فقط به صورت صوت پخش شود
در صورت غیرفعال بودن، فایل های ویدئویی به صورت صوتی پخش می شوند.__

**فقط مدیران** - __فعال کردن این بحش، کاربران غیر ادمین را از استفاده از دستور پخش محدود می کند.__

**تغییر عنوان ویس چت** - با فعال کردن این بخش ، عنوان چت ویدیویی ،صوتی شما به نام آهنگ‌های در حال پخش فعلی ویرایش می‌شود.__

**حالت بُر زدن** - __فعال کردن این بخش،  زمانی که یک لیست پخش را وارد می کنید یا از /yplay استفاده می کنید، ترتیب لیست پخش را به هم می زند.__

**پاسخ خودکار** - __انتخاب کنید که آیا به پیام‌های PM حساب کاربری در حال پخش رپیلای داده شود یا خیر. می‌توانید با استفاده از پیکربندی «REPLY MESSAGE» یک پیام پاسخ سفارشی تنظیم کنید.__\n🅳🅸🅶🆁🅼
"""
    SCHEDULER_HELP="""
دیجی گرام به شما امکان می دهد یک استریم را برنامه ریزی کنید.
این بدان معنی است که می توانید یک استریم را برای تاریخ آینده برنامه ریزی کنید و در تاریخ برنامه ریزی شده، استریم به طور خودکار پخش می شود.
در حال حاضر شما می توانید یک استریم را حتی برای یک سال برنامه ریزی کنید!!.__

دستور: **/schedule**

__با دستور  به یک فایل یا ویدیوی یوتیوب یا حتی یک پیام متنی ریپلای کنید.
رسانه ریپلای زده شده یا ویدیوی یوتیوب برنامه ریزی می شود و در تاریخ برنامه ریزی شده پخش می شود.
زمان زمان‌بندی به‌طور پیش‌فرض در IST است و می‌توانید منطقه زمانی را با استفاده از پیکربندی «TIME_ZONE» تغییر دهید.__

دستور: **/slist**
__استریم های برنامه ریزی شده فعلی خود را مشاهده کنید.__

دستور: **/cancel**
__میتوانید یک برنامه را با شناسه زمانبدی شده را لغو کنید، شناسه برنامه را با استفاده از دستور /slist پیدا کنید__

دستور: **/cancelall**
__لغو همه پخش های برنامه ریزی شده__\n🅳🅸🅶🆁🅼
"""
    RECORDER_HELP="""
__با DigiGram24 می توانید به راحتی تمام چت های تصویری خود را ضبط کنید.
تلگرام به طور پیش فرض به شما امکان ضبط حداکثر 4 ساعت را می دهد.__

دستور: **/record**

توضیحات:
1. ضبط فیلم: __اگر فعال باشد هم ویدیو و هم صدای استریم ضبط می شود، در غیر این صورت فقط صدا ضبط می شود.__

2. اندازه ویدیو: __ابعاد عمودی یا افقی برای ضبط خود انتخاب کنید__

3. عنوان ضبط سفارشی: __یک عنوان ضبط سفارشی برای ضبط های خود تنظیم کنید. برای پیکربندی از یک دستور /rtitle استفاده کنید.
برای خاموش کردن عنوان سفارشی، از `/rtitle False`__ استفاده کنید

4. مدیریت فایل های ضبط: __می‌توانید ارسال همه ضبط‌های خود را به یک کانال ارسال کنید، این کار مفید خواهد بود زیرا در غیر این صورت ضبط‌ها به پیام‌های ذخیره‌شده اکانت پخش ارسال می‌شوند.
راه اندازی با استفاده از پیکربندی «RECORDING_DUMP».__
⚠️ اگر ضبط را با یک اکانت شروع کردید، مطمئن شوید برای توقف از همان اکانت استفاده کنید.\n🅳🅸🅶🆁🅼
"""

    CONTROL_HELP="""
__دیجی گرام به شما این امکان را می دهد تا استریم های خود را به راحتی کنترل کنید__
1. رد کردن رسانه.
دستور: **/skip**
__برای رد کردن آهنگ تک تک فقط خود دستور ارسال کننید: برای ردن کردن همزمان چند رسانه عددی بزرگتر از 2 را  جلو دستور با یک فاصله بنویسید و ارسال کنید.__

2. متوقف کردن پخش.
دستور: **/pause**

3. از سر گیری پخش.
دستور: **/resume**

4. تغییر میزان صدا.
دستور: **/volume**
__برای تنظیم صدا عددی بین 1 تا 200  جلو دستور با یک فاصله نوشته و ارسال کنید.__

5. خروج از حالت پخش.
دستور: **/leave**

6. لیست پخش را به هم بزنید.
دستور: **/shuffle**

7. صف لیست پخش فعلی را پاک کنید.
دستور: **/clearplaylist**

8. پخش ویویو را به جلو بکشید.
دستور: **/seek**
__شما می توانید چند ثانیه را برای رد شدن بگذرانید. مثال: /seek 10 تا رد شدن از 10 sec. /seek -10 تا عقب بردن 10 ثانیه.__

9. بی صدا کردن پخش.
دستور: **/vcmute**

10. حذف بیصدا پخش.
دستور : **/vcunmute**

11. نمایش لیست پخش.
دستور: **/playlist** 
__از /player برای نمایش با دکمه های کنترل استفاده کنید\n🅳🅸🅶🆁🅼
"""

    ADMIN_HELP="""
__ربات پخش کننده این اجازه می دهد تا ادمین ها را کنترل کنید، یعنی می توانید ادمین ها را اضافه کنید و به راحتی آنها را حذف کنید.__

دستور: **/vcpromote**
__شما می توانید یک مدیر را با نام کاربری یا شناسه کاربری خود یا با ریپلای کردن به آن پیام کاربران به ربات معرفی کنید.__

دستور: **/vcdemote**
__حذف یک ادمین از لیست مدیریت__

دستور: **/refresh**
__لیست مدیریت چت را تازه کنید__\n🅳🅸🅶🆁🅼
"""

    MISC_HELP="""
دستور: **/export**
__ربات پخش کننده به شما امکان می دهد لیست پخش فعلی خود را برای استفاده، در آینده استخراج کنید.__
__یک فایل json برای شما ارسال می شود و می توان از آن در کنار دستور /import استفاده کرد.__

دستور: **/update**
__بروزرسانی ربات__\n🅳🅸🅶🆁🅼

"""
    ENV_HELP="""
** متغیرهای قابل تنظیم را می توانید با استفاده از دستور /env تنظیم کنید**\n🅳🅸🅶🆁🅼

"""
