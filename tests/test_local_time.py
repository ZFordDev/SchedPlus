from logic import local_time


def test_now_is_timezone_aware():
    assert local_time.now().utcoffset() is not None


def test_today_matches_local_now():
    assert local_time.today() == local_time.now().date()


def test_combine_preserves_local_wall_clock_values():
    combined = local_time.combine("2026-08-28", "14:35")

    assert (
        combined.year,
        combined.month,
        combined.day,
        combined.hour,
        combined.minute,
    ) == (2026, 8, 28, 14, 35)
    assert combined.utcoffset() is not None
