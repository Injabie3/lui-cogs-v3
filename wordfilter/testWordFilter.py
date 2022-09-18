import pytest
from .wordfilter import (
    _censorMatch,
    _isAllFiltered,
    _isOneWord,
)
import re


class TestHelperFunctions:
    @pytest.mark.parametrize(
        ["inputPhrase", "toFilter", "result"],
        [
            ("I am cool", "am", "I `**` cool"),
            (
                "https://discord.gg/testing123",
                r"(discord.gg\/)(?!YcW3AtX)(?!MmpqtqD)[a-z,A-Z,0-9]*",
                "https://`*********************`",
            ),
            (
                "https://discord.gg/YcW3AtX",
                r"(discord.gg\/)(?!YcW3AtX)(?!MmpqtqD)[a-z,A-Z,0-9]*",
                "https://discord.gg/YcW3AtX",
            ),
        ],
    )
    def testCensorMatch(self, inputPhrase, toFilter, result):
        filteredPhrase = re.sub(toFilter, _censorMatch, inputPhrase, flags=re.IGNORECASE)
        assert result == filteredPhrase

    @pytest.mark.parametrize(
        ["inputStr", "result"],
        [
            ("test", True),
            ("another phrase", False),
        ],
    )
    def testIsOneWord(self, inputStr, result):
        assert _isOneWord(inputStr) == result

    @pytest.mark.parametrize(
        ["inputStr", "result"],
        [
            ("test", False),
            ("***** phrase", False),
            ("**** **another** **phrase**", False),
            ("F*CKING B*LLSH*T", False),
            ("* ** ***", True),
            (" *** **** ", True),
            ("**** ** ****", True),
        ],
    )
    def testIsAllFiltered(self, inputStr, result):
        assert _isAllFiltered(inputStr) == result
