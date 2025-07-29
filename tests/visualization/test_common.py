from geqo.visualization.common import valid_name, valid_angle
import pytest


class TestCommon:
    def test_valid_name(self):
        with pytest.raises(
            TypeError,
            match="Gate/Sequence name must be a string.",
        ):
            valid_name(1)
        with pytest.raises(
            ValueError,
            match="Gate/Sequence names with 2 or more capital letters can have at most 3 letters in total. \n Gate names with fewer than 2 capital letters can have at most 4 letters in total.",
        ):
            valid_name("abcde")
        with pytest.raises(
            ValueError,
            match="Gate/Sequence names with 2 or more capital letters can have at most 3 letters in total. \n Gate names with fewer than 2 capital letters can have at most 4 letters in total.",
        ):
            valid_name("ABcd")

    def test_valid_angle(self):
        with pytest.raises(
            TypeError,
            match="Phase placeholder must be a string.",
        ):
            valid_angle(1)

        valid_angle("a", non_pccm=False)
