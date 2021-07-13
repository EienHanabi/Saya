from operator import itemgetter
import discord
import requests

from constants import partners_names, api_url, headers
from utils import check_id, get_partner_icon, format_time, format_code, send_back_error, send_back_http_error


async def profile(message):
    code = await check_id(message.author.id)
    if not code:
        await message.channel.send("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    response_best_30 = requests.post(f"{api_url}/user/best30?usercode={code}", headers=headers)
    if not response_best_30.ok:
        best_30_str = "Unavailable"
        recent_10_str = "Unavailable"
        max_ptt_str = "Unavailable"
    else:
        best_30_json = response_best_30.json()
        if best_30_json['status'] != 0:
            best_30_str = "Unavailable"
            recent_10_str = "Unavailable"
            max_ptt_str = "Unavailable"
        else:
            best_30 = best_30_json['content']['best30_avg']
            recent_10 = best_30_json['content']['recent10_avg']
            best_30_str = "{:.3f}".format(best_30)
            recent_10_str = "{:.3f}".format(recent_10)
            scores = []
            for elm in best_30_json['content']['best30_list']:
                scores.append(elm)
            scores = sorted(scores, key=itemgetter("rating"), reverse=True)
            scores_top_10 = scores[0:10]
            sum_top_10 = sum([score['rating'] for score in scores_top_10])
            max_ptt = (best_30 * 30 + sum_top_10) / 40
            max_ptt_str = "{:.3f}".format(max_ptt)

    response_info = requests.post(f"{api_url}/user/info?usercode={code}&recent=1", headers=headers)
    if not response_info.ok:
        await send_back_http_error(message, response_info.status_code)
        return
    info_json = response_info.json()
    if info_json['status'] != 0:
        await send_back_error(message, info_json)
        return

    profile = info_json['content']

    rating = "{0:04d}".format(profile["rating"])[:2] + "." + "{0:04d}".format(profile["rating"])[2:] + " PTT"

    if rating == "-0.01 PTT":
        rating = "*Hidden*"

    msg_emb = discord.Embed(title="Profile", type="rich", color=discord.Color.dark_teal())
    msg_emb.set_thumbnail(url=get_partner_icon(profile))
    msg_emb.add_field(name=f'**{profile["name"]}\'s profile**',
                      value=f'> Rating: **{rating}**\n'
                            f'> Max PTT: **{max_ptt_str} PTT**\n'
                            f'> Best 30: **{best_30_str} PTT**\n'
                            f'> Recent 10: **{recent_10_str} PTT**\n'
                            f'> Favchar: **{partners_names[profile["character"]]}**\n'
                            f'> Last play: **{format_time(profile["recent_score"][0]["time_played"])}**\n'
                            f'> Join date: **{format_time(profile["join_date"])}**\n'
                            f'> Code: **{format_code(code)}**')
    await message.reply(embed=msg_emb)
