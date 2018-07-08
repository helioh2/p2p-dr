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
        self.assertEqual(self.C1.rank(Literal("x", self.C2)), 2)
        self.assertEqual(self.C1.rank(Literal("x", self.C3)), 1)
        self.assertEqual(self.C1.rank(Literal("x", self.C4)), 3)
        self.assertEqual(self.C1.rank(Literal("x", self.C5)), 4)
        self.assertEqual(self.C1.rank(Literal("x", self.C6)), 5)
        self.assertEqual(self.C1.rank(Literal("x", self.C1)), 0)


if __name__ == '__main__':
    unittest.main()