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
"""Generic File Import Backend."""


from openerp.addons.connector import backend
from openerp.addons.connector_file.backend import file_import

file_import_bank_statement = backend.Backend(parent=file_import,
                                             version="bank_statement_1")
