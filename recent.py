import discord

from ArcProbeInterface import AsyncAPI

from constants import cover, diff, clr
from utils import check_id, get_partner_icon, get_diff, format_score, format_time

async def recent(message):
    code = await check_id(message.author.id)
    if not code:
        await message.channel.send("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    api_ = AsyncAPI(user_code=code)
    data = await api_.fetch_data()
    songlist = data[0]
    prfl = data[1]
    recent = prfl["recent_score"][0]

    if recent["difficulty"] == 3:
        cover_url = cover + "3_" + recent["song_id"] + ".jpg"
    else:
        cover_url = cover + recent["song_id"] + ".jpg"
    msg_emb = discord.Embed(title="Last play", type="rich", color=discord.Color.dark_teal())
    msg_emb.set_thumbnail(url=cover_url)
    msg_emb.set_author(name=f'{prfl["name"]}', icon_url=get_partner_icon(prfl))
    msg_emb.add_field(name=f'**{songlist[recent["song_id"]]["en"]}\n<{diff[recent["difficulty"]]} '
                           f'{get_diff(recent["constant"])}\>**',
                      value=f'> **{format_score(recent["score"])}** [{clr[recent["best_clear_type"]]}] '
                            f'(Rating: {round(recent["rating"], 3)})\n'
                            f'> Pure: {recent["perfect_count"]} ({recent["shiny_perfect_count"]}) \n'
                            f'> Far: {recent["near_count"]} |  Lost: {recent["miss_count"]}\n'
                            f'> Date: {format_time(recent["time_played"]).split(" - ")[0]}')
    await message.channel.send(embed=msg_emb)