import disnake
from disnake.ext import commands
from disnake.ui import View, Button, Modal, TextInput
from disnake import ApplicationCommandInteraction, TextInputStyle

from utils.logger_util import logger
from utils.role_check_util import check_trust_access

TICKET_CHANNEL_ID = 1371931353313968128
ANSWER_CHANNEL_ID = 1371936365075234876

class TicketModal(Modal):
    def __init__(self, user: disnake.User):
        self.user = user
        components = [
            TextInput(
                label="Опишите подробно вашу проблему!",
                placeholder="Например: Не работает функция в клиенте...",
                custom_id="description",
                style=TextInputStyle.paragraph,
                max_length=1000
            )
        ]
        super().__init__(title="Обращение в поддержку", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        description = inter.text_values["description"]

        embed = disnake.Embed(
            description=f"## Обращение от {inter.user.mention}\n" + description,
            color=disnake.Color.dark_purple()
        )
        embed.set_thumbnail(url=inter.user.avatar.url if inter.user.avatar else None)

        ticket_channel = inter.guild.get_channel(TICKET_CHANNEL_ID)

        if ticket_channel:
            view = ReplyButtonView(inter.user, description, None)
            message = await ticket_channel.send(embed=embed, view=view)
            view.message_to_delete = message

        await inter.response.send_message("Ваше обращение принято на рассмотрение!", ephemeral=True)


class TicketButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Создать обращение", style=disnake.ButtonStyle.primary, custom_id="open_ticket_form")
    async def ticket_button_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(TicketModal(inter.user))

class CreateTicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="create_ticket", description="Создать сообщение с тикетом")
    async def create_ticket(self, inter: ApplicationCommandInteraction):
        if not await check_trust_access(inter):
            return

        await inter.response.defer(ephemeral=True)

        embed_ru = disnake.Embed(
            description=(
                "🔔 **Поддержка**\n"
                "Помощь по вашим вопросам. Чтобы создать обращение в поддержку, нажмите на кнопку ниже!\n\n"
                "⏰ **График работы**\n"
                "Пожалуйста, создавайте тикеты только по будням в промежутке 7:00 - 22:00.\n\n"
                ":exclamation: **Важно**\n"
                "Создавайте свои обращение с подробным описанием проблемы, иначе ваше обращение будет отклонено!\n"
                "Убедитесь, что у вас включены личные сообщения, иначе бот не сможет прислать вам ответ."
            ),
            color=disnake.Color.red()
        )

        embed_eng = disnake.Embed(
            description=(
                "🔔 **Support**\n"
                "Help with your questions. To create a ticket, click the button below!\n\n"
                "⏰ **Working hours**\n"
                "Please create tickets only on weekdays between 7:00 AM and 10:00 PM.\n\n"
                ":exclamation: **Important**\n"
                "Create your request with a detailed description of the problem, otherwise your request will be rejected!\n"
                "Make sure you have private messages enabled, otherwise the bot won't be able to send you a reply."
            ),
            color=disnake.Color.dark_purple()
        )

        await inter.channel.send(embeds=[embed_ru, embed_eng], view=TicketButtonView())

class ReplyModal(Modal):
    def __init__(self, user: disnake.User, issue_text: str, message_to_delete: disnake.Message):
        self.user = user
        self.issue_text = issue_text
        self.message_to_delete = message_to_delete


        components = [
            TextInput(
                label="Ответ на обращение",
                placeholder="Напишите здесь ответ пользователю...",
                custom_id="reply_text",
                style=TextInputStyle.paragraph,
                max_length=1000
            )
        ]
        super().__init__(title="Ответ на обращение", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        reply_text = inter.text_values["reply_text"]

        embed = disnake.Embed(
            description=(
                f"## Ответ на ваше обращение \n **Ваша проблема:**\n{self.issue_text}\n\n"
                f"**Ответ:**\n{reply_text}"
            ),

            color=disnake.Color.dark_purple()
        )
        embed.set_thumbnail(url=inter.user.avatar.url if inter.user.avatar else None)
        answer = disnake.Embed(
            title="Ответ на обращение",
            description=(
                f"**Пользователь:** {self.user.mention}\n"
                f"**Модератор:** {inter.user.mention}\n\n"
                f"**Проблема:**\n{self.issue_text}\n\n"
                f"**Ответ:**\n{reply_text}"
            ),
            color=disnake.Color.dark_purple()
        )
        answer_channel = inter.guild.get_channel(ANSWER_CHANNEL_ID)
        try:
            await self.user.send(embed=embed)
            await inter.response.send_message("Ответ успешно отправлен пользователю!", ephemeral=True)
            await answer_channel.send(embed=answer)
        except disnake.Forbidden:
            await inter.response.send_message("Не удалось отправить сообщение — у пользователя закрыты ЛС.", ephemeral=True)
        finally:
            if self.message_to_delete:
                try:
                    await self.message_to_delete.delete()
                except Exception as e:
                    logger(f"Failed to delete request message:{e}")


class ReplyButtonView(View):
    def __init__(self, user: disnake.User, issue_text: str, message_to_delete: disnake.Message):
        super().__init__(timeout=None)
        self.user = user
        self.issue_text = issue_text
        self.message_to_delete = message_to_delete

    @disnake.ui.button(label="Ответить", style=disnake.ButtonStyle.primary, custom_id="reply_to_ticket")
    async def reply_button_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(ReplyModal(self.user, self.issue_text, self.message_to_delete))


def setup(bot):
    bot.add_cog(CreateTicketCog(bot))
