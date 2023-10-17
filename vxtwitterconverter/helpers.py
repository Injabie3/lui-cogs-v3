import re

from discord import Embed, Message, channel

from .constants import INSTA_REGEX_MATCH, SocialMedia


def convert_to_ddinsta_url(embeds: list[Embed]):
    """
    Parameters
    ----------
    embeds: list of discord embeds

    Returns
    -------
        filtered list of Instagram URLs that have been converted to ddinstagram
    """

    # pulls only video embeds from list of embeds
    urls = [entry.url for entry in embeds]

    ddinsta_urls = [
        re.sub(INSTA_REGEX_MATCH, r"https://dd\1", result)
        for result in urls
        if re.match(INSTA_REGEX_MATCH, result)
    ]

    return ddinsta_urls


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


def urls_to_string(links: list[str], socialMedia: SocialMedia):
    """
    Parameters
    ----------
    links: List[str]
        A list of urls
    socialMedia: SocialMedia
        The social media to replace.

    Returns
    -------
        Formatted output
    """
    return "".join(
        [
            "OwO what's this?\n",
            f"*notices your terrible {socialMedia.value} embeds*\n",
            "Here's a better alternative:\n",
            "\n".join(links),
        ]
    )


def valid(message: Message):
    """
    Parameters
    ----------
    message: Discord input message object

    Returns
    -------
        True if the message is from a human in a guild and contains embeds
        False otherwise
    """

    # skips if the message is sent by any bot
    if message.author.bot:
        return False

    # skips if message is in dm
    if isinstance(message.channel, channel.DMChannel):
        return False

    # skips if the message has no embeds
    if not message.embeds:
        return False

    return True
