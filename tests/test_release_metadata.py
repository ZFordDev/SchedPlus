from scripts.validate_release_metadata import validate


def test_release_metadata_is_complete_and_consistent():
    assert validate() == []
