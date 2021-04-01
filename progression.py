import matplotlib.pyplot as plt
import discord
import io

from datetime import datetime
from Arcapi import AsyncApi

from utils import check_id

plt.rcParams['text.color'] = "white"
plt.rcParams['axes.labelcolor'] = "white"
plt.rcParams['xtick.color'] = "white"
plt.rcParams['ytick.color'] = "white"


async def progression(message):
    code = await check_id(message.author.id)
    if not code:
        await message.channel.send("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    api_ = AsyncApi(user_code=code)
    data = await api_.scores()
    prfl = data[1]
    recs = prfl['rating_records']

    dates = [datetime.strptime(rec[0], '%y%m%d').date() for rec in recs]
    ptts = [float(rec[1]) / 100 for rec in recs]

    plt.rc('axes', edgecolor='white')
    fig, ax = plt.subplots()
    fig.patch.set_facecolor('#36393F')
    ax.set_facecolor('#36393F')
    ax.set_xlabel("Time")
    ax.set_ylabel("PTT")
    ax.set_title(f"{message.author.name}'s PTT progression")
    ax.plot_date(dates, ptts, fmt='-', color='#439EBA')
    fig.autofmt_xdate()
    b = io.BytesIO()
    plt.savefig(b, format='png')
    plt.close()
    b.seek(0)
    file = discord.File(b, f"progression.png")
    await message.channel.send(file=file)
