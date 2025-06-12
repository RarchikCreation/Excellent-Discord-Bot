
import disnake
from disnake.ext import commands
from disnake.ext.commands import CommandSyncFlags
import os
from utils.rpc.rpc_util import DiscordRPC
from buttons.tickets.ReplyButtonView import ReplyButtonView
from buttons.tickets.TicketButtonView import TicketButtonView
from cogs.commands.create_ticket import TICKET_CHANNEL_ID
from data.config import TOKEN, CLIENT_ID
from utils.database.db_util import load_all_tickets, init_db, load_all_created_tickets, migrate_db
from utils.console.logger_util import logger
from utils.rpc import rpc_util

intents = disnake.Intents(
    guilds=True,
    members=True,
    messages=True,
    message_content=True
)

sync_flags = CommandSyncFlags.default()
bot = commands.InteractionBot(intents=intents)

rpc = DiscordRPC(client_id=CLIENT_ID)

@bot.event
async def on_ready():
    logger(f"###################### {bot.user} ######################")
    bot.add_view(TicketButtonView())


    activity = disnake.Game("Excellent Omni — Разработчик » rare.creation")
    await bot.change_presence(status=disnake.Status.online, activity=activity)

    for message_id, user_id, issue_text, *_ in load_all_tickets():

        channel = bot.get_channel(TICKET_CHANNEL_ID)
        if channel:
            try:
                message = await channel.fetch_message(message_id)
                user = await bot.fetch_user(user_id)
                view = ReplyButtonView(user, issue_text, message)
                await message.edit(view=view)
            except Exception as e:
                logger(f"Failed to restore button: {e}")
    for user_id, channel_id in load_all_created_tickets():
        channel = bot.get_channel(channel_id)
        if not isinstance(channel, disnake.TextChannel):
            continue
        if channel:
            try:
                user = await bot.fetch_user(user_id)
                messages = [msg async for msg in channel.history(limit=10)]
                last_bot_message = next((m for m in messages if m.author.id == bot.user.id and m.components), None)

                if last_bot_message:
                    from buttons.tickets.CloseTicketView import CloseTicketView
                    view = CloseTicketView(channel, user, user)
                    await last_bot_message.edit(view=view)
            except Exception as e:
                logger(f"Failed to re-register close button in ticket channel {channel_id}: {e}")

def load_cogs():
    for root, _, files in os.walk("cogs"):
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                cog = f"{root.replace(os.sep, '.')}.{file[:-3]}"
                if cog not in bot.extensions:
                    try:
                        bot.load_extension(cog)
                        logger(f"{cog} has been loaded")
                    except Exception as e:
                        logger(f"Error loading cog {cog}: {e}")


if __name__ == "__main__":
    init_db()
    migrate_db()
    load_cogs()
    bot.run(TOKEN)
