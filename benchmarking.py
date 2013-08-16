import benchmark
import dictdiffer
from dictdiffernew import DictDiffer
def set_diff(first,second):
    firstset = frozenset(first)
    secondset = frozenset(second)
    intersection = firstset.intersection(secondset)
    addition = secondset - intersection
    deletion = firstset - intersection


def loop_diff(first,second):
    intersection = [k for k in first if k in second]
    addition = [k for k in second if not k in first]
    deletion = [k for k in first if not k in second]

class Benchmark_DictDiffer(benchmark.Benchmark):
    label = "compare dictdiffer.diff and diff of DictDiffer """
    each = 100
    def setUp(self):
        d1 = {'ahhhh':['111','222',['jajja',1],3],'dict':{'hhhh':11,'a':2,'dict':{'a':1}}}
        d2 = {'ahhhh':['111','222',['jajja',1,2]],'dict':{'h':2,'a':[2,3],'dict':{'a':2}}}
        self.d1 = {'shit':d1,'tu':d2,'uuu':d1}
        self.d2 = {'shat':d1,'tu':d1}
        self.differ_DictDiffer = DictDiffer().diff
        self.differ_dictdiffer = dictdiffer.diff

    def test_dictdiffer(self):
        diff = self.differ_dictdiffer(self.d1,self.d2)
    def test_DictDiffer(self):
        diff = self.differ_DictDiffer(self.d1,self.d2)

class Benchmark_DictDiff(benchmark.Benchmark):
    label = 'Benchmark for small dict with same keys'
    each = 100
    def setUp(self):
        self.first = {str(x):x for x in range(100)}
        self.second = {str(x):x for x in range(100)}

    def test_set(self):
        set_diff(self.first,self.second)

    def test_loop(self):
        loop_diff(self.first,self.second)

class Benchmark_DictDiff_2(Benchmark_DictDiff):
    label = 'Benchmark for small dict with completely different keys'
    def setUp(self):
        self.first = {str(x):x for x in range(100)}
        self.second = {str(x+200):x for x in range(100)}

class Benchmark_DictDiff_3(Benchmark_DictDiff):
    label = 'Benchmark for big dict with same keys'
    def setUp(self):
        self.first = {str(x):x for x in range(1000)}
        self.second = {str(x):x for x in range(1000)}

class Benchmark_DictDiff_4(Benchmark_DictDiff):
    label = 'Benchmark for big dict with completely different keys'
    def setUp(self):
        self.first = {str(x):x for x in range(1000)}
        self.second = {str(x+2000):x for x in range(1000)}

class Benchmark_DictDiff_5(Benchmark_DictDiff):
    label = 'Benchmark for huge dict with same keys'
    def setUp(self):
        self.first = {str(x):x for x in range(10000)}
        self.second = {str(x):x for x in range(10000)}

class Benchmark_DictDiff_6(Benchmark_DictDiff):
    label = 'Benchmark for huge dict with completely different keys'
    def setUp(self):
        self.first = {str(x):x for x in range(10000)}
        self.second = {str(x+2000):x for x in range(10000)}




if __name__ == '__main__':
    benchmark.main(format="markdown", numberFormat="%.4g")

