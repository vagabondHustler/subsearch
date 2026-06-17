from subsearch.io import json_file


def test_dump_json_data_is_atomic_and_leaves_no_temp_file(tmp_path):
    config_path = tmp_path / "config.json"
    temp_path = tmp_path / "config.json.tmp"

    json_file.dump_json_data(config_path, {"search": {"accept_threshold": 90}})

    assert config_path.exists()
    assert not temp_path.exists()
    assert json_file.load_json_data(config_path) == {"search": {"accept_threshold": 90}}
