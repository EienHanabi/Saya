# Display help
async def get_help(message):
    await message.reply("**Help:**\n"
                               "> !art: Displays a random art tweet\n"
                               "> !best [1-30]: Sends the Top [1-30] plays (Default: 30)\n"
                               "> !help: Sends this message\n"
                               "> !profile: Displays the user profile\n"
                               "> !rec [1-20]: Sends [1-20] recommended plays to increase PTT (Default: 5)\n"
                               "> !session [args]: Generates a personalized Arcaea session (Example : !session 8 4 9 2 9+ 1)\n"
                               "> !leaderboard [song] [diff]: Sends the leaderboard for the selected song (Updates every 7 days)\n"
                               "> !recent: Sends the latest play\n"
                               "> !prog: Generates a PTT evolution graph\n"
                               "> !pog: Sends a Pog in the chat\n"
                               "> !score [song] [diff] : Returns your best score on the selected song\n" 
                               "> !register: Links a user code to a Discord account")
