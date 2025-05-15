import disnake
from disnake.ui import View

class TicketButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="📩 Создать обращение", style=disnake.ButtonStyle.primary, custom_id="open_ticket_form")
    async def ticket_button_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        from cogs.commands.create_ticket import TicketModal
        await inter.response.send_modal(TicketModal(inter.user))
