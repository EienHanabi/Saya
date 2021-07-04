import discord
import random

from ArcProbeInterface import AsyncAPI
from itertools import repeat
from operator import itemgetter

from constants import diff, clr
from utils import check_id, get_diff, get_partner_icon, get_ptt_recommendation_scores, format_time, format_score


# Generate an Arcaea session depending of parameters entered by user
async def session_generator(message):
    code = await check_id(message.author.id)
    if not code:
        await message.channel.send("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    # Parse parameters
    params = message.content.split(" ")
    if len(params) <= 1 or len(params) % 2 == 0:
        await message.channel.send(
            "> Erreur: Paramètres incorrects, aucune session ne peut être générée (*Exemple : !session 8 4 9 2 9+ 1*)")
        return
    i = 1
    diffs = []
    nb_songs = []
    while i < len(params):
        if not params[i + 1].isdigit():
            await message.channel.send(
                "> Erreur: Le nombre de songs d'une difficulté ne doit contenir que des chiffres (*Exemple : !session 8 4 9 2 9+ 1*)")
            return
        diffs.append(params[i])
        nb_songs.append(int(params[i + 1]))
        i += 2

    api_ = AsyncAPI(user_code=code)
    data = await api_.fetch_data()
    songlist = data['songtitle']
    prfl = data['userinfo']
    scores = []
    for elm in data['scores']:
        scores.append(elm)

    # Get PTT Recommendations so they can be used in the algorithm
    ptt_rec = get_ptt_recommendation_scores(scores, prfl, 20)

    session_songs = []
    for i in range(len(diffs)):
        songs_list = sorted(filter(lambda score: get_diff(score["constant"]) == diffs[i], scores),
                            key=itemgetter("time_played"), reverse=True)
        if len(songs_list) < nb_songs[i]:
            await message.channel.send(
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
    session_songs = sorted(session_songs, key=itemgetter("constant"), reverse=False)

    msg_emb = discord.Embed(title="Session Generator", type="rich", color=discord.Color.dark_teal())
    msg_emb.set_author(name=f'{prfl["name"]}', icon_url=get_partner_icon(prfl))
    msg_emb.set_footer(text="*(Credit: Okami)*")
    for elm in session_songs:
        msg_emb.add_field(name=f'**{songlist[elm["song_id"]]["en"]}\n<{diff[elm["difficulty"]]} '
                               f'{get_diff(elm["constant"])}\>**',
                          value=f'> **{format_score(elm["score"])}** [{clr[elm["best_clear_type"]]}] '
                                f'(Rating: {round(elm["rating"], 3)})\n'
                                f'> Pure: {elm["perfect_count"]} ({elm["shiny_perfect_count"]}) \n'
                                f'> Far: {elm["near_count"]} | Lost: {elm["miss_count"]}\n'
                                f'> Date: {format_time(elm["time_played"]).split(" - ")[0]}')
    await message.channel.send(embed=msg_emb)
