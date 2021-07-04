import aiosqlite


async def register(message):
    code = None
    if len(message.content.split(" ")) == 2:
        if len(message.content.split(" ")[1]) == 9 and message.content.split(" ")[1].isdigit():
            code = message.content.split(" ")[1]

    elif len(message.content.split(" ")) < 2:
        if len("".join(message.content.split(" ")[1:])) == 9 and "".join(message.content.split(" ")[1:].isdigit()):
            code = "".join(message.content.split(" ")[1:])

    if code:
        async with aiosqlite.connect(f"players.db") as db:
            async with db.execute(f"SELECT * FROM players WHERE discord_id = {message.author.id}") as c:
                if len(await c.fetchall()) == 0:
                    async with db.execute(f"INSERT INTO players (discord_id, arc_id) VALUES "
                                          f"('{message.author.id}', '{code}')"):
                        await db.commit()
                    await message.channel.send("> INFO: Code ajouté a la base de données")
                    return
                else:
                    async with db.execute(f"UPDATE players SET arc_id = '{code}' "
                                          f"WHERE discord_id = '{message.author.id}'"):
                        await db.commit()
                    await message.channel.send("> INFO: Code mis à jour la base de données")
                    return

    else:
        await message.channel.send("> ERREUR: Le format du code est incorrect")
        return
