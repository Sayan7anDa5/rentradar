"""Shared helpers for RentRadar. Imported by the modeling notebook and the app
so the locality-bucketing rule lives in exactly one place."""

import pandas as pd


def bucket_localities(localities: pd.Series, known) -> pd.Series:
    """Map any locality not in `known` to "Other".

    `known` is the list of localities that have enough listings to keep their
    own column (count >= 10 in the training split). Rare localities collapse to
    a single "Other" bucket. `city` is a separate feature, so a global "Other"
    is enough — the model learns the Other x city interaction.
    """
    known_set = set(known)
    return localities.where(localities.isin(known_set), "Other")
