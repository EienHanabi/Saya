import json
import logging

import requests

from constants import api_url, headers, gsheet_webhook_url
from utils import check_id, query_songname, send_back_error, send_back_http_error

diff = ["PST", "PRS", "FTR", "BYD"]


async def event(message):
    code = await check_id(message.author.id)
    if not code:
        await message.channel.send("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    response_info = response_info = requests.post(f"{api_url}/user/info", headers=headers,
                                                  params={"usercode": code, "recent": 1}, timeout=180)
    if not response_info.ok:
        await send_back_http_error(message, response_info.status_code)
        return
    info_json = response_info.json()
    if info_json['status'] != 0:
        await send_back_error(message, info_json)
        return

    profile = info_json['content']
    recent = profile["recent_score"][0]

    recent["name"] = profile["name"]
    recent["song"] = f'{query_songname(recent["song_id"])}'
    recent["diff"] = f'{diff[recent["difficulty"]]}'
    logging.error(json.dumps(recent))
    response = requests.post(
        gsheet_webhook_url, data=json.dumps(recent),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to FRAG returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )
    else:
        await message.reply("Upload to FRAG done!")
