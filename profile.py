import discord
import requests

from constants import partners_names, api_url, headers
from utils import check_id, get_partner_icon, format_time, format_code, send_back_error


async def profile(message):
    code = await check_id(message.author.id)
    if not code:
        await message.channel.send("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    r_b30 = requests.post(f"{api_url}/user/best30?usercode={code}", headers=headers)
    b30_json = r_b30.json()
    if b30_json['status'] != 0:
        await send_back_error(message, b30_json)
        return

    r_info = requests.post(f"{api_url}/user/info?usercode={code}&recent=1", headers=headers)
    info_json = r_info.json()
    if info_json['status'] != 0:
        await send_back_error(message, info_json)
        return

    prfl = info_json['content']

    b30 = b30_json['content']['best30_avg']
    r10 = b30_json['content']['recent10_avg']

    b30f = "{:.3f}".format(b30)
    r10f = "{:.3f}".format(r10)

    rating = "{0:04d}".format(prfl["rating"])[:2] + "." + "{0:04d}".format(prfl["rating"])[2:] + " PTT"

    if rating == "-0.01 PTT":
        rating = "*Hidden*"

    msg_emb = discord.Embed(title="Profile", type="rich", color=discord.Color.dark_teal())
    msg_emb.set_thumbnail(url=get_partner_icon(prfl))
    msg_emb.add_field(name=f'**{prfl["name"]}\'s profile**',
                      value=f'> Rating: **{rating}**\n'
                            f'> Best 30: **{b30f} PTT**\n'
                            f'> Recent 10: **{r10f} PTT**\n'
                            f'> Favchar: **{partners_names[prfl["character"]]}**\n'
                            f'> Last play: **{format_time(prfl["recent_score"][0]["time_played"])}**\n'
                            f'> Join date: **{format_time(prfl["join_date"])}**\n'
                            f'> Code: **{format_code(code)}**')
    await message.channel.send(embed=msg_emb)
