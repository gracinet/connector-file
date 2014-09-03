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

{
    'name': 'Connector for importing bank statement files',
    'version': '0.1',
    'category': 'Connector',
    'author': 'Anybox',
    'website': 'http://anybox.fr',
    'license': 'AGPL-3',
    'description': """
Extension of the connector file import to treat bank statements.
""",
    'depends': [
        'connector_file',
        'account_statement_base_import',
    ],
    'external_dependencies': {
    },
    'update_xml': [
        'view/backend_model_view.xml',
        'view/chunk_binding_view.xml',
    ],
    'installable': True,
}
