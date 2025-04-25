import disnake
from disnake import ApplicationCommandInteraction
from data.config import TRUST_ROLE_ID

def has_trust_role(member: disnake.Member) -> bool:
    return any(role.id == 1251855905587200032 for role in member.roles)

async def check_trust_access(inter: ApplicationCommandInteraction) -> bool:
    if not has_trust_role(inter.author):
        await inter.response.send_message("У вас нет доступа к этой команде.", ephemeral=True)
        return False
    return True
