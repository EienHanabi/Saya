import discord
import requests

from constants import cover, diff, clr, api_url, headers
from utils import check_id, get_partner_icon, get_diff, format_score, format_time, send_back_error, query_songname, \
    query_constant, send_back_http_error


async def recent(message):
    code = await check_id(message.author.id)
    if not code:
        await message.reply("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    response_info = requests.post(f"{api_url}/user/info?usercode={code}&recent=1", headers=headers)
    if not response_info.ok:
        await send_back_http_error(message, response_info.status_code)
        return
    info_json = response_info.json()
    if info_json['status'] != 0:
        await send_back_error(message, info_json)
        return

    profile = info_json['content']
    recent = profile["recent_score"][0]

    if recent["difficulty"] == 3:
        cover_url = cover + "3_" + recent["song_id"] + ".jpg"
    else:
        cover_url = cover + recent["song_id"] + ".jpg"
    msg_emb = discord.Embed(title=f'{query_songname(recent["song_id"])} <{diff[recent["difficulty"]]} {get_diff(query_constant(recent))}\>', type="rich", color=discord.Color.dark_teal())
    msg_emb.set_thumbnail(url=cover_url)
    msg_emb.set_author(name=f'{profile["name"]}', icon_url=get_partner_icon(profile))
    msg_emb.add_field(name=f'{format_score(recent["score"])} [{clr[recent["best_clear_type"]]}]',
                      value=f'> **Rating:** {round(recent["rating"], 3)}\n'
                            f'> **Pure:** {recent["perfect_count"]} ({recent["shiny_perfect_count"]}) \n'
                            f'> **Far:** {recent["near_count"]} |  **Lost:** {recent["miss_count"]}\n'
                            f'> **Date:** {format_time(recent["time_played"]).split(" - ")[0]}')
    await message.reply(embed=msg_emb)
