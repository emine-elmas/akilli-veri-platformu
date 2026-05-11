def humanize(text):

    return (
        str(text)
        .replace("_", " ")
        .title()
    )


def normalize(text):

    return (
        str(text)
        .lower()
        .replace("_", "")
        .replace(" ", "")
        .replace("-", "")
    )