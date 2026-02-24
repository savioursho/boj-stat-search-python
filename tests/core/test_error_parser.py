from boj_stat_search.core.error_parser import BojErrorFields, parse_error_payload


def test_normal_payload():
    result = parse_error_payload({"STATUS": "100", "MESSAGEID": "E001", "MESSAGE": "Not found"})
    assert result == BojErrorFields(boj_status=100, message_id="E001", boj_message="Not found")


def test_empty_dict():
    result = parse_error_payload({})
    assert result == BojErrorFields(boj_status=None, message_id=None, boj_message=None)


def test_empty_string_status():
    result = parse_error_payload({"STATUS": "", "MESSAGEID": "E002", "MESSAGE": "Error"})
    assert result.boj_status is None
    assert result.message_id == "E002"
    assert result.boj_message == "Error"


def test_non_numeric_status():
    result = parse_error_payload({"STATUS": "abc"})
    assert result.boj_status is None


def test_numeric_string_status():
    result = parse_error_payload({"STATUS": "404"})
    assert result.boj_status == 404


def test_missing_messageid():
    result = parse_error_payload({"STATUS": "200", "MESSAGE": "OK"})
    assert result.message_id is None


def test_missing_message():
    result = parse_error_payload({"STATUS": "200", "MESSAGEID": "M01"})
    assert result.boj_message is None


def test_non_string_value_coercion():
    result = parse_error_payload({"STATUS": 500, "MESSAGEID": 42, "MESSAGE": 99})
    assert result.boj_status == 500
    assert result.message_id == "42"
    assert result.boj_message == "99"


def test_extra_keys_ignored():
    result = parse_error_payload(
        {"STATUS": "200", "MESSAGEID": "M01", "MESSAGE": "OK", "EXTRA": "ignored"}
    )
    assert result == BojErrorFields(boj_status=200, message_id="M01", boj_message="OK")


def test_none_status():
    result = parse_error_payload({"STATUS": None})
    assert result.boj_status is None


def test_empty_messageid_treated_as_none():
    result = parse_error_payload({"MESSAGEID": ""})
    assert result.message_id is None


def test_empty_message_treated_as_none():
    result = parse_error_payload({"MESSAGE": ""})
    assert result.boj_message is None
