# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Georges Racinet
#    Copyright 2014 Anybox SAS
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import csv
import osv
import simplejson as json
from binascii import b2a_base64
from cStringIO import StringIO
from datetime import datetime

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from openerp.addons.connector_file.unit.move_load_policy import MoveLoadPolicy

from ..backend import file_import_bank_statement


def now_str():
    return datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)


# here it'd be more logical if the base class would be called simply
# LoadPolicy (and its parent LoadPolicy should be called BaseLoadPolicy)
@file_import_bank_statement
class StatementLoadPolicy(MoveLoadPolicy):
    """Defines the load process of CSV chunks as bank statements."""

    def load_one_chunk(self, chunk_b_id):
        """Load chunk as a bank statement.

        Notes:

        * the chunk content will end up as attachment on the statement object
          as well (poor DB)
        * for now I'm forced to reconstruct the CSV, to give it to statement
          profile parser (base64 and all). Inefficient and another source of
          hardcoding (dialect). It'd be so much better to use an entry point
          meant for after parsing.
        * auto-completion is already taken care of by import profile, but that
          means the configuration must be appropriate. TODO
          can it be correct to confirm a statement that has not been
          auto-completed ? If not, the method should raise an error if the
          profile is not an auto-completing one.
        """
        s = self.session
        profile_obj = s.pool['account.statement.profile']

        chunk_b = s.pool[self._model_name].browse(s.cr, s.uid, chunk_b_id,
                                                  context=s.context)
        backend_b = chunk_b.backend_id
        if chunk_b.load_state != 'pending':
            return
        csv_stream = StringIO()
        writer = csv.writer(csv_stream, dialect='excel')
        writer.writerow(json.loads(chunk_b.prepared_header))
        data_lines = json.loads(chunk_b.prepared_data)
        if not data_lines:  # one is never too safe
            return

        map(writer.writerow, data_lines)
        csv_stream.seek(0)

        profile_id = backend_b.bank_stmt_profile_id.id

        savepoint = 'chunk_import_statement'
        s.cr.execute('SAVEPOINT ' + savepoint)
        try:
            # called method has a bogus parameter 'ids' (unused),
            # that we're forced to pass anyway, same as the wizard also does
            # it's tempting to use _statement_import, let's try not to do it
            st_ids = profile_obj.multi_statement_import(
                s.cr, s.uid, False,
                profile_id,
                b2a_base64(csv_stream.read()),
                context=s.context)
            if len(st_ids) > 1:
                # GR I'm not really sure what the most appropriate exc is
                raise osv.except_osv(
                    "Wrong configuration",
                    "The parser for import profile %d "
                    "should not issue multiple statements "
                    "to be used in "
                    "connector_file_bank_statement " % profile_id)
            st_id = st_ids[0]

            chunk_b.write(dict(bank_statement_id=st_id))
            st_obj = s.pool['account.bank.statement']

            stmt_edit = {}
            st_obj.write(s.cr, s.uid, [st_id], {}, context=s.context)

            if backend_b.bank_stmt_by_date:
                # chunks are guaranteed to hold at most one line date
                stmt_edit['date'] = data_lines[0][1]
            if backend_b.bank_stmt_by_label:
                # chunks are guaranteed to hold at most one line label
                stmt_edit['name'] = '%s/%d-%d' % (data_lines[0][4],
                                                  chunk_b.line_start,
                                                  chunk_b.line_stop)

            # write may well be empty, but that's exactly what the
            # 'compute' button does, so it might actually be useful.
            st_obj.write(s.cr, s.uid, [st_id], stmt_edit, context=s.context)

            # TODO check if all lines are completed ?
            st_obj.button_confirm_bank(s.cr, s.uid, [st_id], context=s.context)
        except Exception as exc:
            # TODO finer exception treatment
            # TODO i18n
            s.cr.execute('ROLLBACK TO SAVEPOINT ' + savepoint)
            chunk_b.write(dict(load_state='failed',
                               exc_info=u'Error in bank statement import or '
                               u'processing: ' + repr(exc)))
        else:
            s.cr.execute('RELEASE SAVEPOINT ' + savepoint)
            chunk_b.write(dict(sync_date=now_str(),
                               # TODO bank_statement_id=st_id,
                               load_state='done'), context=s.context)
            # TODO raise for complete traceback in job ?
            # certainly not what LoadMovePolicy does (exception already
            # swallowed by ORM's load())
