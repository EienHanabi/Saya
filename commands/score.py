import aiosqlite
import discord
import requests

from constants import diff, cover, clr, songlist, api_url, headers
from utils import check_id, format_time, format_score, send_back_error, send_back_http_error, query_songname, get_diff, \
    query_constant


async def score(message):
    code = await check_id(message.author.id)
    if not code:
        await message.reply("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    songlist_0 = []
    for elm in songlist['songs']:
        songlist_0.append({elm['id']: elm['title_localized']['en']})

    songname = " ".join(message.content.split(" ")[1:-1]).strip().lower()

    # Verification de la difficulté
    diff_asked = message.content.split(" ")[-1]
    try:
        if diff.index(diff_asked.upper()) == -1:
            await message.reply("> Erreur: Le format de la difficulté n'existe pas")
            return
        diff_asked = diff.index(diff_asked.upper())
    except ValueError:
        await message.reply("> Erreur: Le format de la difficulté n'existe pas")
        return

    song = [d for d in songlist_0 if any(songname in v.lower() for v in d.values())]

    if len(song) == 0:
        await message.reply("> Erreur: Aucune song n'a été trouvée")
        return
    elif len(song) > 1:
        await message.reply("> Erreur: Plus d'une song a été trouvée, soyez plus precis !")
        return
    else:
        songname = list(song[0].values())[0]
        song = list(song[0].keys())[0]

    api_response = requests.post(
        f"{api_url}/user/history", headers=headers,
        params={"usercode": code, "quantity": 1, "songname": song, "difficulty": diff_asked}, timeout=180)
    if not api_response.ok:
        await send_back_http_error(message, api_response.status_code)
        return
    history_json = api_response.json()
    if history_json['status'] != 0:
        await send_back_error(message, history_json)
        return

    if len(history_json['content']['history']) == 0:
        await message.reply("You did not play this song or the API is not aware you played it :C")
        return
    score_data = history_json['content']['history'][0]

    if score_data["difficulty"] == 3:
        cover_url = cover + "3_" + score_data["song_id"] + ".jpg"
    else:
        cover_url = cover + score_data["song_id"] + ".jpg"
    msg_emb = discord.Embed(
        title=f'{query_songname(score_data["song_id"])} <{diff[score_data["difficulty"]]} '
              f'{get_diff(query_constant(score_data))} | {query_constant(score_data)}\>',
        type="rich", color=discord.Color.dark_teal())
    msg_emb.set_thumbnail(url=cover_url)
    msg_emb.add_field(name=f'{format_score(score_data["score"])} [{clr[score_data["best_clear_type"]]}]',
                      value=f'> **Rating:** {round(score_data["rating"], 3)}\n'
                            f'> **Pure:** {score_data["perfect_count"]} ({score_data["shiny_perfect_count"]}) \n'
                            f'> **Far:** {score_data["near_count"]} |  **Lost:** {score_data["miss_count"]}\n'
                            f'> **Date:** {format_time(score_data["time_played"]).split(" - ")[0]}')
    await message.reply(embed=msg_emb)
