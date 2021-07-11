import random
from itertools import repeat
from operator import itemgetter

import discord
import requests

from constants import diff, clr, api_url, headers
from utils import check_id, get_diff, get_partner_icon, get_ptt_recommendation_scores, format_time, format_score, \
    send_back_error, query_songname, query_constant, send_back_http_error


# Generate an Arcaea session depending of parameters entered by user
async def session_generator(message):
    code = await check_id(message.author.id)
    if not code:
        await message.reply("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    # Parse parameters
    params = message.content.split(" ")
    if len(params) <= 1 or len(params) % 2 == 0:
        await message.reply(
            "> Erreur: Paramètres incorrects, aucune session ne peut être générée (*Exemple : !session 8 4 9 2 9+ 1*)")
        return
    i = 1
    diffs = []
    nb_songs = []
    while i < len(params):
        if not params[i + 1].isdigit():
            await message.reply(
                "> Erreur: Le nombre de songs d'une difficulté ne doit contenir que des chiffres (*Exemple : !session 8 4 9 2 9+ 1*)")
            return
        diffs.append(params[i])
        nb_songs.append(int(params[i + 1]))
        i += 2

    response_best_30 = requests.post(f"{api_url}/user/best30?usercode={code}&overflow=400", headers=headers)
    if not response_best_30.ok:
        await send_back_http_error(message, response_best_30.status_code)
        return
    best_30_json = response_best_30.json()
    if best_30_json['status'] != 0:
        await send_back_error(message, best_30_json)
        return

    response_info = requests.post(f"{api_url}/user/info?usercode={code}", headers=headers)
    if not response_info.ok:
        await send_back_http_error(message, response_info.status_code)
        return
    info_json = response_info.json()
    if info_json['status'] != 0:
        await send_back_error(message, info_json)
        return

    profile = info_json['content']
    scores = []
    for elm in best_30_json['content']['best30_list']:
        scores.append(elm)

    for elm in best_30_json['content']['best30_overflow']:
        scores.append(elm)

    # Get PTT Recommendations so they can be used in the algorithm
    ptt_rec = get_ptt_recommendation_scores(scores, profile, 20)

    session_songs = []
    for i in range(len(diffs)):
        songs_list = sorted(filter(lambda score: get_diff(query_constant(score)) == diffs[i], scores),
                            key=itemgetter("time_played"), reverse=True)
        if len(songs_list) < nb_songs[i]:
            await message.reply(
                f'> Erreur: Impossible de générer {nb_songs[i]} songs de difficulté {diffs[i]} ({len(songs_list)} disponibles)')
            return
        songs_pool = []
        for j in range(len(songs_list)):
            song = songs_list[j]
            is_rec = len(list(filter(
                lambda rec_score: rec_score["song_id"] == song["song_id"] and rec_score["difficulty"] == song[
                    "difficulty"], ptt_rec)))  # Check if a song is in PTT Recommendations
            songs_pool.extend(repeat(song, j + 1 + is_rec * 2))
        for j in range(nb_songs[i]):
            song = random.choice(songs_pool)
            while len(list(filter(
                    lambda score: score["song_id"] == song["song_id"] and score["difficulty"] == song["difficulty"],
                    session_songs))) > 0:  # Avoid duplicate songs
                song = random.choice(songs_pool)
            session_songs.append(song)
    session_songs = sorted(session_songs, key=lambda x: query_constant(x), reverse=False)

    msg_emb = discord.Embed(title="Session Generator", type="rich", color=discord.Color.dark_teal())
    msg_emb.set_author(name=f'{profile["name"]}', icon_url=get_partner_icon(profile))
    msg_emb.set_footer(text="*(Credit: Okami)*")
    for elm in session_songs:
        msg_emb.add_field(name=f'**{query_songname(elm["song_id"])}\n<{diff[elm["difficulty"]]} '
                               f'{get_diff(query_constant(elm))}\>**',
                          value=f'> **{format_score(elm["score"])}** [{clr[elm["best_clear_type"]]}] '
                                f'(Rating: {round(elm["rating"], 3)})\n'
                                f'> Pure: {elm["perfect_count"]} ({elm["shiny_perfect_count"]}) \n'
                                f'> Far: {elm["near_count"]} | Lost: {elm["miss_count"]}\n'
                                f'> Date: {format_time(elm["time_played"]).split(" - ")[0]}')
    await message.reply(embed=msg_emb)
