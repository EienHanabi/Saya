import tweepy as tw
import random
import discord
import yaml


def get_keys():
    with open("config.yaml", "r", encoding="UTF-8") as f:
        return yaml.load("".join(f.readlines()), Loader=yaml.FullLoader)["tweepy"]


keys = get_keys()

auth = tw.OAuthHandler(keys["consumer_key"], keys["consumer_secret"])
auth.set_access_token(keys["access_token"], keys["access_token_secret"])

api = tw.API(auth, wait_on_rate_limit=True)


async def get_random_tweet(message):
    tweets = tw.Cursor(api.search, q="#arcaea_art filter:images min_faves:50", include_entities=True).items(100)
    ls_tweets = []

    for tweet in tweets:
        ls_tweets.append(tweet)
    rand = random.randint(0, len(ls_tweets))
    tweet = ls_tweets[rand]

    msg_emb = discord.Embed(title='Art', type='rich', color=discord.Color.dark_teal(), description=tweet.text)
    msg_emb.set_author(name=tweet.user.name, icon_url=tweet.user.profile_image_url)
    msg_emb.set_image(url=tweet.entities["media"][0]["media_url"])
    msg_emb.set_footer(text=f"Original tweet: https://twitter.com/twitter/statuses/{tweet.id}")
    msg_emb.add_field(name=":repeat:", value=tweet.retweet_count)
    msg_emb.add_field(name=":heart:", value=tweet.favorite_count)
    await message.reply(embed=msg_emb)
