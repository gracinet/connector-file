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
from openerp.osv import orm, fields


class chunk_binding_bank_statement(orm.Model):
    """Adding an optional link to imported bank statement."""

    _name = 'file.chunk.binding'
    _inherit = 'file.chunk.binding'

    _columns = dict(
        bank_statement_id=fields.many2one(
            'account.bank.statement', string="Bank Statement"),
    )
