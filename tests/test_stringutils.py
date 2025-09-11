from process_inspector.utils.stringutils import extract_version
from process_inspector.utils.stringutils import formatted_number
from process_inspector.utils.stringutils import formatted_percentage


def test_formatted_number_integer():
    assert formatted_number(1000) == "1,000"


def test_formatted_number_float():
    assert formatted_number(1234.56) == "1,234.56"


def test_formatted_number_zero():
    assert formatted_number(0) == "0"


def test_formatted_number_negative():
    assert formatted_number(-1000) == "-1,000"


def test_formatted_percentage_positive():
    assert formatted_percentage(12.3456) == "12.35%"


def test_formatted_percentage_zero():
    assert formatted_percentage(0) == "0.00%"


def test_formatted_percentage_negative():
    assert formatted_percentage(-12.3456) == "-12.35%"


def test_extract_version_found():
    assert extract_version("Version 1.2.3") == "1.2.3"
    assert extract_version("v1.2.3") == "1.2.3"


def test_extract_version_not_found():
    assert extract_version("No version here") == "--"


def test_extract_version_multiple_versions():
    assert extract_version("Version 1.2.3 and 4.5.6") == "1.2.3"


def test_extract_version_empty_string():
    assert extract_version("") == "--"


def test_extract_version_version_at_start():
    assert extract_version("1.2.3 is the version") == "1.2.3"


def test_extract_version_version_at_end():
    assert extract_version("The version is 1.2.3") == "1.2.3"
