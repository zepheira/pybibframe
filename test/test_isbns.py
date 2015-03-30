import pytest

from bibframe.isbnplus import isbn_list

ISBN_LISTS = [
    {'expected': [('978158890215', '(TNY)'), ('978313612804', '(GTV)')],
    'inputs': [
        ['9783136128046 (GTV)', '1588902153 (TNY)', '9781588902153 (TNY)', '3136128044 (GTV)'],
        ['9783136128046 (GTV)', '9781588902153 (TNY)', '1588902153 (TNY)', '3136128044 (GTV)'],
        ['978-3136128046 (GTV)', '3136128044 (GTV)', '978-1588902153 (TNY)', '1588902153 (TNY)'],
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


if __name__ == '__main__':
    raise SystemExit("Run with py.test")
