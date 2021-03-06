# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
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
"""Policy for parsing CSV files into chunks."""
import csv
import simplejson
from datetime import datetime

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from ..backend import file_import
from .policy import ParsePolicy


@file_import
class CSVParsePolicy(ParsePolicy):

    """Policy to parse a CSV file into chunks with JSON data."""

    _model_name = 'ir.attachment.binding'

    def ask_files(self):
        """Return a list of files to parse."""
        return self.session.search(self._model_name, [
            ('sync_date', '=', False),
            ('backend_id', '=', self.backend_record.id),
        ])

    def parse_one(self, attachment_b_id):
        """Parse the attachment and split it into chunks."""
        s = self.session
        chunk_b_obj = s.pool['file.chunk.binding']
        attachment_b = s.browse(self.model._name, attachment_b_id)

        if attachment_b.parse_state != 'pending':
            return

        backend = attachment_b.backend_id

        file_like = self.model.get_file_like(
            s.cr,
            s.uid,
            [attachment_b_id],
            context=s.context
        )
        self.model.write(s.cr, s.uid, attachment_b_id, {
            'prepared_header': self._parse_header_data(file_like,
                                                       backend.delimiter,
                                                       backend.quotechar),
            'sync_date': datetime.now().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT
            ),
            'parse_state': 'done',
        })

        file_like_2 = self.model.get_file_like(
            s.cr,
            s.uid,
            [attachment_b_id],
            context=s.context
        )

        for chunk_data in self._split_data_in_chunks(file_like_2,
                                                     backend.delimiter,
                                                     backend.quotechar):

            chunk_data.update({
                'attachment_binding_id': attachment_b_id,
                'backend_id': backend.id,
            })

            chunk_b_obj.create(s.cr, s.uid, chunk_data, context=s.context)

    @staticmethod
    def _split_data_in_chunks(data, delimiter, quotechar):
        """Take a file-like object, and return chunk data."""
        with data as file_like:
            file_like.seek(0)
            reader = csv.reader(
                file_like,
                delimiter=str(delimiter),
                quotechar=str(quotechar),
            )

            # skip the header
            reader.next()

            chunk_array = []
            line_start = 1

            for line in reader:
                # it is a move, not a move line: write a chunk and create a
                # new one
                if line[0]:
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

    @staticmethod
    def _parse_header_data(data, delimiter, quotechar):
        """Take a file-like object, and return JSON-parsed header."""
        with data as file_like:
            file_like.seek(0)

            reader = csv.reader(
                file_like,
                delimiter=str(delimiter),
                quotechar=str(quotechar),
            )

            try:
                raw_header = reader.next()
            except StopIteration:
                # empty file, we can also decide to raise here
                return ''
            return simplejson.dumps(raw_header)
