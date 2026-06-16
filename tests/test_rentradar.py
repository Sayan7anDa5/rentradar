import pandas as pd
from rentradar import bucket_localities


def test_known_locality_is_kept():
    s = pd.Series(["Kharadi", "Wagholi"])
    known = ["Kharadi", "Wagholi"]
    result = bucket_localities(s, known)
    assert list(result) == ["Kharadi", "Wagholi"]


def test_unknown_locality_becomes_other():
    s = pd.Series(["Kharadi", "ObscureNagar"])
    known = ["Kharadi"]
    result = bucket_localities(s, known)
    assert list(result) == ["Kharadi", "Other"]


def test_all_unknown_all_other():
    s = pd.Series(["A", "B", "C"])
    result = bucket_localities(s, [])
    assert list(result) == ["Other", "Other", "Other"]


def test_returns_series_same_index():
    s = pd.Series(["Kharadi", "X"], index=[10, 20])
    result = bucket_localities(s, ["Kharadi"])
    assert list(result.index) == [10, 20]
