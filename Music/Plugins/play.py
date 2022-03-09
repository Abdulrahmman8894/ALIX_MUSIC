import os
import time
from os import path
import random
import asyncio
import shutil
from pytube import YouTube
from yt_dlp import YoutubeDL
from Music import converter
import yt_dlp
import shutil
import psutil
from typing import Callable
from pyrogram import Client
from pyrogram.types import Message, Voice
from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputAudioStream, InputStream
from sys import version as pyver
from Music import (
    dbb,
    app,
    BOT_USERNAME,
    BOT_ID,
    BOT_NAME,
    ASSID,
    ASSNAME,
    ASSUSERNAME,
    ASSMENTION,
)
from Music.MusicUtilities.tgcallsrun import (
    music,
    convert,
    download,
    clear,
    get,
    is_empty,
    put,
    task_done,
    ASS_ACC,
)
from Music.MusicUtilities.database.queue import (
    get_active_chats,
    is_active_chat,
    add_active_chat,
    remove_active_chat,
    music_on,
    is_music_playing,
    music_off,
)
from Music.MusicUtilities.database.onoff import (
    is_on_off,
    add_on,
    add_off,
)
from Music.MusicUtilities.database.chats import (
    get_served_chats,
    is_served_chat,
    add_served_chat,
    get_served_chats,
)
from Music.MusicUtilities.helpers.inline import (
    play_keyboard,
    search_markup,
    play_markup,
    playlist_markup,
    audio_markup,
    play_list_keyboard,
)
from Music.MusicUtilities.database.blacklistchat import (
    blacklisted_chats,
    blacklist_chat,
    whitelist_chat,
)
from Music.MusicUtilities.database.gbanned import (
    get_gbans_count,
    is_gbanned_user,
    add_gban_user,
    add_gban_user,
)
from Music.MusicUtilities.database.theme import (
    _get_theme,
    get_theme,
    save_theme,
)
from Music.MusicUtilities.database.assistant import (
    _get_assistant,
    get_assistant,
    save_assistant,
)
from Music.config import DURATION_LIMIT
from Music.MusicUtilities.helpers.decorators import errors
from Music.MusicUtilities.helpers.filters import command
from Music.MusicUtilities.helpers.gets import (
    get_url,
    themes,
    random_assistant,
    ass_det,
)
from Music.MusicUtilities.helpers.logger import LOG_CHAT
from Music.MusicUtilities.helpers.thumbnails import gen_thumb
from Music.MusicUtilities.helpers.chattitle import CHAT_TITLE
from Music.MusicUtilities.helpers.ytdl import ytdl_opts 
from Music.MusicUtilities.helpers.inline import (
    play_keyboard,
    search_markup2,
    search_markup,
)
from pyrogram import filters
from typing import Union
import subprocess
from asyncio import QueueEmpty
import shutil
import os
from youtubesearchpython import VideosSearch
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import Message, Audio, Voice
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

flex = {}
chat_watcher_group = 3


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))



