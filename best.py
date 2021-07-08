import discord
import requests

from constants import cover, diff, clr, api_url, headers
from utils import check_id, get_partner_icon, get_diff, format_score, format_time, send_back_error, query_songname, \
    query_constant


async def best(message):
    code = await check_id(message.author.id)
    nb_scores = 30
    if not code:
        await message.channel.send("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    if len(message.content.split(" ")) > 1:
        if message.content.split(" ")[1].isdigit():
            if 1 <= int(message.content.split(" ")[1]) <= 30:
                nb_scores = int(message.content.split(" ")[1])

    r_b30 = requests.post(f"{api_url}/user/best30?usercode={code}", headers=headers)
    b30_json = r_b30.json()
    if b30_json['status'] != 0:
        await send_back_error(message, b30_json)
        return

    r_info = requests.post(f"{api_url}/user/info?usercode={code}", headers=headers)
    info_json = r_info.json()
    if info_json['status'] != 0:
        await send_back_error(message, info_json)
        return

    prfl = info_json['content']
    ls_top = b30_json['content']['best30_list']

    msg_emb = discord.Embed(title=f'Top {nb_scores}', type="rich", color=discord.Color.dark_teal())
    msg_emb.set_author(name=f'{prfl["name"]}', icon_url=get_partner_icon(prfl))

    if nb_scores == 1:
        if ls_top[0]["difficulty"] == 3:
            cover_url = cover + "3_" + ls_top[0]["song_id"] + ".jpg"
        else:
            cover_url = cover + ls_top[0]["song_id"] + ".jpg"
        msg_emb.set_thumbnail(url=cover_url)

    if nb_scores > len(ls_top):
        nb_scores = len(ls_top)

    for i in range(nb_scores):
        if i == round(nb_scores / 2) and nb_scores > 20:
            await message.channel.send(embed=msg_emb)
            msg_emb = discord.Embed(title="Top 30", type="rich", color=discord.Color.dark_teal())
            msg_emb.set_author(name=f'{prfl["name"]}', icon_url=get_partner_icon(prfl))
        msg_emb.add_field(name=f'**{query_songname(ls_top[i]["song_id"])}\n<{diff[ls_top[i]["difficulty"]]} '
                               f'{get_diff(query_constant(ls_top[i]))}\>**',
                          value=f'> **{format_score(ls_top[i]["score"])}** [{clr[ls_top[i]["best_clear_type"]]}] '
                                f'(Rating: {round(ls_top[i]["rating"], 3)})\n'
                                f'> Pure: {ls_top[i]["perfect_count"]} ({ls_top[i]["shiny_perfect_count"]}) \n'
                                f'> Far: {ls_top[i]["near_count"]} | Lost: {ls_top[i]["miss_count"]}\n'
                                f'> Date: {format_time(ls_top[i]["time_played"]).split(" - ")[0]}')
    await message.channel.send(embed=msg_emb)
