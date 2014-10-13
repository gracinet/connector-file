import simplejson as json
from anybox.testing.openerp import SharedSetupTransactionCase


class TestLoadPolicy(SharedSetupTransactionCase):

    _data_files = ('profile_backend.xml',)

    def setUp(self):
        super(TestLoadPolicy, self).setUp()
        self.backend_id = self.ref(
            'tests.file_import_backend_test_statements')
        self.chunk_binding = self.registry('file.chunk.binding')

    def make_chunk(self, tuples, line_start=3, line_stop=5):
        """Create a chunk.binding record.

        :param tuples: raw data, as a tuple of tuples (or iterable in the same
                       way)
        :returns: id of created record
        """
        att_id = self.registry('ir.attachment').create(
            self.cr, self.uid,
            dict(name="fake attachment",
                 description="needed for reference only",
                 type='binary'))

        att_b_id = self.registry('ir.attachment.binding').create(
            self.cr, self.uid,
            dict(openerp_id=att_id,
                 prepared_header='["ref", "date", "amount", '
                 '"commission_amount", "label"]',
                 backend_id=self.backend_id,
                 parse_state='done'))

        chunk_id = self.registry('file.chunk').create(
            self.cr, self.uid,
            dict(prepared_data=json.dumps(tuples),
                 line_start=line_start,
                 line_stop=line_stop))

        return self.chunk_binding.create(
            self.cr, self.uid,
            dict(openerp_id=chunk_id,
                 attachment_binding_id=att_b_id,
                 backend_id=self.backend_id))

    def test_basic(self):
        """Import a statement using the most basic configuration."""
        cb_id = self.make_chunk(
            [["ref1", "2014-07-02", "13.6", "", "label1"],
             ["ref2", "2014-07-03", "200.0", "", "label2"]])
        self.chunk_binding.load_now_button(self.cr, self.uid, [cb_id])
        self.assertRecord(self.chunk_binding, cb_id, dict(load_state='done'))

    def test_name_from_lines(self):
        """Import a statement w/ backend set so that name is from the lines.
        """
        cr, uid = self.cr, self.uid

        self.registry('file_import.backend').write(
            cr, uid, self.backend_id, dict(bank_stmt_by_label=True))

        cb_id = self.make_chunk(
            [["ref1", "2014-07-02", "13.6", "", "unique_label"],
             ["ref2", "2014-07-03", "200.0", "", "unique_label"]],
            line_start=103, line_stop=105)
        self.chunk_binding.load_now_button(cr, uid, [cb_id])

        chunk_br = self.chunk_binding.browse(cr, uid, cb_id)
        self.assertEqual(chunk_br.load_state, 'done')
        stmt_br = chunk_br.bank_statement_id
        self.assertEqual(stmt_br.name, 'unique_label/103-105')

    def test_date_from_lines(self):
        """Import a statement w/ backend set so that date is from the lines.
        """
        cr, uid = self.cr, self.uid

        self.registry('file_import.backend').write(
            cr, uid, self.backend_id, dict(bank_stmt_by_date=True))

        cb_id = self.make_chunk(
            [["ref1", "2014-07-02", "13.6", "", "spam"],
             ["ref2", "2014-07-02", "200.0", "", "eggs"]],
            line_start=103, line_stop=105)
        self.chunk_binding.load_now_button(cr, uid, [cb_id])

        chunk_br = self.chunk_binding.browse(cr, uid, cb_id)
        self.assertEqual(chunk_br.load_state, 'done')
        stmt_br = chunk_br.bank_statement_id
        self.assertEqual(stmt_br.date, '2014-07-02')
