IGNORE_PATTERNS = [
    "id",
    "_id",
    "index",
    "unnamed",
    "row",
    "customerid"
]


def is_meaningful_column(col):

    col = str(col).lower()

    return not any(
        bad in col
        for bad in IGNORE_PATTERNS
    )