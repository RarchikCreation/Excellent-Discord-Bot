import disnake
from disnake.ext import commands
from disnake.ui import View, Button, Modal, TextInput
from disnake import ApplicationCommandInteraction, ModalInteraction

from utils.users.role_check_util import check_trust_access

class ApplicationButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ApplicationButton())

class ApplicationButton(Button):
    def __init__(self):
        super().__init__(label="Отправить заявку", style=disnake.ButtonStyle.green, custom_id="application_button")

    async def callback(self, interaction: disnake.MessageInteraction):
        blocked_role = interaction.guild.get_role(1305991288843407462)
        if blocked_role in interaction.user.roles:
            await interaction.response.send_message("Вы не можете повторно подать заявку.", ephemeral=True)
            return

        await interaction.response.send_modal(ApplicationModal())

class ApplicationModal(Modal):
    def __init__(self):
        components = [
            TextInput(label="Возраст, имя, часовой пояс", custom_id="personal", style=disnake.TextInputStyle.paragraph, required=True, max_length=50),
            TextInput(label="Онлайн и активность на сервере", custom_id="activity", style=disnake.TextInputStyle.paragraph, required=True, max_length=100),
            TextInput(label="Опыт модерации, причины ухода", custom_id="experience", style=disnake.TextInputStyle.paragraph, required=True, max_length=500),
            TextInput(label="Что такое флуд? Объясните своими словами.", custom_id="communication", style=disnake.TextInputStyle.paragraph, required=True, max_length=150),
            TextInput(label="Знание и понимание правил сервера", custom_id="rules", style=disnake.TextInputStyle.paragraph, required=True, max_length=50),
        ]
        super().__init__(title="Заявка на персонал", components=components)

    async def callback(self, interaction: ModalInteraction):
        channel = interaction.bot.get_channel(1372568284830109758)
        embed = disnake.Embed(description=f"## 📨 Заявка от {interaction.user.mention}", color=disnake.Color.dark_blue())
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="Личная информация", value=interaction.text_values['personal'], inline=True)
        embed.add_field(name="Активность", value=interaction.text_values['activity'], inline=True)
        embed.add_field(name="Опыт модерации", value=interaction.text_values['experience'], inline=True)
        embed.add_field(name="Понимание флуда", value=interaction.text_values['communication'], inline=True)
        embed.add_field(name="Знание правил", value=interaction.text_values['rules'], inline=True)

        if channel:
            await channel.send(embed=embed, view=PersistentReviewView(applicant_id=interaction.user.id))
            await interaction.response.send_message("Ваша заявка получена на рассмотрение!", ephemeral=True)

class PersistentReviewView(View):
    def __init__(self, applicant_id=None):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id
        self.add_item(Button(label="Принять", style=disnake.ButtonStyle.green, custom_id="accept_application"))
        self.add_item(Button(label="Отказать", style=disnake.ButtonStyle.red, custom_id="reject_application"))

class InStaffTicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ApplicationButtonView())
        self.bot.add_view(PersistentReviewView())

    @commands.Cog.listener()
    async def on_button_click(self, interaction: disnake.MessageInteraction):
        if interaction.component.custom_id in ["accept_application", "reject_application"]:
            embed = interaction.message.embeds[0]
            mention = embed.description.split(" от ")[-1]
            user_id = int(mention.strip("<@!>"))
            user = interaction.guild.get_member(user_id)

            fields_text = ""
            for field in embed.fields:
                fields_text += f"**{field.name}:**\n{field.value}\n\n"

            if interaction.component.custom_id == "accept_application":
                roles_to_add = [1251855717686575144, 1251855556222914650]
                for role_id in roles_to_add:
                    role = interaction.guild.get_role(role_id)
                    if role:
                        await user.add_roles(role, reason="Заявка принята")

                embed_dm = disnake.Embed(
                    description=f"## Ответ на вашу заявку в персонал\nСодержание: \n```{fields_text}```\n\n**Решение:** Принят",
                    color=disnake.Color.light_grey()
                )
                embed_dm.set_thumbnail(url=interaction.user.display_avatar.url)
                try:
                    await user.send(embed=embed_dm)
                except:
                    await interaction.send("Не удалось отправить сообщение в ЛС пользователю.", ephemeral=True)

                await interaction.send("Пользователь принят.", ephemeral=True)

            elif interaction.component.custom_id == "reject_application":
                deny_role = interaction.guild.get_role(1305991288843407462)
                if deny_role:
                    await user.add_roles(deny_role, reason="Заявка отклонена")

                embed_dm = disnake.Embed(
                    description=f"## Ответ на вашу заявку в персонал\nСодержание: \n```{fields_text}```\n\n**Решение:** Отказ",
                    color=disnake.Color.light_grey()
                )
                embed_dm.set_thumbnail(url=interaction.user.display_avatar.url)
                try:
                    await user.send(embed=embed_dm)
                except:
                    await interaction.send("Не удалось отправить сообщение в ЛС пользователю.", ephemeral=True)

                await interaction.send("Пользователь отклонён.", ephemeral=True)

            await interaction.message.edit(view=None)

    @commands.slash_command(name="in_staff", description="Создать сообщение с формой персонала")
    async def in_staff(self, inter: ApplicationCommandInteraction):
        if not await check_trust_access(inter):
            return

        await inter.response.defer(ephemeral=True)

        embed = disnake.Embed(
            title="Excellent Staff",
            description=(
                "Чтобы отправить заявку, нажмите на кнопку ниже. Ответ от Куратора персонала поступит вам в личные сообщения через бота — убедитесь, что у вас включены личные сообщения.\n\n"
                ":exclamation: **Критерии:**\n\n "
                "Возраст от 15 лет \n - Требуется базовая зрелость, ответственность и способность вести спокойное общение.\n\n"
                "Грамотная письменная речь\n - Умение четко, понятно и без грубых ошибок излагать мысли.\n\n"
                "Адекватность \n - Спокойное поведение в конфликтных ситуациях, умение не поддаваться на провокации.\n\n"
                "Онлайн-активность \n - Регулярное присутствие для оперативного ответа на тикеты и наблюдения за чатом.\n\n"
                "Базовые знания правил сервера \n - Умение применять и объяснять правила другим пользователям."
            ),
            color=disnake.Color.red()
        )

        await inter.channel.send(embed=embed, view=ApplicationButtonView())
        await inter.followup.send("Сообщение отправлено.", ephemeral=True)

def setup(bot):
    bot.add_cog(InStaffTicketCog(bot))
