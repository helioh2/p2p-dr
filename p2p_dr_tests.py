import unittest
from p2pdr import *

class TestP2P_DR(unittest.TestCase):

    def setUp(self):
        self.C1 = Context("C1", ["C3", "C2", "C4", "C5", "C6"])
        self.C2 = Context("C2")
        self.C3 = Context("C3")
        self.C4 = Context("C4")
        self.C5 = Context("C5")
        self.C6 = Context("C6")

    def test_rank(self):
        self.assertEqual(rank(Literal("x", C2), self.C1.preferences), 2)
        self.assertEqual(rank(Literal("x", C3), self.C1.preferences), 1)
        self.assertEqual(rank(Literal("x", C4), self.C1.preferences), 3)
        self.assertEqual(rank(Literal("x", C5), self.C1.preferences), 4)
        self.assertEqual(rank(Literal("x", C6), self.C1.preferences), 5)
        self.assertEqual(rank(Literal("x", C1), self.C1.preferences), 0)


if __name__ == '__main__':
    unittest.main()