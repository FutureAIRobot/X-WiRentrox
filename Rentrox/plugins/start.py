
import logging
logger = logging.getLogger(__name__)
from Rentrox.bot import Bot as Rentrox 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters

url_button=InlineKeyboardMarkup(
        [
              [
                  InlineKeyboardButton("⚙ UPDATE CHANNE", url='https://t.me/Lx0980AI'), 
                  InlineKeyboardButton("⭕️ SOURCE", url='https://github.com/0AIB/Auto-Forward-Bot')
              ]
        ]
) 

################################################################################################################################################################################################################################################
# start command

@Rentrox.on_message(filters.command("start") & filters.private & filters.incoming)
async def start(client, message):
    await message.reply(
        text="Hi There I'm Rentrox",
        disable_web_page_preview=True,
        reply_markup = url_button,
        quote=True
    )

################################################################################################################################################################################################################################################
# about command

@Rentrox.on_message(filters.command("about") & filters.private & filters.incoming)
async def about(client, message):
    await message.reply(
        text="Here is About me",
        disable_web_page_preview=True,
        reply_markup = url_button,
        quote=True
    )
