from discord import Embed, Message, channel


def convert_to_vx_twitter_url(embeds: list[Embed]):
    """
    Parameters
    ----------
    embeds: list of discord embeds

    Returns
    -------
        filtered list of twitter URLs that have been converted to vxtwitter
    """

    # pulls only video embeds from list of embeds
    urls = [entry.url for entry in embeds if entry.video]

    vxtwitter_urls = [
        result.replace("https://twitter.com", "https://vxtwitter.com")
        for result in urls
        if "https://twitter.com" in result
    ]

    return vxtwitter_urls


def urls_to_string(vx_twit_links: list[str]):
    """
    Parameters
    ----------
    vx_twit_links: list of urls

    Returns
    -------
        Formatted output
    """

    return "".join(
        [
            "OwO what's this?\n",
            "*notices your terrible twitter embeds*\n",
            "Here's a better alternative:\n",
            "\n".join(vx_twit_links),
        ]
    )


def valid(message: Message):
    """
    Parameters
    ----------
    message: Discord input message object

    Returns
    -------
        True if the message is from a human in a guild and contains video embeds
        False otherwise
    """

    # skips if the message is sent by any bot
    if message.author.bot:
        return False

    # skips if message is in dm
    if isinstance(message.channel, channel.DMChannel):
        return False

    # skips if the message has no embeds
    if not any(embed.video for embed in message.embeds):
        return False

    return True
