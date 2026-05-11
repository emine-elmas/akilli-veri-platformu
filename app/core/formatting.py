def compact_number(num):

    try:

        num = float(num)

        if abs(num) >= 1_000_000_000:
            return f"{num/1_000_000_000:.1f}B"

        if abs(num) >= 1_000_000:
            return f"{num/1_000_000:.1f}M"

        if abs(num) >= 1_000:
            return f"{num/1_000:.1f}K"

        return round(num, 2)

    except:
        return num