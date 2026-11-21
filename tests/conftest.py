from __future__ import annotations

import pandas as pd
import pytest

from g7kaih.data import load_dataset, load_meta


@pytest.fixture(scope="session")
def dataset() -> pd.DataFrame:
    return load_dataset()


@pytest.fixture(scope="session")
def meta() -> dict:
    return load_meta()
