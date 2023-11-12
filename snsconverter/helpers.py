import re

from discord import Embed, Message, channel

from .constants import (
    INSTA_REGEX_PATTERN,
    REDDIT_REGEX_PATTERN,
    THREADS_REGEX_PATTERN,
    TIKTOK_REGEX_PATTERN,
    TWITTER_REGEX_PATTERN,
    X_REGEX_PATTERN,
    SocialMedia,
)


def convert_to_ddinsta_url(embeds: list[Embed]):
    """
    Parameters
    ----------
    embeds: list of Discord embeds

    Returns
    -------
        filtered list of Instagram URLs that have been converted to ddinstagram
    """

    # pulls only video embeds from list of embeds
    urls = [entry.url for entry in embeds]

    ddinsta_urls = [
        re.sub(INSTA_REGEX_PATTERN, r"https://dd\1", result)
        for result in urls
        if re.match(INSTA_REGEX_PATTERN, result)
    ]

    return ddinsta_urls


def convert_to_vx_tiktok_url(embeds: list[Embed]):
    """
    Parameters
    ----------
    embeds: list of Discord embeds

    Returns
    -------
        filtered list of TikTok URLs that have been converted to vxtiktok
    """

    # pulls only video embeds from list of embeds
    urls = [entry.url for entry in embeds]

    vxtiktok_urls = [
        re.sub(TIKTOK_REGEX_PATTERN, r"https://\1vx\2", result)
        for result in urls
        if re.match(TIKTOK_REGEX_PATTERN, result)
    ]

    return vxtiktok_urls


def convert_to_fx_twitter_url(message_content: str):
    """
    Parameters
    ----------
    message_content: str

    Returns
    -------
        filtered list of twitter/x URLs that have been converted to fxtwitter/fixupx
    """

    message_split = message_content.split()

    fixed_urls = []

    for word in message_split:
        # I don't think @everyone will work anyway, but just incase...
        if "@" in word:
            continue
        elif re.match(TWITTER_REGEX_PATTERN, word):
            fixed_urls.append(
                re.sub(TWITTER_REGEX_PATTERN, r"https://fxtwitter.com\1", word)
            )
        elif re.match(X_REGEX_PATTERN, word):
            fixed_urls.append(re.sub(X_REGEX_PATTERN, r"https://fixupx.com\1", word))

    return fixed_urls


def convert_to_rxddit_url(embeds: list[Embed]):
    """
    Parameters
    ----------
    embeds: list of Discord embeds

    Returns
    -------
        filtered list of Reddit URLs that have been converted to rxddit
    """

    # pulls only video embeds from list of embeds
    urls = [entry.url for entry in embeds]

    rxddit_urls = [
        re.sub(REDDIT_REGEX_PATTERN, r"https://rxddit.com", result)
        for result in urls
        if re.match(REDDIT_REGEX_PATTERN, result)
    ]

    return rxddit_urls


def convert_to_vx_threads_url(embeds: list[Embed]):
    """
    Parameters
    ----------
    embeds: list of Discord embeds

    Returns
    -------
        filtered list of Threads URLs that have been converted to vxthreads
    """

    # pulls only video embeds from list of embeds
    urls = [entry.url for entry in embeds]

    vxthreads_urls = [
        re.sub(THREADS_REGEX_PATTERN, r"https://vx\1", result)
        for result in urls
        if re.match(THREADS_REGEX_PATTERN, result)
    ]

    return vxthreads_urls


def urls_to_string(links: list[str], socialMedia: SocialMedia):
    """
    Parameters
    ----------
    links: list[str]
        A list of urls
    socialMedia: SocialMedia
        The social media to replace.

    Returns
    -------
        Formatted output
    """
    return "\n".join(
        [
            "OwO what's this?",
            f"*fixes your {socialMedia.value} embeds:*",
            *links,
        ]
    )


def valid(message: Message):
    """
    Parameters
    ----------
    message: Discord input message object

    Returns
    -------
        True if the message is from a human in a guild
        False otherwise
    """

    # skips if the message is sent by any bot
    if message.author.bot:
        return False

    # skips if message is in dm
    if isinstance(message.channel, channel.DMChannel):
        return False
    return True
