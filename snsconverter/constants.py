import enum
import re

KEY_ENABLED = "enabled"
DEFAULT_GUILD = {KEY_ENABLED: False}
INSTA_REGEX_PATTERN = re.compile(r"https://(?:www\.)?(instagram.com)")
TIKTOK_REGEX_PATTERN = re.compile(r"https://(www\.|vm\.)?(tiktok.com)")
TWITTER_REGEX_PATTERN = re.compile(r"https://(?:www\.|)twitter\.com(/[^/]+/status/\d+)")
X_REGEX_PATTERN = re.compile(r"https://(?:www\.|)x\.com(/[^/]+/status/\d+)")


class SocialMedia(enum.Enum):
    INSTAGRAM = "Instagram"
    # I'm not calling it f****ng "x" lol
    TWITTER = "Twitter"
    TIKTOK = "TikTok"
