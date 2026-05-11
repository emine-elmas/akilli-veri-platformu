from ..core.text import normalize


SEMANTIC_PATTERNS = {

    "identifier": [
        "id",
        "uuid",
        "index",
        "customerid",
        "userid",
        "orderid"
    ],

    "datetime": [
        "date",
        "time",
        "year",
        "month",
        "day",
        "createdat"
    ],

    "revenue": [
        "sales",
        "revenue",
        "income",
        "profit",
        "amount",
        "price"
    ],

    "quantity": [
        "quantity",
        "count",
        "units",
        "orders"
    ],

    "geography": [
        "city",
        "country",
        "region",
        "state"
    ],

    "person": [
        "customer",
        "user",
        "employee",
        "client"
    ],

    "product": [
        "product",
        "item",
        "category",
        "brand"
    ],

    "health": [
        "heart",
        "pulse",
        "calorie",
        "weight",
        "height",
        "bmi"
    ]
}


def detect_semantic_type(column_name):

    col = normalize(column_name)

    for semantic_type, patterns in SEMANTIC_PATTERNS.items():

        for pattern in patterns:

            if pattern in col:
                return semantic_type

    return "unknown"