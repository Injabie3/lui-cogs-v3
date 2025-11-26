import enum
import re

KEY_ENABLED = "enabled"
DEFAULT_GUILD = {KEY_ENABLED: False}
INSTA_REGEX_PATTERN = re.compile(r"http(?:s)?://(?:www\.)?(instagram\.com)")
TIKTOK_REGEX_PATTERN = re.compile(r"http(?:s)?://(www\.|vm\.)?(tiktok\.com)")
TWITTER_REGEX_PATTERN = re.compile(
    r"http(?:s)?://(?:www\.)?twitter\.com(/[^/]+/status/\d+)"
)
X_REGEX_PATTERN = re.compile(r"http(?:s)?://(?:www\.)?x\.com(/[^/]+/status/\d+)")
# Match any reddit subdomain, too many to list (old, np, de, us, etc)
REDDIT_REGEX_PATTERN = re.compile(r"http(?:s)?://(?:[\w-]+?\.)?reddit\.com")
THREADS_REGEX_PATTERN = re.compile(r"http(?:s)?://(?:www\.)?(threads\.net)")


class SocialMedia(enum.Enum):
    INSTAGRAM = "Instagram"
    # I'm not calling it f****ng "x" lol
    TWITTER = "Twitter"
    TIKTOK = "TikTok"
    REDDIT = "Reddit"
    THREADS = "Threads"
