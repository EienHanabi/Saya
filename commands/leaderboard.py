import discord
import aiosqlite

from datetime import datetime

import requests
from ArcProbeInterface import AsyncAPI

from constants import diff, cover, clr, songlist, api_url, headers
from utils import check_id, format_time, format_score, send_back_error, send_back_http_error


async def leaderboard(message):
    code = await check_id(message.author.id)
    if not code:
        await message.reply("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    # Get song name

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

    # Score updating
    async with aiosqlite.connect(f"leaderboard.db") as db:
        async with db.execute(f"SELECT * FROM 'last-update' WHERE code = {code}") as c:
            res = await c.fetchall()
            if len(res) == 0:
                async with db.execute(f"INSERT INTO 'last-update' (code, 'last-update') VALUES "
                                      f"('{code}', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')"):
                    await db.commit()
                    await add_scores(message, code)
            else:
                if (datetime.strptime(res[0][1], '%Y-%m-%d %H:%M:%S') - datetime.now()).days >= 1:
                    async with db.execute(
                            f"UPDATE 'last-update' SET 'last-update'={datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
                            f"WHERE code='{code}'"):
                        await db.commit()
                        await add_scores(message, code)

    # Leaderboard
    async with aiosqlite.connect(f"leaderboard.db") as db:
        async with db.execute(f"SELECT * FROM scores WHERE song='{song}' AND diff={diff_asked}") as c:
            res = await c.fetchall()
            if len(res) == 0:
                await message.reply("> Erreur: Aucun score trouvé pour cette track")
                pass
            else:
                if diff_asked == 3:
                    cover_url = cover + "3_" + song + ".jpg"
                else:
                    cover_url = cover + song + ".jpg"
                msg_emb = discord.Embed(title=f"Leaderboard | {songname} <{diff[diff_asked]}>",
                                        type="rich", color=discord.Color.dark_teal())
                msg_emb.set_thumbnail(url=cover_url)
                res.sort(key=lambda x: x[4], reverse=True)
                for elm in res:
                    username = elm[3]
                    score = format_score(elm[4])
                    stats = elm[5].split(";")
                    clear_type = elm[6]
                    date = elm[7]
                    msg_emb.add_field(name=f'**{username}**',
                                      value=f'> **{score}** [{clr[clear_type]}]\n'
                                            f'> Pure: {stats[1]} ({stats[0]})\n'
                                            f'> Far: {stats[2]} | Lost: {stats[3]}\n'
                                            f'> Date: {date}')
                await message.reply(embed=msg_emb)


async def forceupdate(message):
    code = await check_id(message.author.id)
    if not code:
        await message.reply("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return
    await add_scores(message, code)
    await message.reply("> Mise à jour effectuée.")


async def add_scores(message, code):
    r_b30 = requests.post(f"{api_url}/user/best30?usercode={code}&overflow=400", headers=headers)
    if not r_b30.ok:
        await send_back_http_error(message, r_b30.status_code)
        return
    b30_json = r_b30.json()
    if b30_json['status'] != 0:
        await send_back_error(message, b30_json)
        return

    r_info = requests.post(f"{api_url}/user/info?usercode={code}", headers=headers)
    if not r_info.ok:
        await send_back_http_error(message, r_info.status_code)
        return
    info_json = r_info.json()
    if info_json['status'] != 0:
        await send_back_error(message, info_json)
        return

    username = info_json['content']['name']

    async with aiosqlite.connect(f"leaderboard.db") as db:
        for line in [*b30_json['content']['best30_list'], *b30_json['content']['best30_overflow']]:
            song = line["song_id"]
            diff = line["difficulty"]
            score = line["score"]
            clear_type = line["clear_type"]
            date = format_time(line["time_played"])
            stats = f"{line['shiny_perfect_count']};{line['perfect_count']};{line['near_count']};{line['miss_count']}"
            async with db.execute(
                    f"SELECT * FROM scores WHERE username='{username}' AND song='{song}' AND diff={diff}") as c:
                res = await c.fetchall()
            if len(res) != 0:
                if res[0][4] == score:
                    pass
                else:
                    async with db.execute(
                            f"UPDATE scores SET score={score}, stats={stats}, clear_type={clear_type}, date='{date}' WHERE id={res[0][0]}"):
                        await db.commit()
            else:
                params = (song, diff, username, score, stats, clear_type, date)
                async with db.execute(f"INSERT INTO scores VALUES "
                                      f"(NULL, ?, ?, ?, ?, ?, ?, ?)", params):
                    await db.commit()
