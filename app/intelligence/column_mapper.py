COLUMN_ALIASES = {

    "sales": "Satış",
    "revenue": "Gelir",
    "price": "Fiyat",
    "cost": "Maliyet",
    "profit": "Kâr",
    "customer": "Müşteri",
    "date": "Tarih",
    "quantity": "Miktar",
    "units": "Satış Miktarı",
    "weight": "Ağırlık",
    "horsepower": "Motor Gücü",
    "torque": "Tork",
}


def humanize_column(col):

    col_lower = col.lower()

    for key, value in COLUMN_ALIASES.items():

        if key in col_lower:
            return value

    return col.replace("_", " ").title()