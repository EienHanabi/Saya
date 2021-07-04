import json
import logging

import requests
from ArcProbeInterface import AsyncAPI

from utils import check_id

diff = ["PST", "PRS", "FTR", "BYD"]


async def event(message):
    code = await check_id(message.author.id)
    if not code:
        await message.channel.send("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    api_ = AsyncAPI(user_code=code)
    data = await api_.fetch_data()
    songlist = data['songtitle']
    prfl = data['userinfo']
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
