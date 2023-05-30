import re, pyrogram
from pyrogram import filters, enums, Client
from Rentrox import Config
from Rentrox.bot import Bot
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

MEDIA_FILTER = enums.MessagesFilter.VIDEO 
BUTTONS = {}

SPELL_CHECK = {}






async def perform_search(client: Bot, message: Message, query: str):
    btn = []
    async for msg in client.USER.search_messages(Config.SEARCHCHANNEL_ID, query=query, filter=MEDIA_FILTER):
        file_name = msg.video.file_name
        msg_id = msg.id
        link = msg.link
        btn.append([InlineKeyboardButton(text=f"{file_name}", url=f"{link}")])

    if not btn:
        await message.reply_text("Your Request not Available")
        return
    
    if len(btn) > 5: 
        btns = list(split_list(btn, 5)) 
        keyword = f"{message.chat.id}-{message.id}"
        BUTTONS[keyword] = {
            "total" : len(btns),
            "buttons" : btns
        }
    else:
        buttons = btn
        buttons.append(
            [InlineKeyboardButton(text="📃 Pages 1/1",callback_data="pages")]
        )
        await message.reply_text(
            f"<b> Here is the result for {message.text}</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    data = BUTTONS[keyword]
    buttons = data['buttons'][0].copy()

    buttons.append(
        [InlineKeyboardButton(text="NEXT ⏩",callback_data=f"next_0_{keyword}")]
    )    
    buttons.append(
        [InlineKeyboardButton(text=f"📃 Pages 1/{data['total']}",callback_data="pages")]
    )

    await message.reply_text(
            f"<b> Here is the result for {message.text}</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )    
        


async def spell_check(client: Bot, message: Message):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", message.text, flags=re.IGNORECASE)  # remove common words
    query = query.strip() + " movie"
    g_s = await search_gagala(query)
    g_s += await search_gagala(message.text)
    gs_parsed = []
    if not g_s:
        k = await message.reply("I couldn't find any movie with that name.")
        await asyncio.sleep(8)
        await k.delete()
        return

    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE)  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(
        r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)',
        '', i, flags=re.IGNORECASE) for i in gs]
    
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*",
                         re.IGNORECASE)  # match something like Watch Niram | Amazon Prime
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    
    user = message.from_user.id if message.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed))  # removing duplicates
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    if gs_parsed:
        for mov in gs_parsed:
            imdb_s = await get_poster(mov.strip(), bulk=True)  # searching each keyword in imdb
            if imdb_s:
                movielist += [movie.get('title') for movie in imdb_s]
    
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    
    if not movielist:
        k = await message.reply("I couldn't find anything related to that. Check your spelling.")
        await asyncio.sleep(8)
        await k.delete()
        return
    
    SPELL_CHECK[message.message_id] = movielist
    btn = [
        [
            InlineKeyboardButton(
                text=movie.strip(),
                callback_data=f"spolling#{user}#{message.message_id}",
            )
        ] for movie in movielist
    ]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spolling#{user}#close_spellcheck')])
    await message.reply(
        "I couldn't find anything related to that.\nDid you mean any one of these?",
        reply_markup=InlineKeyboardMarkup(btn)
    )


@Client.on_message(filters.chat(Config.GROUPS) & filters.text)
async def filter(client: Bot, message: Message):
    if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
        return

    if len(message.text) > 2:
        await perform_search(client, message, message.text)
        if not BUTTONS:
            await spell_check(client, message)


