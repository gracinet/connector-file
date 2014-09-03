import unittest
import mock
from ..unit.csv_policy import StatementSplitter


def make_splitter(max_chunk_size=50,
                  by_date=False,
                  by_label=False):
    """Produce a :class:`StatementSplitter` instance conveniently.

    This does not require a true browse record.
    """
    backend_b = mock.Mock()
    backend_b.bank_stmt_chunk_size = max_chunk_size
    backend_b.bank_stmt_by_date = by_date
    backend_b.bank_stmt_by_label = by_label
    return StatementSplitter(backend_b)


class SplitterTestCase(unittest.TestCase):

    def test_chunk_size(self):
        splitter = make_splitter(max_chunk_size=3)
        lines = ([1], [2], [3], [4], [5])
        self.assertEqual([l[0] for l in lines if splitter.is_new_chunk(l)],
                         [1, 4])

    def test_by_date(self):
        splitter = make_splitter(by_date=True)
        lines = ((1, '2014-08-03'),
                 (2, '2014-08-03'),
                 (3, '2014-08-04'),
                 (4, '2014-08-04'),
                 (5, '2014-08-05'))
        self.assertEqual([l[0] for l in lines if splitter.is_new_chunk(l)],
                         [1, 3, 5])

    def test_by_label(self):
        splitter = make_splitter(by_label=True)
        lines = ((1, '2014-08-03', '', '', 'A'),
                 (2, '2014-08-03', '', '', 'A'),
                 (3, '2014-08-04', '', '', 'A'),
                 (4, '2014-08-04', '', '', 'B'),
                 (5, '2014-08-05', '', '', 'B'),)
        self.assertEqual([l[0] for l in lines if splitter.is_new_chunk(l)],
                         [1, 4])

    def test_by_date_and_label(self):
        splitter = make_splitter(by_date=True, by_label=True)
        lines = ((1, '2014-08-03', '', '', 'A'),
                 (2, '2014-08-03', '', '', 'A'),
                 (3, '2014-08-04', '', '', 'A'),
                 (4, '2014-08-04', '', '', 'B'),
                 (5, '2014-08-05', '', '', 'B'),)
        self.assertEqual([l[0] for l in lines if splitter.is_new_chunk(l)],
                         [1, 3, 4, 5])
