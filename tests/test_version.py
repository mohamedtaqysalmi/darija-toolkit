import re

import darija_toolkit


def test_version_is_semver_string() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", darija_toolkit.__version__)
