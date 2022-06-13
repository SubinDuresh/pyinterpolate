import unittest
from typing import Tuple, Dict

import numpy as np
from pyinterpolate.distance.distance import calc_block_to_block_distance


NO_OF_BLOCKS = 3
BLOCK_IDS = np.arange(0, NO_OF_BLOCKS)
BLOCKS = {}
for bid in BLOCK_IDS:
    points = np.random.randint(0, 1000, (100, 3))
    BLOCKS[bid] = points

class TestBlockToBlockFn(unittest.TestCase):

    def test_calculate_block_to_block(self):
        distances = calc_block_to_block_distance(BLOCKS)
        self.assertIsInstance(distances, Tuple)
        self.assertIsInstance(distances[0], Dict)
        self.assertIsInstance(distances[1], Tuple)
        self.assertEqual(distances[1], (0, 1, 2))
