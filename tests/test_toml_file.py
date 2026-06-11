from subsearch.io import toml_file


def test_dump_toml_data_is_atomic_and_leaves_no_temp_file(tmp_path):
    config_path = tmp_path / "config.toml"
    temp_path = tmp_path / "config.toml.tmp"

    toml_file.dump_toml_data(config_path, {"search": {"accept_threshold": 90}})

    assert config_path.exists()
    assert not temp_path.exists()
    assert toml_file.load_toml_data(config_path) == {"search": {"accept_threshold": 90}}
