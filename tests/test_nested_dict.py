from subsearch.runtime.config import nested_dict


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


def test_changed_leaves_carries_old_and_new_value():
    assert nested_dict.changed_leaves("a.b", 90, 50) == [("a.b", 90, 50)]


def test_changed_leaves_walks_nested_dicts():
    previous = {"search": {"accept_threshold": 90, "language": "en"}}
    new = {"search": {"accept_threshold": 50, "language": "en"}}

    assert nested_dict.changed_leaves("config", previous, new) == [("config.search.accept_threshold", 90, 50)]


def test_changed_leaves_returns_empty_when_unchanged():
    assert nested_dict.changed_leaves("a.b", 90, 90) == []
