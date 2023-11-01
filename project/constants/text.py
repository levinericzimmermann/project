def _split(s, delimiter):
    d = delimiter
    ls = []
    s = s.strip()
    split_data = [n for n in s.split(d) if n]
    for n in split_data[:-1]:
        ls.append(n + d)
    if split_data:
        last = split_data[-1] + d if s[-1] == d else split_data[-1]
        ls.append(last)
    return [n.strip() for n in ls]


def _():
    with open("project/constants/feldweg", "r") as f:
        feldweg = f.read()

    sentences = [feldweg]
    delimiter_tuple = (".", "?", ":", ";")
    for d in delimiter_tuple:
        n = []
        for s in sentences:
            n.extend(_split(s, d))
        sentences = n

    # manually split very long sentences
    sentences[27:28] = _split(sentences[27], 'ob')
    sentences[1:2] = _split(sentences[1], ',')
    sentences[60:61] = _split(sentences[60], 'tes,')

    sentences = list(filter(bool, sentences))
    sentences = [s.lower() for s in sentences]
    return tuple(sentences)


SENTENCE_TUPLE = _()