@Client.on_message(command(["play", "شغل" ,"بارلو" ,"تشغيل", f"play@{BOT_USERNAME}", "p"]))
async def play(_, message: Message):
    chat_id = message.chat.id
    if message.sender_chat:
        return await message.reply_text(
            """
اسف انت لست ادمن!
عود الي مالك الجروب لتصبح ادمن وحاول مججددا.
"""
        )
    user_id = message.from_user.id
    chat_title = message.chat.title
    username = message.from_user.first_name
    checking = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    if await is_on_off(1):
        LOG_ID = "-100156899495"
        if int(chat_id) != int(LOG_ID):
            return await message.reply_text(
                f"الـبوت تـحـت الـتحـديث نـتـاسـف للازعاج!"
            )
        return await message.reply_text(
            f"البوت تحت الصيانة.  نأسف للإزعاج!"
        )
    a = await app.get_chat_member(message.chat.id, BOT_ID)
    if a.status != "administrator":
        await message.reply_text(
            """
أحتاج أن أكون مشرفًا مع بعض الأذونات:

- **صلاحيه  إدارة الدردشة الصوتية:** لإدارة الدردشة الصوتية
- **صلاحية حذف الرسايل:** لحذف الموسيقى غير المرغوب فيها التي تم البحث عنها
- **صلاحية داعوة المستخدمين عبر الرابط**: لدعوه الحساب المساعد
- **صـلاحية حظر المستخدمين**: لحماية الموسيقى من البريد العشوائي.
"""
        )
        return
    if not a.can_manage_voice_chats:
        await message.reply_text(
            "اسف ليس لدي الصلاحيات المطلوبة لتشغيل الموسقي💗 ."
            + "\n❌ إدارة المحادثات الصوتية"
        )
        return
    if not a.can_delete_messages:
        await message.reply_text(
            "اسف  ليس لدي الصلاحيات المطلوبة لتشغيل الموسقي"
            + "\n❌ حذف الرسايل"
        )
        return
    if not a.can_invite_users:
        await message.reply_text(
            "بحاجهة الي صلاحيهة"
            + "\n❌ داعوه المستخدمين عبر الرابط"
        )
        return
    if not a.can_restrict_members:
        await message.reply_text(
            "بحاجة الي صلاحية ."
            + "\n❌ حظر مستخدمين"
        )
        return
    try:
        b = await app.get_chat_member(message.chat.id, ASSID)
        if b.status == "kicked":
            await message.reply_text(
                f"""
{ASSNAME}(@{ASSUSERNAME}) محظور في الدردشة الخاصة بك **{chat_title}**

قم بي الغاء الحظر للاستخدام البوت بي نجاح🎶️
"""
            )
            return
    except UserNotParticipant:
        if message.chat.username:
            try:
                await ASS_ACC.join_chat(f"{message.chat.username}")
                await message.reply(
                    f"{ASSNAME} تم انضمام المساعد بناج🎧 ،،",
                )
                await remove_active_chat(chat_id)
            except Exception as e:
                await message.reply_text(
                    f"""
**فشل الانضمام إلى المساعد**
**السبب**:{e}
"""
                )
                return
        else:
            try:
                invite_link = await message.chat.export_invite_link()
                if "+" in invite_link:
                    kontol = (invite_link.replace("+", "")).split("t.me/")[1]
                    link_bokep = f"https://t.me/joinchat/{kontol}"
                await ASS_ACC.join_chat(link_bokep)
                await message.reply(f"{ASSNAME} Berhasil Bergabung",)
                await remove_active_chat(chat_id)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await message.reply_text(
                    f"""
**فشل الانضمام إلى المساعد**
**السبب**:{e}
"""
                )
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    url = get_url(message)
    fucksemx = 0
    if audio:
        fucksemx = 1
        what = "Audio Searched"
        await LOG_CHAT(message, what)
        mystic = await message.reply_text(
            f"*جـاري معالجه الصوت انتظر🎶️ {username}**"
        )
        if audio.file_size > 157286400:
            await mystic.edit_text("Ukuran File Audio Harus Kurang dari 150 mb")
            return
        duration = round(audio.duration / 60)
        if duration > DURATION_LIMIT:
            return await mystic.edit_text(
                f"""
**خطا في المده**

**المدة المسموح بها: **{DURATION_LIMIT}
**المدة المقبولة:** {duration}
"""
            )
        file_name = (
            audio.file_unique_id
            + "."
            + (
                (audio.file_name.split(".")[-1])
                if (not isinstance(audio, Voice))
                else "ogg"
            )
        )
        file_name = path.join(path.realpath("downloads"), file_name)
        file = await convert(
            (await message.reply_to_message.download(file_name))
            if (not path.isfile(file_name))
            else file_name,
        )
        title = "Audio Yang Dipilih Dari Telegram"
        link = "https://t.me/bar_lo0o"
        thumb = "cache/Audio.png"
        videoid = "smex1"
    elif url:
        what = "URL Searched"
        await LOG_CHAT(message, what)
        query = message.text.split(None, 1)[1]
        mystic = await message.reply_text("Processing Url")
        ydl_opts = {"format": "bestaudio/best"}
        try:
            results = VideosSearch(query, limit=1)
            for result in results.result()["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"]
                link = result["link"]
                (result["id"])
                videoid = result["id"]
        except Exception as e:
            return await mystic.edit_text(
                f"Lagu Tidak Ditemukan.\n**Kemungkinan Alasan:** {e}"
            )
        smex = int(time_to_seconds(duration))
        if smex > DURATION_LIMIT:
            return await mystic.edit_text(
                f"""
**خطا في المدة**

**المدة المسموح بها:** {DURATION_LIMIT}
**المدة المقبولة:** {duration}
"""
            )
        if duration == "None":
            return await mystic.edit_text("Maaf! Video langsung tidak Didukung")
        if views == "None":
            return await mystic.edit_text("Maaf! Video langsung tidak Didukung")
        semxbabes = f"Downloading {title[:50]}"
        await mystic.edit(semxbabes)
        theme = random.choice(themes)
        ctitle = message.chat.title
        ctitle = await CHAT_TITLE(ctitle)
        userid = message.from_user.id
        thumb = await gen_thumb(thumbnail, title, userid, theme, ctitle)

        def my_hook(d):
            if d["status"] == "downloading":
                percentage = d["_percent_str"]
                per = (str(percentage)).replace(".", "", 1).replace("%", "", 1)
                per = int(per)
                eta = d["eta"]
                speed = d["_speed_str"]
                size = d["_total_bytes_str"]
                bytesx = d["total_bytes"]
                if str(bytesx) in flex:
                    pass
                else:
                    flex[str(bytesx)] = 1
                if flex[str(bytesx)] == 1:
                    flex[str(bytesx)] += 1
                    try:
                        if eta > 2:
                            mystic.edit(
                                f"Downloading {title[:50]}\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                            )
                    except Exception:
                        pass
                if per > 250:
                    if flex[str(bytesx)] == 2:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            mystic.edit(
                                f"Downloading {title[:50]}..\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                            )
                        print(
                            f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                        )
                if per > 500:
                    if flex[str(bytesx)] == 3:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            mystic.edit(
                                f"Downloading {title[:50]}...\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                            )
                        print(
                            f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                        )
                if per > 800:
                    if flex[str(bytesx)] == 4:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            mystic.edit(
                                f"Downloading {title[:50]}....\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                            )
                        print(
                            f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                        )
            if d["status"] == "finished":
                try:
                    taken = d["_elapsed_str"]
                except Exception:
                    taken = "00:00"
                size = d["_total_bytes_str"]
                mystic.edit(
                    f"**Downloaded {title[:50]}.....**\n\n**FileSize:** {size}\n**Time Taken:** {taken} sec\n\n**Converting File**[__FFmpeg processing__]"
                )
                print(f"[{videoid}] Downloaded| Elapsed: {taken} seconds")

        loop = asyncio.get_event_loop()
        x = await loop.run_in_executor(None, download, link, my_hook)
        file = await convert(x)
    else:
        if len(message.command) < 2:
            what = "Command"
            await LOG_CHAT(message, what)
            message.from_user.first_name
            hmo = await message.reply_text(
                """
<b>لم يتم العثور علي اسم الاغنية قم بكتابه الاسم الصحيحه

وقم بكتابه جنمبي امر
`/play 🎧`
""",
            )
            return
        what = "Query Given"
        await LOG_CHAT(message, what)
        query = message.text.split(None, 1)[1]
        mystic = await message.reply_text("**جاري العثور علي الاغنيه انتظر**")
        try:
            a = VideosSearch(query, limit=5)
            result = (a.result()).get("result")
            title1 = result[0]["title"]
            duration1 = result[0]["duration"]
            title2 = result[1]["title"]
            duration2 = result[1]["duration"]
            title3 = result[2]["title"]
            duration3 = result[2]["duration"]
            title4 = result[3]["title"]
            duration4 = result[3]["duration"]
            title5 = result[4]["title"]
            duration5 = result[4]["duration"]
            ID1 = result[0]["id"]
            ID2 = result[1]["id"]
            ID3 = result[2]["id"]
            ID4 = result[3]["id"]
            ID5 = result[4]["id"]
        except Exception as e:
            return await mystic.edit_text(
                f"لم يتم العثور علي الاغنيه.\n**سبب محتمل:** {e}"
            )
        thumb ="cache/IMG_20211105_143948_192.jpg"
        buttons = search_markup(ID1, ID2, ID3, ID4, ID5, duration1, duration2, duration3, duration4, duration5, user_id, query)
        await mystic.edit( 
            f"**الـرجـاء اخـتـيـار الـمـوسـيـقـي الـمـطـلـوبة مـن الاسفل • 🎶👇 **\n\n¹ <b>{title1[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID1})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__\n\n² <b>{title2[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID2})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__\n\n³ <b>{title3[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID3})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__\n\n⁴ <b>{title4[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID4})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__\n\n⁵ <b>{title5[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID5})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__",    
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )  
        return
    if await is_active_chat(chat_id):
        position = await put(chat_id, file=file)
        _chat_ = (str(file)).replace("_", "", 1).replace("/", "", 1).replace(".", "", 1)
        cpl = f"downloads/{_chat_}final.png"
        shutil.copyfile(thumb, cpl)
        f20 = open(f"search/{_chat_}title.txt", "w")
        f20.write(f"{title}")
        f20.close()
        f111 = open(f"search/{_chat_}duration.txt", "w")
        f111.write(f"{duration}")
        f111.close()
        f27 = open(f"search/{_chat_}username.txt", "w")
        f27.write(f"{checking}")
        f27.close()
        if fucksemx != 1:
            f28 = open(f"search/{_chat_}videoid.txt", "w")
            f28.write(f"{videoid}")
            f28.close()
            buttons = play_markup(videoid, user_id)
        else:
            f28 = open(f"search/{_chat_}videoid.txt", "w")
            f28.write(f"{videoid}")
            f28.close()
            buttons = audio_markup(videoid, user_id)
        checking = (
            f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
        )
        await message.reply_photo(
            photo=thumb,
            caption=f"""
<b>🎧 Trek ditambahkan ke antrian</b>

<b>🖋️ Nama Kontol: [{title[:25]}]({link})</b>
<b>🕓 Durasi Kontol:</b> {duration} \n
<b>🎧 Atas permintaan Si kontol: </b>{checking}

<b>#️⃣ Posisi antrian Kontol</b> {position}
""",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return await mystic.delete()
    else:
        await music_on(chat_id)
        await add_active_chat(chat_id)
        await music.pytgcalls.join_group_call(
            chat_id,
            InputStream(
                InputAudioStream(
                    file,
                ),
            ),
            stream_type=StreamType().local_stream,
        )
        _chat_ = (str(file)).replace("_", "", 1).replace("/", "", 1).replace(".", "", 1)
        checking = (
            f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
        )
        if fucksemx != 1:
            f28 = open(f"search/{_chat_}videoid.txt", "w")
            f28.write(f"{videoid}")
            f28.close()
            buttons = play_markup(videoid, user_id)
        else:
            f28 = open(f"search/{_chat_}videoid.txt", "w")
            f28.write(f"{videoid}")
            f28.close()
            buttons = audio_markup(videoid, user_id)
        await message.reply_photo(
            photo=thumb,
            reply_markup=InlineKeyboardMarkup(buttons),
            caption=f"""
<b>🖋 اسم الاغنيه:</b> [{title[:25]}]({link})
<b>🕓 المدة:</b> {duration}
<b>🎧 مطلوبه من:</b> {checking}
""",
        )
        return await mystic.delete()


@Client.on_callback_query(filters.regex(pattern=r"Music"))
async def startyuplay(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    CallbackQuery.message.chat.title
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id
    try:
        id, duration, user_id = callback_request.split("|")
    except Exception as e:
        return await CallbackQuery.message.edit(
            f"Error Occured\n**Possible reason could be**:{e}"
        )
    if duration == "None":
        return await CallbackQuery.message.reply_text(
            f"Sorry!, Live Videos are not supported"
        )
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "This is not for you! Search You Own Song nigga", show_alert=True
        )
    await CallbackQuery.message.delete()
    checking = f"[{CallbackQuery.from_user.first_name}](tg://user?id={userid})"
    url = f"https://www.youtube.com/watch?v={id}"
    videoid = id
    smex = int(time_to_seconds(duration))
    if smex > DURATION_LIMIT:
        await CallbackQuery.message.reply_text(
            f"""
**خطا في المده**

**المدة المسموح بها: {DURATION_LIMIT}**
**المدة المقبولة:** {duration}
"""
        )
        return
    try:
        with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
            x = ytdl.extract_info(url, download=False)
    except Exception as e:
        return await CallbackQuery.message.reply_text(
            f"Gagal mengunduh video ini..\n\n**Alasan**: {e}"
        )
    title = x["title"]
    mystic = await CallbackQuery.message.reply_text(f"Downloading {title[:50]}")
    thumbnail = x["thumbnail"]
    (x["id"])
    videoid = x["id"]

    def my_hook(d):
        if d["status"] == "downloading":
            percentage = d["_percent_str"]
            per = (str(percentage)).replace(".", "", 1).replace("%", "", 1)
            per = int(per)
            eta = d["eta"]
            speed = d["_speed_str"]
            size = d["_total_bytes_str"]
            bytesx = d["total_bytes"]
            if str(bytesx) in flex:
                pass
            else:
                flex[str(bytesx)] = 1
            if flex[str(bytesx)] == 1:
                flex[str(bytesx)] += 1
                try:
                    if eta > 2:
                        mystic.edit(
                            f"Downloading {title[:50]}\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                        )
                except Exception:
                    pass
            if per > 250:
                if flex[str(bytesx)] == 2:
                    flex[str(bytesx)] += 1
                    if eta > 2:
                        mystic.edit(
                            f"Downloading {title[:50]}..\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                        )
                    print(
                        f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                    )
            if per > 500:
                if flex[str(bytesx)] == 3:
                    flex[str(bytesx)] += 1
                    if eta > 2:
                        mystic.edit(
                            f"Downloading {title[:50]}...\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                        )
                    print(
                        f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                    )
            if per > 800:
                if flex[str(bytesx)] == 4:
                    flex[str(bytesx)] += 1
                    if eta > 2:
                        mystic.edit(
                            f"Downloading {title[:50]}....\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                        )
                    print(
                        f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                    )
        if d["status"] == "finished":
            try:
                taken = d["_elapsed_str"]
            except Exception:
                taken = "00:00"
            size = d["_total_bytes_str"]
            mystic.edit(
                f"**Downloaded {title[:50]}.....**\n\n**FileSize:** {size}\n**Time Taken:** {taken} sec\n\n**Converting File**[__FFmpeg processing__]"
            )
            print(f"[{videoid}] Downloaded| Elapsed: {taken} seconds")

    loop = asyncio.get_event_loop()
    x = await loop.run_in_executor(None, download, url, my_hook)
    file = await convert(x)
    theme = random.choice(themes)
    ctitle = CallbackQuery.message.chat.title
    ctitle = await CHAT_TITLE(ctitle)
    thumb = await gen_thumb(thumbnail, title, userid, theme, ctitle)
    await mystic.delete()
    if await is_active_chat(chat_id):
        position = await put(chat_id, file=file)
        buttons = play_markup(videoid, user_id)
        _chat_ = (str(file)).replace("_", "", 1).replace("/", "", 1).replace(".", "", 1)
        cpl = f"downloads/{_chat_}final.png"
        shutil.copyfile(thumb, cpl)
        f20 = open(f"search/{_chat_}title.txt", "w")
        f20.write(f"{title}")
        f20.close()
        f111 = open(f"search/{_chat_}duration.txt", "w")
        f111.write(f"{duration}")
        f111.close()
        f27 = open(f"search/{_chat_}username.txt", "w")
        f27.write(f"{checking}")
        f27.close()
        f28 = open(f"search/{_chat_}videoid.txt", "w")
        f28.write(f"{videoid}")
        f28.close()
        await mystic.delete()
        m = await CallbackQuery.message.reply_photo(
            photo=thumb,
            caption=f"""
<b>🎧 تمت إضافة المسارات إلى قائمة الانتظار</b>

<b>🖋 الاسم Kontol:</b>[{title[:25]}]({url})
<b>🕓 المده Kontol:</b> {duration}
<b>🎧</b> [My Bot](https://t.me/{BOT_USERNAME}?start=info_{id})
<b>🎧 مطلوبه من:</b> {checking}

<b>#️⃣ الاغنيه في قائمة رقم</b> {position}
""",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        os.remove(thumb)
        await CallbackQuery.message.delete()
    else:
        await music_on(chat_id)
        await add_active_chat(chat_id)
        await music.pytgcalls.join_group_call(
            chat_id,
            InputStream(
                InputAudioStream(
                    file,
                ),
            ),
            stream_type=StreamType().local_stream,
        )
        buttons = play_markup(videoid, user_id)
        await mystic.delete()
        m = await CallbackQuery.message.reply_photo(
            photo=thumb,
            reply_markup=InlineKeyboardMarkup(buttons),
            caption=f"""
<b>🖋 الاسم:</b> [{title[:25]}]({url})
<b>🕓 المدة:</b> {duration}
<b>🎧 الدخول إلي البوت:</b> [My Bot](https://t.me/{BOT_USERNAME}?start=info_{id})
<b>💁‍♂️ مطلوبة من:</b> {checking}
""",
        )
        os.remove(thumb)
        await CallbackQuery.message.delete()


@Client.on_callback_query(filters.regex(pattern=r"popat"))
async def popat(_,CallbackQuery): 
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    print(callback_request)
    userid = CallbackQuery.from_user.id 
    try:
        id , query, user_id = callback_request.split("|") 
    except Exception as e:
        return await CallbackQuery.message.edit(f"Terjadi Kesalahan\n**Kemungkinan alasannya adalah**:{e}")       
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer("This is not for you! Search You Own Song", show_alert=True)
    i=int(id)
    query = str(query)
    try:
        a = VideosSearch(query, limit=10)
        result = (a.result()).get("result")
        title1 = (result[0]["title"])
        duration1 = (result[0]["duration"])
        title2 = (result[1]["title"])
        duration2 = (result[1]["duration"])      
        title3 = (result[2]["title"])
        duration3 = (result[2]["duration"])
        title4 = (result[3]["title"])
        duration4 = (result[3]["duration"])
        title5 = (result[4]["title"])
        duration5 = (result[4]["duration"])
        title6 = (result[5]["title"])
        duration6 = (result[5]["duration"])
        title7= (result[6]["title"])
        duration7 = (result[6]["duration"])      
        title8 = (result[7]["title"])
        duration8 = (result[7]["duration"])
        title9 = (result[8]["title"])
        duration9 = (result[8]["duration"])
        title10 = (result[9]["title"])
        duration10 = (result[9]["duration"])
        ID1 = (result[0]["id"])
        ID2 = (result[1]["id"])
        ID3 = (result[2]["id"])
        ID4 = (result[3]["id"])
        ID5 = (result[4]["id"])
        ID6 = (result[5]["id"])
        ID7 = (result[6]["id"])
        ID8 = (result[7]["id"])
        ID9 = (result[8]["id"])
        ID10 = (result[9]["id"])                    
    except Exception as e:
        return await mystic.edit_text(f"Lagu Tidak Ditemukan.\n**Kemungkinan Alasan:**{e}")
    if i == 1:
        buttons = search_markup2(ID6, ID7, ID8, ID9, ID10, duration6, duration7, duration8, duration9, duration10 ,user_id, query)
        await CallbackQuery.edit_message_text(
            f"**الـرجـاء اخـتـيـار الاغـنـيـة الـمـطـلوبه مـن الاسـفـل **\n\n⁶ <b>{title6[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID6})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__\n\n₇ <b>{title7[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID7})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__\n\n⁸ <b>{title8[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID8})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__\n\n⁹ <b>{title9[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID9})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__\n\n¹⁰ <b>{title10[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID10})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__",    
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )  
        return    
    if i == 2:
        buttons = search_markup(ID1, ID2, ID3, ID4, ID5, duration1, duration2, duration3, duration4, duration5, user_id, query)
        await CallbackQuery.edit_message_text(
            f"**الـرجـاء اخـتـيـار الاغـنـة الـمـطـلوبة مـن الاسـفل**\n\n¹ <b>{title1[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID1})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__\n\n² <b>{title2[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID2})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__\n\n³ <b>{title3[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID3})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__\n\n⁴ <b>{title4[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID4})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__\n\n⁵ <b>{title5[:27]}</b>\n  ┗ 🎧 <u>__[My Bot](https://t.me/{BOT_USERNAME}?start=info_{ID5})__</u>\n  ┗ 🎥 __Powered by {BOT_NAME}__",    
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True 
        )  
        return
            


@app.on_message(filters.command(["playplaylist", "قائمه التشغيل",]))
async def play_playlist_cmd(_, message):
    thumb ="cache/IMG_20211230_211509_034.jpg"
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    buttons = playlist_markup(user_name, user_id)
    await message.reply_photo(
    photo=thumb, 
    caption=("**__اهلا بك في ميزه قائمة التشغيل__**\n\nحدد قائمة التشغيل التي تريد تشغيلها🎧 ،،"),    
    reply_markup=InlineKeyboardMarkup(buttons),
    )
    return
