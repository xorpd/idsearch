import unittest
from idsearch.func_iter import FuncIter

class TestSearchDB(unittest.TestCase):
    def test_basic(self):
        my_iter = (i for i in range(5))
        fiter = FuncIter(my_iter)
        self.assertEqual(list(fiter), [0,1,2,3,4])

    def test_map(self):
        my_iter = (i for i in range(5))
        fiter = FuncIter(my_iter)
        new_fiter = fiter.map(lambda x:x*x)
        self.assertEqual(list(new_fiter), [0,1,4,9,16])

    def test_all(self):
        my_iter = (i for i in range(5))
        fiter = FuncIter(my_iter)
        new_fiter = fiter.all(lambda x:x>-1)
        self.assertEqual(new_fiter, True)

        my_iter = (i for i in range(5))
        fiter = FuncIter(my_iter)
        new_fiter = fiter.all(lambda x:x>2)
        self.assertEqual(new_fiter, False)

    def test_any(self):
        my_iter = (i for i in range(5))
        fiter = FuncIter(my_iter)
        new_fiter = fiter.any(lambda x:x>-1)
        self.assertEqual(new_fiter, True)

        my_iter = (i for i in range(5))
        fiter = FuncIter(my_iter)
        new_fiter = fiter.any(lambda x:x>2)
        self.assertEqual(new_fiter, True)

        my_iter = (i for i in range(5))
        fiter = FuncIter(my_iter)
        new_fiter = fiter.any(lambda x:x>6)
        self.assertEqual(new_fiter, False)


    def test_filter(self):
        my_iter = (i for i in range(5))
        fiter = FuncIter(my_iter)
        new_fiter = fiter.filter(lambda x:(x%2)==0)
        self.assertEqual(list(new_fiter), [0,2,4])

    def test_unique(self):
        my_iter = (i for i in [1,5,5,2,5,3,1])
        fiter = FuncIter(my_iter)
        new_fiter = fiter.unique(lambda x:x)
        self.assertEqual(list(new_fiter), [1,5,2,3])

    def test_double_map(self):
        my_iter = (i for i in range(5))
        fiter = FuncIter(my_iter)
        new_fiter = fiter.map(lambda x:x*x).map(lambda x:-x)
        self.assertEqual(list(new_fiter), [0,-1,-4,-9,-16])

    def test_load_from_list(self):
        my_iter = [0,1,2,3,4]
        fiter = FuncIter(my_iter)
        new_fiter = fiter.map(lambda x:x*x)
        self.assertEqual(list(new_fiter), [0,1,4,9,16])
