from cloudutils.transforms import normalize_cols

def test_normalize_cols():
    assert normalize_cols([" A ", "b", "C c"]) == ["a", "b", "c_c"]
