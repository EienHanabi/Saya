from utils import check_id, format_score
from Arcapi import AsyncApi
import discord
import json
import requests
import logging

from utils import check_id

diff = ["PST", "PRS", "FTR", "BYD"]

async def event(message):
    code = await check_id(message.author.id)
    if not code:
        await message.channel.send("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    api_ = AsyncApi(user_code=code)
    data = await api_.songs()
    songlist = data[0]
    prfl = data[1]
    recent = prfl["recent_score"][0]

    recent["name"] = prfl["name"]
    recent["song"] = f'{songlist[recent["song_id"]]["en"]}'
    recent["diff"] = f'{diff[recent["difficulty"]]}'
    webhook_url = 'https://script.google.com/macros/s/AKfycbxGTTjt12J1HmD1B1RaiNTZuIc3ZoFlIvafFAdEtuN7ewCQ-YQVnkUEOb23d3iXQ9I0CQ/exec'
    logging.error(json.dumps(recent))
    response = requests.post(
        webhook_url, data=json.dumps(recent),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to FRAG returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )
#    else:
#        msg_emb = discord.Embed(title=f'Test', type="rich", color=discord.Color.dark_teal())
#        msg_emb.add_field(name=f'Test',
#                          value=f'{response.text}')
#        msg_emb = discord.Embed(title=f'Score FRAG - {prfl["name"]}', type="rich", color=discord.Color.dark_teal())
#        msg_emb.add_field(name=f'{recent["song"]}',
#                          value=f'> Score: {format_score(recent["score"])}\n'
#                                f'> Pure: {recent["perfect_count"]} ({recent["shiny_perfect_count"]}) \n'
#                                f'> Far: {recent["near_count"]} |  Lost: {recent["miss_count"]}')
#        await message.channel.send(embed=msg_emb)


