from funct import check_id, format_time, format_score
from datetime import datetime
import aiosqlite
from Arcapi import AsyncApi
import discord

diff_l = ["PST", "PRS", "FTR", "BYD"]
clr = ["F", "NC", "FR", "PM", "EC", "HC"]
cover = "http://119.23.30.103:8080/ArcAssets/cover/"


async def leaderboard(message):
    code = await check_id(message.author.id)
    if not code:
        await message.channel.send("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    # Get song name
    api_ = AsyncApi(user_code=code)
    data = await api_.scores()
    songlist0 = data[0]

    songlist = []
    for elm in songlist0:
        songlist.append({elm: songlist0[elm]["en"]})

    songname = " ".join(message.content.split(" ")[1:-1]).strip()

    # Verification de la difficulté
    diff = message.content.split(" ")[-1]
    try:
        if diff_l.index(diff.upper()) == -1:
            await message.channel.send("> Erreur: Le format de la difficulté n'existe pas")
            return
        diff = diff_l.index(diff.upper())
    except ValueError:
        await message.channel.send("> Erreur: Le format de la difficulté n'existe pas")
        return

    song = [d for d in songlist if any(songname in v.lower() for v in d.values())]

    if len(song) == 0:
        await message.channel.send("> Erreur: Aucune song n'a été trouvée")
        return
    elif len(song) > 1:
        await message.channel.send("> Erreur: Plus d'une song a été trouvée, soyez plus precis !")
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
                    await add_scores(code)
            else:
                if (datetime.strptime(res[0][1], '%Y-%m-%d %H:%M:%S') - datetime.now()).days >= 7:
                    async with db.execute(
                            f"UPDATE 'last-update' SET 'last-update'={datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
                            f"WHERE code='{code}'"):
                        await db.commit()
                        await add_scores(code)

    # Leaderboard
    async with aiosqlite.connect(f"leaderboard.db") as db:
        async with db.execute(f"SELECT * FROM scores WHERE song='{song}' AND diff={diff}") as c:
            res = await c.fetchall()
            if len(res) == 0:
                await message.channel.send("> Erreur: Aucun score trouvé pour cette track")
                pass
            else:
                if diff == 3:
                    cover_url = cover + "3_" + song + ".jpg"
                else:
                    cover_url = cover + song + ".jpg"
                msg_emb = discord.Embed(title=f"Leaderboard | {songname} <{diff_l[diff]}>",
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
                await message.channel.send(embed=msg_emb)


async def add_scores(code):
    api_ = AsyncApi(user_code=code)
    data = await api_.scores()

    async with aiosqlite.connect(f"leaderboard.db") as db:
        for line in data[2:]:
            song = line["song_id"]
            diff = line["difficulty"]
            username = line["name"]
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
                    async with db.execute(f"UPDATE scores SET score={score} clear_type={clear_type} date='{date}' "
                                          f"WHERE id={res[0][0]}"):
                        await db.commit()
            else:
                params = (song, diff, username, score, stats, clear_type, date)
                async with db.execute(f"INSERT INTO scores VALUES "
                                      f"(NULL, ?, ?, ?, ?, ?, ?, ?)", params):
                    await db.commit()
