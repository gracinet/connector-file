# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Georges Racinet, Leonardo Pistone
#    Copyright 2014 Anybox SAS, Camptocamp SA
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
import simplejson

from openerp.addons.connector_file.unit.csv_policy import CSVParsePolicy
from ..backend import file_import_bank_statement


class StatementSplitter(object):
    """Provide the means to split according to configurable parameters.

    It is fed new parsed lines, and works by maintaining state between them.

    TODO check if that fits c2c way of thinking.
    """

    max_chunk_size = 50

    by_date = False
    """Produce chunks so that date is unique in them."""

    by_label = False
    """Produce chunks with unique label in them.

    Label may have a strong fonctional meaning for the user.
    """

    def __init__(self, backend_b):
        self.max_chunk_size = backend_b.bank_stmt_chunk_size
        self.by_date = backend_b.bank_stmt_by_date
        if self.by_date:
            self.current_date = None

        self.by_label = backend_b.bank_stmt_by_label
        if self.by_label:
            self.current_label = None

        self.current_chunk_lines = 0

    def is_new_chunk(self, line):
        """Tell if ``line`` should belong to a new chunk

        :returns: a boolean, always True upon the first line (for compat with
                  overidden code)
        """
        is_new = False

        if self.current_chunk_lines == 0:
            is_new = True
        if self.current_chunk_lines >= self.max_chunk_size:
            # GR if this is generalized, then parsers that eat several lines
            # at once must be supported, hence a modulo isn't reliable enough.
            self.current_chunk_lines = 0
            is_new = True
        self.current_chunk_lines += 1

        if self.by_date:
            if line[1] != self.current_date:
                is_new = True
            self.current_date = line[1]

        if self.by_label:
            if line[4] != self.current_label:
                is_new = True
            self.current_label = line[4]

        return is_new


@file_import_bank_statement
class StatementCSVParsePolicy(CSVParsePolicy):
    """Policy to split incoming CSV in bank statement chunks.

    Most of the code is duplicated from :class:`CSVParsePolicy`.
    Most of that duplication could be avoided if :class:`CSVParsePolicy`
    could register a splitter class, and instantiate it with a backend browse
    record
    """

    @staticmethod
    def _split_data_in_chunks(data, backend):
        """Generator that yields appropriate chunks for bank statements.

        :param data: a file like object with CSV content (including header)
        :param backend: browse record of the relevant backend model, or any
                        object having the same attributes.
        """

        with data as file_like:
            file_like.seek(0)
            reader = csv.reader(
                file_like,
                delimiter=str(backend.delimiter),
                quotechar=str(backend.quotechar),
            )

            # skip the header
            reader.next()

            chunk_array = []
            line_start = 1
            splitter = StatementSplitter(backend)

            for line in reader:
                if splitter.is_new_chunk(line):
                    # if we have a previous chunk, write it
                    if chunk_array:
                        yield {
                            'prepared_data': simplejson.dumps(chunk_array),
                            'line_start': line_start,
                            'line_stop': reader.line_num,
                        }
                    # reader.line_num is not the same as enumerate(reader): a
                    # field could contain newlines. We use line_num because we
                    # then use it to recover lines from the original file.
                    line_start = reader.line_num
                    # if it is first part of chunk we reinitialize chunck array
                    chunk_array = [line]
                else:
                    chunk_array.append(line)

            # write the last chunk
            if chunk_array:
                yield {
                    'prepared_data': simplejson.dumps(chunk_array),
                    'line_start': line_start,
                    'line_stop': reader.line_num + 1,
                }
