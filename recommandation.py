import discord

from Arcapi import AsyncApi

from constants import diff, clr
from utils import check_id, get_diff, get_partner_icon, get_ptt_recommendation_scores, format_time, format_score


# Gives [1-20] PTT recommendations
async def ptt_recommendation(message):
    code = await check_id(message.author.id)
    if not code:
        await message.channel.send("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    nb_scores = 5
    if len(message.content.split(" ")) > 1:
        if message.content.split(" ")[1].isdigit():
            if 1 <= int(message.content.split(" ")[1]) <= 20:
                nb_scores = int(message.content.split(" ")[1])

    api_ = AsyncApi(user_code=code)
    data = await api_.scores()
    songlist = data[0]
    prfl = data[1]
    scores = []
    for elm in data[2:]:
        scores.append(elm)

    ptt_rec = get_ptt_recommendation_scores(scores, prfl, nb_scores)

    msg_emb = discord.Embed(title="Recommendation", type="rich", color=discord.Color.dark_teal())
    msg_emb.set_author(name=f'{prfl["name"]}', icon_url=get_partner_icon(prfl))
    msg_emb.set_footer(text="*(Credit: Okami)*")
    for elm in ptt_rec:
        msg_emb.add_field(name=f'**{songlist[elm["song_id"]]["en"]}\n<{diff[elm["difficulty"]]} '
                               f'{get_diff(elm["constant"])}\>**',
                          value=f'> **{format_score(elm["score"])}** [{clr[elm["best_clear_type"]]}] '
                                f'(Rating: {round(elm["rating"], 3)})\n'
                                f'> Pure: {elm["perfect_count"]} ({elm["shiny_perfect_count"]}) \n'
                                f'> Far: {elm["near_count"]} | Lost: {elm["miss_count"]}\n'
                                f'> Date: {format_time(elm["time_played"]).split(" - ")[0]}')
    await message.channel.send(embed=msg_emb)