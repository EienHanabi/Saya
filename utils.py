import aiosqlite
import time
import math

from operator import itemgetter
from datetime import datetime, timedelta

from constants import partners, songlist


async def check_id(id):
    async with aiosqlite.connect(f"players.db") as db:
        async with db.execute(f"SELECT * FROM players WHERE discord_id = {id}") as c:
            res = await c.fetchall()
            if len(res) != 0:
                return str("{0:09d}").format(res[0][1])
            else:
                return None


async def send_back_error(message, json):
    await message.reply(f"Error, status: {json['status']}, message: {json['message']}")
    return


# Format score as 00'000'000
def format_score(score):
    return "{0:08d}".format(score)[:2] + "'" + "{0:08d}".format(score)[2:5] + "'" + "{0:08d}".format(score)[5:]


# Format player code as 000 000 000
def format_code(code):
    return code[:3] + " " + code[3:6] + " " + code[6:]


# Get song difficulty based on PTT (Is incorrect for Moonheart BYD)
def get_diff(cst):
    if 9.6 < cst < 11:
        if cst < 10:
            return "9+"
        elif cst < 10.6:
            return "10"
        else:
            return "10+"
    else:
        return str(cst).split(".")[0]


# Get URL asset for Partner icon
def get_partner_icon(prfl):
    if prfl["is_char_uncapped"]:
        return partners + str(prfl["character"]) + "u_icon.png"
    else:
        return partners + str(prfl["character"]) + "_icon.png"


# Format time; Arcapi returns a delta from current time instead of EPOCH
def format_time(ts):
    sec = int(time.time() - ts / 1000)
    days = int(sec / 86400)
    hours = int(sec % 86400 / 3600)
    minutes = int(sec % 86400 % 3600 / 60)
    seconds = int(sec % 86400 % 3600 % 60)

    res = datetime.today() - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    return res.strftime("%d/%m/%Y - %H:%M")


# Return nb_scores recommendations based on given scores/profile, doesn't display anything
def get_ptt_recommendation_scores(scores, prfl, nb_scores):
    ptt_rec = []
    PTT = float(prfl["rating"]) / 100

    scores = sorted(scores, key=itemgetter("rating"), reverse=True)
    # Divides scores between top 30 and scores below
    scores_top_30 = scores[0:30]
    last_top_30 = scores_top_30[-1]
    scores_others = scores[30:]
    scores_others_2 = scores_others
    # Removes PMs
    scores_top_30 = filter(lambda scores: scores["score"] < 10000000, scores_top_30)
    scores_others = list(filter(lambda scores: scores["score"] < 10000000, scores_others))

    half_nb_scores = math.floor(nb_scores / 2)
    # Max 1/4 recommendations : Oldest scores not in top 30 with Chart Constant > PTT - 1
    filtered_scores = filter(
        lambda scores: query_constant(scores) > PTT - 1 and scores["rating"] > last_top_30["rating"] - 1, scores_others)
    ptt_rec += sorted(filtered_scores, key=itemgetter("time_played"), reverse=False)[
               0:int(math.ceil(half_nb_scores / 2))]
    # Max 1/4 recommendations : Oldest scores not in top 30 with PTT - 1 >= Chart Constant > PTT - 2
    filtered_scores = filter(
        lambda scores: PTT - 1 >= query_constant(scores) > last_top_30["rating"] - 2 and scores["rating"] > last_top_30[
            "rating"] - 1, scores_others)
    ptt_rec += sorted(filtered_scores, key=itemgetter("time_played"), reverse=False)[
               0:int(math.floor(half_nb_scores / 2))]
    # Rest of recommendations : Oldest scores from top 30
    ptt_rec += sorted(scores_top_30, key=itemgetter("time_played"), reverse=False)[0:nb_scores - len(ptt_rec)]
    # Sort by time_played
    ptt_rec = sorted(ptt_rec, key=itemgetter("time_played"), reverse=False)
    return ptt_rec


def query_songname(songid):
    for i in songlist['songs']:
        if i['id'] == songid:
            return i['title_localized']['en']


def query_constant(json_entry):
    for i in songlist['songs']:
        if json_entry['song_id'] == i['id']:
            return i['difficulties'][json_entry['difficulty']]['fixedValue']
