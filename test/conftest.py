import os

import pytest
from unittest.mock import patch


@pytest.fixture
def environment():
    return {
        "IMAP_SERVER": "localhost",
        "EMAIL_ACCOUNT": "me@this.com",
        "EMAIL_PASS": "pa$$word",
    }


@pytest.fixture
def patch_env(environment):
    with patch.dict(os.environ, environment, clear=True):
        yield