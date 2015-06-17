import pytest

from bibframe.isbnplus import isbn_list, compute_ean13_check

ISBN_LISTS = [
    {'expected': [('978158890215', '(TNY)'), ('978313612804', '(GTV)')],
    'inputs': [
        ['9783136128046 (GTV)', '1588902153 (TNY)', '9781588902153 (TNY)', '3136128044 (GTV)'],
        ['9783136128046 (GTV)', '9781588902153 (TNY)', '1588902153 (TNY)', '3136128044 (GTV)'],
        ['978-3136128046 (GTV)', '3136128044 (GTV)', '978-1588902153 (TNY)', '1588902153 (TNY)'],
    ]},
    {'expected': [('978068807546', None)],
    'inputs': [
        ['0688075460'],
    ]}
]

ISBN_LISTS_ENTAILED = [] #inputdata, expected
for igroup in ISBN_LISTS:
    for inp in igroup['inputs']:
        ISBN_LISTS_ENTAILED.append((inp, igroup['expected']))

@pytest.mark.parametrize('inputdata,expected', ISBN_LISTS_ENTAILED)
def test_isbn_list(inputdata, expected):
    result = list(isbn_list(inputdata))
    assert result == expected, (result, expected)


ISBN_13_TESTS = {
    '9781588902153': '9781588902153',
    '978158890215': '9781588902153',
    '9783136128046': '9783136128046',
    '978313612804': '9783136128046',
    '4006381333931': '4006381333931',
    '400638133393': '4006381333931',
    '9780615886084': '9780615886084',
    '978061588608': '9780615886084',
    '978068807546': '9780688075460',
}


@pytest.mark.parametrize('inputdata,expected', ISBN_13_TESTS.items())
def test_compute_ean13_check(inputdata, expected):
    result = compute_ean13_check(inputdata)
    assert len(result) == 13, (result,)
    assert result == expected, (result, expected)


if __name__ == '__main__':
    raise SystemExit("Run with py.test")
