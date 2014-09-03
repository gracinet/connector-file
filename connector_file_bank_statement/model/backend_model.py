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
"""Backend Model for Bank Statements.

It's exactly the same as for account moves : unit differentiation will hapen
because of backend version (I hope)
"""

from openerp.osv import orm, fields


class file_import_bank_statement_backend(orm.Model):
    """Adding another version with its specific fields"""

    _name = "file_import.backend"
    _inherit = "file_import.backend"

    def _select_versions(self, cr, uid, context=None):
        """Parent model inheritance (needs redefinition)."""
        return super(file_import_bank_statement_backend,
                     self)._select_versions(cr, uid, context=context) + [
            ('bank_statement_1', 'Bank Statement v1')]

    _columns = dict(
        version=fields.selection(_select_versions,
                                 string='Version',
                                 required=True),
        bank_stmt_profile_id=fields.many2one('account.statement.profile',
                                             string="Import profile"),
        bank_stmt_chunk_size=fields.integer(
            string="Statement maximum chunk size"),
        bank_stmt_by_date=fields.boolean(
            string="One line date per chunk, and make it statement's date"),
        bank_stmt_by_label=fields.boolean(
            string="One line label per chunk, and "
            "base statement's name on it")
    )

    _defaults = dict(bank_stmt_chunk_size=50)

    # TODO add constraint to make profile required on this backend version
