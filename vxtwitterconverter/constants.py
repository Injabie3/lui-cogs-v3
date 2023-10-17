import enum

KEY_ENABLED = "enabled"
DEFAULT_GUILD = {KEY_ENABLED: False}
INSTA_REGEX_MATCH = r"https://(?:www\.)?(instagram.com)"


class SocialMedia(enum.Enum):
    INSTAGRAM = "Instagram"
    TWITTER = "Twitter"
