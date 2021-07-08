import discord
import requests

from constants import cover, diff, clr, api_url, headers
from utils import check_id, get_partner_icon, get_diff, format_score, format_time, send_back_error, query_songname, \
    query_constant


async def recent(message):
    code = await check_id(message.author.id)
    if not code:
        await message.channel.send("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    r_info = r_info = requests.post(f"{api_url}/user/info?usercode={code}&recent=1", headers=headers)
    info_json = r_info.json()
    if info_json['status'] != 0:
        await send_back_error(message, info_json)
        return

    prfl = info_json['content']
    recent = prfl["recent_score"][0]

    if recent["difficulty"] == 3:
        cover_url = cover + "3_" + recent["song_id"] + ".jpg"
    else:
        cover_url = cover + recent["song_id"] + ".jpg"
    msg_emb = discord.Embed(title="Last play", type="rich", color=discord.Color.dark_teal())
    msg_emb.set_thumbnail(url=cover_url)
    msg_emb.set_author(name=f'{prfl["name"]}', icon_url=get_partner_icon(prfl))
    msg_emb.add_field(name=f'**{query_songname(recent["song_id"])}\n<{diff[recent["difficulty"]]} '
                           f'{get_diff(query_constant(recent))}\>**',
                      value=f'> **{format_score(recent["score"])}** [{clr[recent["best_clear_type"]]}] '
                            f'(Rating: {round(recent["rating"], 3)})\n'
                            f'> Pure: {recent["perfect_count"]} ({recent["shiny_perfect_count"]}) \n'
                            f'> Far: {recent["near_count"]} |  Lost: {recent["miss_count"]}\n'
                            f'> Date: {format_time(recent["time_played"]).split(" - ")[0]}')
    await message.channel.send(embed=msg_emb)
