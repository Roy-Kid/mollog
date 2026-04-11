from mollog.level import Level


def test_level_ordering():
    assert Level.TRACE < Level.DEBUG < Level.INFO < Level.WARNING < Level.ERROR < Level.CRITICAL


def test_level_values():
    assert Level.TRACE == 5
    assert Level.DEBUG == 10
    assert Level.INFO == 20
    assert Level.WARNING == 30
    assert Level.ERROR == 40
    assert Level.CRITICAL == 50


def test_level_str():
    assert str(Level.INFO) == "INFO"
    assert str(Level.CRITICAL) == "CRITICAL"


def test_level_comparison_with_int():
    assert Level.INFO > 15
    assert Level.WARNING >= 30


def test_level_coerce_from_string_and_int():
    assert Level.coerce("info") is Level.INFO
    assert Level.coerce(40) is Level.ERROR


def test_level_coerce_invalid_value():
    import pytest

    with pytest.raises(ValueError):
        Level.coerce("verbose")
