import argparse
import collections
from functools import lru_cache
from sys import stdin, stdout
from Bio import SeqIO, SeqRecord
from itertools import islice


class SeqRecordWrapper(object):
    def __init__(self):
        self._r = None  # type: SeqRecord.SeqRecord

    @staticmethod
    @lru_cache(100)
    def _func_by_name(name):
        if name == '_':
            return lambda self: self
        if name in {'id', 'name', 'description', 'seq'}:
            return lambda self: getattr(self._r, name)
        if name == 'length':
            return lambda self: len(self._r)
        raise ValueError(name)

    def __getitem__(self, name):
        f = SeqRecordWrapper._func_by_name(name)
        return f(self)


def func_from_code(code):
    wrapper = SeqRecordWrapper()
    def _wrp_f(x):
        wrapper._r = x
        return eval(compile(code, "<string>", "eval"), None, wrapper)
    return _wrp_f


def main():
    p = argparse.ArgumentParser()
    p.add_argument('input', default=stdin, nargs='?')
    p.add_argument('-t', '--input-format', default='fasta')
    p.add_argument('-T', '--output-format')
    p.add_argument('-f', '--filter')
    p.add_argument('-m', '--map')
    p.add_argument('-a', '--aggregate')
    p.add_argument('--head', type=int)

    p.add_argument('--tail', type=int)

    def identity(x):
        return x

    def always_true(x):
        return True

    filter_func = always_true
    map_func = identity

    args = p.parse_args()

    if args.filter:
        filter_func = func_from_code(args.filter)

    if args.map:
        map_func = func_from_code(args.map)

    if not args.output_format:
        args.output_format = args.input_format

    f = SeqIO.parse(args.input, args.input_format)

    it = map(map_func, filter(filter_func, f))
    if args.head:
        it = islice(it, args.head)
    # if args.offset:
    #     it = islice(it, 0, args.offset)

    if args.tail:
        it = iter(collections.deque(it, maxlen=args.tail))

    if args.aggregate:
        def count(xs):
            return sum(1 for x in xs)

        def mean(xs):
            s = 0
            c = 0
            for x in xs:
                s += x
                c += 1
            return s / c
        agg_func = eval(compile(args.aggregate, "<string>", "eval"), None, dict(count=count, mean=mean))
        print(args.aggregate, agg_func(it))
    else:
        for r in it:
            if isinstance(r, SeqRecord.SeqRecord):
                stdout.write(r.format(args.output_format))
            else:
                if isinstance(r, tuple):
                    stdout.write('\t'.join(map(str, r)))
                else:
                    stdout.write(str(r))
                stdout.write('\n')

if __name__ == '__main__':
    main()

