import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction

from utils.role_check_util import check_trust_access

class CreateTicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="create_ticket", description="Создать сообщение с тикетом")
    async def create_ticket(self, inter: ApplicationCommandInteraction):
        if not await check_trust_access(inter):
            return

        await inter.response.defer(ephemeral=True)

        embed = disnake.Embed(
            description=(
                "🔔 **Поддержка**\n"
                "Помощь по вашим вопросам. Чтобы создать тикет, нажмите на кнопку ниже! \n\n"
                "⏰ **График работы**\n"
                "Пожалуйста, создавайте тикеты только по будням."
            ),
            color=disnake.Color.dark_purple()
        )

        await inter.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(CreateTicketCog(bot))
