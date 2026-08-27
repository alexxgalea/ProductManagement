def test_deliberately_fails():
    raise AssertionError("intentional failure to prove branch protection blocks a red PR")
