import disnake
from disnake.ui import View

from permanent.constans import TICKET_CATEGORY_ID, SUPPORT_ROLE_ID
from utils.database.db_util import delete_ticket
from utils.console.logger_util import logger

class ReplyButtonView(View):
    def __init__(self, user: disnake.User, issue_text: str, message_to_delete: disnake.Message):
        super().__init__(timeout=None)
        self.user = user
        self.issue_text = issue_text
        self.message_to_delete = message_to_delete

    @disnake.ui.button(label="📨 Ответить", style=disnake.ButtonStyle.primary, custom_id="reply_to_ticket")
    async def reply_button_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        from cogs.commands.create_ticket import ReplyModal
        await inter.response.send_modal(ReplyModal(self.user, self.issue_text, self.message_to_delete))

    @disnake.ui.button(label="🎫 Создать тикет", style=disnake.ButtonStyle.secondary, custom_id="create_ticket_channel")
    async def create_ticket_channel_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        from buttons.tickets.CloseTicketView import CloseTicketView
        guild = inter.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        support_role = guild.get_role(SUPPORT_ROLE_ID)

        overwrites = {
            guild.default_role: disnake.PermissionOverwrite(view_channel=False),
            self.user: disnake.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            inter.user: disnake.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            support_role: disnake.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{self.user.name}",
            category=category,
            overwrites=overwrites,
            reason="Создание тикета по обращению"
        )

        embed = disnake.Embed(
            title="🎫 Тикет создан",
            description=f"Обсуждение проблемы пользователя: {self.user.mention}\n\n**Содержание:**\n{self.issue_text}",
            color=disnake.Color.blurple()
        )
        view = CloseTicketView(channel, self.user, inter.user)
        await channel.send(embed=embed, view=view)
        await inter.response.send_message(f"Канал {channel.mention} успешно создан!", ephemeral=True)

        from utils.database.db_util import log_created_ticket
        log_created_ticket(self.user.id, channel.id, self.issue_text, inter.user.id)


        if self.message_to_delete:
            try:
                await self.message_to_delete.delete()
                delete_ticket(self.message_to_delete.id)
            except Exception as e:
                logger(f"Failed to delete request message after creating ticket: {e}")
