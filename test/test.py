from binfr.binfr import find_all_occurrences, find_unique_contexts
from test_data import find_all_occurrences_test_data, find_unique_context_test_data
import pytest

@pytest.mark.parametrize("data, search, expected", find_all_occurrences_test_data)
def test_find_all_occurrences(data, search, expected):
    observed_offsets = find_all_occurrences(data, search)

    assert observed_offsets == expected

@pytest.mark.parametrize("data, search, expected", find_unique_context_test_data)
def test_find_unique_context(data, search, expected):
    prefix, find, suffix = search

    offsets = find_all_occurrences(data, prefix + find + suffix)
    observed_contexts = find_unique_contexts(data, offsets, prefix, find, suffix)

    assert observed_contexts == expected
