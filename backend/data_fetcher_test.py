# Copyright 2020 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
"""Test Module for data_fetcher.py"""
# pylint: disable=W0212

import pytest
from data_fetcher import DataFetcher


class TestDataFetcher:
    """Test Class for data_fetcher.py"""
    @pytest.mark.parametrize('numbers,value,expected', [
        ([0, 2, 4, 6, 8, 10, 12], -1, 0),
        ([0, 2, 4, 6, 8, 10, 12], 0, 0),
        ([0, 2, 4, 6, 8, 10, 12], 1, 0),
        ([0, 2, 4, 6, 8, 10, 12], 2, 0),
        ([0, 2, 4, 6, 8, 10, 12], 3, 1),
        ([0, 2, 4, 6, 8, 10, 12], 4, 1),
        ([0, 2, 4, 6, 8, 10, 12], 5, 2),
        ([0, 2, 4, 6, 8, 10, 12], 6, 2),
        ([0, 2, 4, 6, 8, 10, 12], 12, 5),
        ([0, 2, 4, 6, 8, 10, 12], 13, 6),
        ([0, 2, 4, 6, 8, 10, 12], 100, 6),
    ])
    def test__binary_search_increasing(self, numbers, value, expected):
        """Tests binary search with list of numbers in increasing order."""
        preprocess = DataFetcher('dummy', 'dummy')
        assert preprocess._binary_search(numbers, value, False) == expected

    @pytest.mark.parametrize('numbers,value,expected', [
        ([10, 8, 6, 4, 2, 0], 100, 0),
        ([10, 8, 6, 4, 2, 0], 10, 0),
        ([10, 8, 6, 4, 2, 0], 9, 0),
        ([10, 8, 6, 4, 2, 0], 8, 1),
        ([10, 8, 6, 4, 2, 0], 7, 1),
        ([10, 8, 6, 4, 2, 0], 4, 3),
        ([10, 8, 6, 4, 2, 0], 3, 3),
        ([10, 8, 6, 4, 2, 0], 1, 4),
        ([10, 8, 6, 4, 2, 0], 0, 5),
        ([10, 8, 6, 4, 2, 0], -1, 5),
    ])
    def test__binary_search_decreasing(self, numbers, value, expected):
        """Tests binary search with list of numbers in decreasing order."""
        preprocess = DataFetcher('dummy', 'dummy')
        assert preprocess._binary_search(numbers, value, True) == expected
