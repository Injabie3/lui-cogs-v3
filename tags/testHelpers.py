import random

import pytest

from . import constants, helpers


class Utils:
    @classmethod
    def randomNumberString(cls, len: int, digits: str = "0123456789"):
        """Returns a string of specified length and of specified digits chosen randomly."""
        return "".join(random.choice(digits) for _ in range(len))

    @classmethod
    def insertStringIntoString(cls, str1: str, str2: str, pos: int):
        """Returns the result of inserting str1 into str2 at position pos."""
        return "".join((str2[:pos], str1, str2[pos:]))


class TestCheckLengthInRaw:
    """Tests to ensure helper checkLengthInRaw() works as expected."""

    # good cases
    @pytest.mark.parametrize(
        ["content"],
        map(
            lambda content: [content],
            (
                "",
                "**test**",
                "~~**__`test`__**~~",
                "~~**__```test```__**~~",
                Utils.randomNumberString(constants.MAX_MSG_LEN),
                Utils.randomNumberString(constants.MAX_MSG_LEN - 4) + "test",
                Utils.randomNumberString(constants.MAX_MSG_LEN - 12) + "**test**",
                Utils.randomNumberString(constants.MAX_MSG_LEN - 32) + "~~**__`test`__**~~",
                Utils.randomNumberString(constants.MAX_MSG_LEN - 64) + "~~**__`test`__**~~",
                Utils.randomNumberString(constants.MAX_MSG_LEN - 40) + "~~**__```test```__**~~",
                Utils.randomNumberString(constants.MAX_MSG_LEN - 64) + "~~**__```test```__**~~",
                # cases with non-effective block-quotes
                Utils.randomNumberString(constants.MAX_MSG_LEN - 42) + ">~~**__```test```__**~~<",
                Utils.randomNumberString(constants.MAX_MSG_LEN - 46)
                + ">>>~~**__```test```__**~~<<<",
                # cases with effective block-quotes
                "> ~~**__```test```__**~~ <"
                + Utils.randomNumberString(constants.MAX_MSG_LEN - 45),
                ">>> ~~**__```test```__**~~ <<<"
                + Utils.randomNumberString(constants.MAX_MSG_LEN - 49),
                # cases with non-ASCII characters
                Utils.insertStringIntoString(
                    "~*_`ネコミミ大好き`_*~",
                    Utils.randomNumberString(constants.MAX_MSG_LEN - 23),
                    random.randint(0, constants.MAX_MSG_LEN - 23),
                ),
                Utils.insertStringIntoString(
                    "~*_`ねこみみだいすき`_*~",
                    Utils.randomNumberString(constants.MAX_MSG_LEN - 24),
                    random.randint(0, constants.MAX_MSG_LEN - 24),
                ),
                # cases with markdown-lookalike characters
                Utils.insertStringIntoString(
                    "~*_`バーバラ☆いっくよ！～`_*~",
                    Utils.randomNumberString(constants.MAX_MSG_LEN - 27),
                    random.randint(0, constants.MAX_MSG_LEN - 27),
                ),
                # cases with markdown effective block-quote lookalike characters
                Utils.insertStringIntoString(
                    "＞＞ ~*_`バーバラ☆いっくよ！～`_*~ ＜＜",
                    Utils.randomNumberString(constants.MAX_MSG_LEN - 33),
                    random.randint(0, constants.MAX_MSG_LEN - 33),
                ),
            ),
        ),
    )
    def testGoodCases(self, content: str):
        assert helpers.checkLengthInRaw(content) == True

    # bad cases
    @pytest.mark.parametrize(
        ["content"],
        map(
            lambda content: [content],
            (
                Utils.randomNumberString(constants.MAX_MSG_LEN * 2),
                Utils.randomNumberString(constants.MAX_MSG_LEN + 1),
                Utils.randomNumberString(constants.MAX_MSG_LEN - 8) + "**test**",
                Utils.randomNumberString(constants.MAX_MSG_LEN - 10) + "**test**",
                Utils.randomNumberString(constants.MAX_MSG_LEN - 11) + "**test**",
                Utils.randomNumberString(constants.MAX_MSG_LEN - 14) + "~~**__`test`__**~~",
                Utils.randomNumberString(constants.MAX_MSG_LEN - 31) + "~~**__`test`__**~~",
                Utils.randomNumberString(constants.MAX_MSG_LEN - 20) + "~~**__```test```__**~~",
                Utils.randomNumberString(constants.MAX_MSG_LEN - 39) + "~~**__```test```__**~~",
                # cases with non-effective block-quotes
                Utils.randomNumberString(constants.MAX_MSG_LEN - 41) + ">~~**__```test```__**~~<",
                Utils.randomNumberString(constants.MAX_MSG_LEN - 45)
                + ">>>~~**__```test```__**~~<<<",
                # cases with effective block-quotes
                "> ~~**__```test```__**~~ <"
                + Utils.randomNumberString(constants.MAX_MSG_LEN - 44),
                ">>> ~~**__```test```__**~~ <<<"
                + Utils.randomNumberString(constants.MAX_MSG_LEN - 48),
                # cases with non-ASCII characters
                Utils.insertStringIntoString(
                    "~*_`ネコミミ大好き`_*~",
                    Utils.randomNumberString(constants.MAX_MSG_LEN - 22),
                    random.randint(0, constants.MAX_MSG_LEN - 22),
                ),
                Utils.insertStringIntoString(
                    "~*_`ねこみみだいすき`_*~",
                    Utils.randomNumberString(constants.MAX_MSG_LEN - 23),
                    random.randint(0, constants.MAX_MSG_LEN - 23),
                ),
                # cases with markdown-lookalike characters
                Utils.insertStringIntoString(
                    "~*_`バーバラ☆いっくよ！～`_*~",
                    Utils.randomNumberString(constants.MAX_MSG_LEN - 26),
                    random.randint(0, constants.MAX_MSG_LEN - 26),
                ),
                # cases with markdown effective block-quote lookalike characters
                Utils.insertStringIntoString(
                    "＞＞ ~*_`バーバラ☆いっくよ！～`_*~ ＜＜",
                    Utils.randomNumberString(constants.MAX_MSG_LEN - 32),
                    random.randint(0, constants.MAX_MSG_LEN - 32),
                ),
            ),
        ),
    )
    def testBadCases(self, content: str):
        assert helpers.checkLengthInRaw(content) == False
