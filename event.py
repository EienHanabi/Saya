from funct import check_id
from Arcapi import AsyncApi
import csv


diff = ["PST", "PRS", "FTR", "BYD"]


async def event(message):
    with open("test.csv", "r", encoding="UTF-8") as f:
        cf = csv.reader(f, delimiter=';')
        dat = []
        for elm in cf:
            dat.append(elm)

    code = await check_id(message.author.id)
    if not code:
        await message.channel.send("> Erreur: Aucun code Arcaea n'est lié a ce compte Discord (*!register*)")
        return

    api_ = AsyncApi(user_code=code)
    data = await api_.songs()
    songlist = data[0]
    prfl = data[1]
    recent = prfl["recent_score"][0]

    mode = dat[0][1]
    song = songlist[recent["song_id"]]["en"]
    dif = diff[recent["difficulty"]]

    if mode == "score":
        res = recent["score"]

    elif mode == "pures":
        res = recent["perfect_count"]

    elif mode == "ppures":
        res = recent["shiny_perfect_count"]

    else:
        await message.channel.send("> ERREUR: Aucun event en cours")
        return

    e_songs = []
    e_players = [elm[1] for elm in dat[2:]]
    for elm in dat[1][3:]:
        if elm.split("|")[0] not in e_songs:
            e_songs.append(elm)

    if f"{song}|{dif}" in e_songs:
        e_ind = e_songs.index(f"{song}|{dif}") + 3
        p_line = e_players.index(str(message.author.id)) + 2
        if dat[p_line][e_ind] != "X":
            if int(dat[p_line][e_ind]) < res:
                dat[p_line][e_ind] = res

                with open('test.csv', 'w', newline='', encoding="UTF-8") as f:
                    cf = csv.writer(f, delimiter=';')
                    for elm in dat:
                        cf.writerow(elm)

                await message.channel.send(f"> INFO: Envoi du score reussi\n"
                                           f"> Score de {song} <{dif}> modifié en {res}")

            else:
                await message.channel.send("> ERREUR: Le score est inferieur au resultat précédent")
                return
        else:
            await message.channel.send("> ERREUR: La difficulté de cette track ne fait pas partie de l'event en cours")
            return
    else:
        await message.channel.send("> ERREUR: La track ne fait pas partie de l'event en cours")
        return




