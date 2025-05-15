import disnake
from disnake import Embed

from permanent.constans import ANSWER_CHANNEL_ID, SUPPORT_ROLE_ID

class CloseTicketView(disnake.ui.View):
    def __init__(self, channel: disnake.TextChannel, user: disnake.User, moderator: disnake.User):
        super().__init__(timeout=None)
        self.channel = channel
        self.user = user
        self.moderator = moderator

    @disnake.ui.button(label="Закрыть тикет", style=disnake.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if SUPPORT_ROLE_ID not in [role.id for role in inter.user.roles]:
            await inter.response.send_message("У вас нет прав закрывать тикеты.", ephemeral=True)
            return

        await inter.response.defer()

        answer_channel = disnake.utils.get(self.channel.guild.text_channels, id=ANSWER_CHANNEL_ID)

        messages = [msg async for msg in self.channel.history(limit=None, oldest_first=True)]
        message_lines = [f"{m.author.display_name}: {m.content}" for m in messages if m.content]

        if message_lines:
            formatted_log = "\n".join(message_lines)[-1900:]

            embed = Embed(
                title="📑 Архив тикета",
                description=f"```{formatted_log}```",
                color=disnake.Color.light_grey()
            )
            embed.set_footer(text=f"Закрыл: {inter.user.display_name}",
                             icon_url=inter.user.avatar.url if inter.user.avatar else None)

            await answer_channel.send(embed=embed)
        else:
            embed = Embed(
                title="📑 Архив тикета",
                description=f"Тикет `{self.channel.name}` был закрыт, но сообщений не было.",
                color=disnake.Color.light_grey()
            )
            embed.set_footer(text=f"Закрыл: {inter.user.display_name}",
                             icon_url=inter.user.avatar.url if inter.user.avatar else None)

            await answer_channel.send(embed=embed)

        await self.channel.delete(reason="Тикет закрыт модератором")
