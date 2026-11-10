import json

import pytest

from amsha.output_process.optimization.json_cleaner_utils import JsonCleanerUtils


@pytest.mark.parametrize("value", [{}, [], False, 0, None, ""])
def test_falsy_json_round_trips_without_overwriting_source(tmp_path, value):
    source = tmp_path / "source.json"
    source.write_text(json.dumps(value), encoding="utf-8")
    cleaner = JsonCleanerUtils(str(source))
    assert cleaner.process_file() is True
    assert cleaner.output_file_path != source
    assert json.loads(cleaner.output_file_path.read_text(encoding="utf-8")) == value
    assert json.loads(source.read_text(encoding="utf-8")) == value


def test_invalid_json_does_not_write_output(tmp_path):
    source = tmp_path / "invalid.json"
    source.write_text("{invalid", encoding="utf-8")
    cleaner = JsonCleanerUtils(str(source))
    assert cleaner.process_file() is False
    assert not cleaner.output_file_path.exists()
