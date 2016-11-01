import collections

# Functional iterator.

class FuncIter(collections.Iterator):
    def __init__(self,input_iter):
        self._input_iter = input_iter
    
    def next(self):
        """
        Perform one iteration of the input iterator.
        This is used to make the FuncIter behave like an iterator.
        """
        return next(self._input_iter)

    def map(self,func):
        """
        Map
        """
        return FuncIter(func(elem) for elem in self._input_iter)

    def any(self,func):
        """
        Check if any of the elements satisfy some condition.
        """
        for elem in self._input_iter:
            if func(elem) == True:
                return True
        return False

    def all(self,func):
        """
        Check if all the elements satisfy some condition.
        """
        for elem in self._input_iter:
            if func(elem) == False:
                return False
        return True


    def filter(self,func):
        """
        Filter
        """
        def filt_inner_iter():
            for elem in self._input_iter:
                if func(elem) == True:
                    yield elem

        return FuncIter(filt_inner_iter())

    def unique(self,key):
        """
        Bring only unique elements according to some key function.
        """
        def unique_inner_iter():
            # Keys that we have already seen:
            seen_keys = set()
            
            for elem in self._input_iter:
                elem_key = key(elem)
                if elem_key not in seen_keys:
                    seen_keys.add(elem_key)
                    yield elem

        return FuncIter(unique_inner_iter())

