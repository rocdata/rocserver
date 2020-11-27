
import pytest

import uuid

from standards.utils import generate_short_uuid
from standards.utils import uuid_to_short_code
from standards.utils import short_code_to_uuid


def test_convert_uuid_to_short_code():
    input = uuid.UUID('00000000-0000-0000-0000-00e1c270ce13')
    expected_short_code = 'WHWo4hY'
    observed_short_code = uuid_to_short_code(input)
    assert observed_short_code == expected_short_code, 'unexpected conversion of uuid to short code'


def test_convert_short_code_to_uuid():
    expected = uuid.UUID('00000000-0000-0000-0000-00e1c270ce13')
    observed = short_code_to_uuid('WHWo4hY')
    assert observed == expected, 'unexpected decoding of short code'


def test_conversions_together():
    u = generate_short_uuid()
    short_code = uuid_to_short_code(u)
    u2 = short_code_to_uuid(short_code)
    assert u == u2, 'roundrip uuid-->short_code-->uuid failed'
