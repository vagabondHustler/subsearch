from subsearch.io import nested_dict


def test_nested_value_read_set_delete():
    data = {"search": {"accept_threshold": 90}}

    assert nested_dict.read_nested_value(data, "search.accept_threshold") == 90

    nested_dict.set_nested_value(data, "search.accept_threshold", 50)
    assert data["search"]["accept_threshold"] == 50

    nested_dict.delete_nested_value(data, "search.accept_threshold")
    assert "accept_threshold" not in data["search"]


def test_delete_nested_value_with_missing_parent_does_not_raise():
    nested_dict.delete_nested_value({}, "missing.parent.leaf")


def test_read_nested_value_with_missing_parent_returns_none():
    assert nested_dict.read_nested_value({}, "missing.parent.leaf") is None
