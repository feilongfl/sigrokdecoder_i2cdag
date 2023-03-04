##
# This file is part of the libsigrokdecode project.
##
# Copyright (C) 2023 YuLong Yao<feilongphone@gmail.com>
##
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
##
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
##
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
##

import sigrokdecode as srd
import os
import logging
import tempfile

from .dag_object import DAGObject

logfile = os.path.join(tempfile.gettempdir(), 'sigrok_decoder_i2c_dag.log')
logging.basicConfig(filename=logfile,
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    format='%(asctime)s %(message)s',
                    encoding='utf-8', level=logging.DEBUG)


class Decoder(srd.Decoder):
    api_version = 3
    id = 'i2c_dag'
    name = 'I²C DAG'
    longname = 'I2C_DAG'
    desc = 'Analyse I2C by DAG file.'
    license = 'gplv2+'
    inputs = ['i2c']
    outputs = []
    options = (
        {'id': 'dag', 'desc': 'Dag', 'default': os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'dag_demo.yml')},
    )
    tags = ['IC', 'Memory']
    annotations = (
        # Warnings
        ('warning', 'Warning'),
        # frame
        ('device', 'Device'),
    )
    annotation_rows = (
        ('warnings', 'Warnings', (0,)),
        ('frame', 'Frames', (1, )),
    )

    def __init__(self):
        logging.info("I²C DAG: init")
        print(f"I²C DAG: log storage to {logfile}")

        self.dagfile = ""
        self.dag = None

        self._decode_listener_init()

    def reset(self):
        logging.info("I²C DAG: reset")

    def start(self):
        logging.info("I²C DAG: start")
        self.out_ann = self.register(srd.OUTPUT_ANN)

        self.dagfile = self.options['dag']
        logging.info("dag: %s" % os.path.realpath(self.dagfile))
        self.dag = DAGObject(file=self.dagfile)

    def decode(self, ss, es, data):
        logging.info("I²C DAG: decode: %s" % data)

        if self.dag == None:
            return

        if data[0] in self.decode_listener.keys():
            self.decode_listener[data[0]](ss, es, data)

    ###########################
    # Print Methods
    ###########################
    def put_dagName(self, ss, es, dag):
        self.put(ss, es, self.out_ann, [1, dag.getName()])

    def put_bitName(self, ss, es, bit):
        self.put(ss, es, self.out_ann, [1, [bit.longname, bit.name]])

    ###########################
    # decord listeners
    ###########################
    def _decode_listener_address_write(self, ss, es, data) -> None:
        self._dag = self.dag.getDAG(data[1])
        if self._dag == None:
            logging.debug("ignore addr %s" % data[1])
        else:
            self.put_dagName(ss, es, self._dag)

        self._last_bits = None
        pass

    def _decode_listener_data_bits_xxx(self, bitdesc):
        (_, _, data) = self._decode_listener_bits_last

        ss, es = data[7-bitdesc.mask.start][1], data[7-bitdesc.mask.end][2]
        logging.debug("I²C DAG: _decode_listener_data_bits_xxx: %s" %
                      bitdesc.mask.start)
        logging.debug("I²C DAG: _decode_listener_data_bits_xxx: %s" %
                      bitdesc.mask.end)
        self.put_bitName(ss, es, bitdesc)

    def _decode_listener_data_bits(self, dag_bits):
        logging.debug(
            "I²C DAG: last_bits: [%s][%s] %s" % self._decode_listener_bits_last)
        logging.debug("I²C DAG: dag_bits_desc: %s" % dag_bits)

        for bitdesc in dag_bits:
            self._decode_listener_data_bits_xxx(bitdesc)

    def _decode_listener_data(self, ss, es, data) -> None:
        if self._dag == None:
            return

        # logging.debug(self._dag.__dict__)
        if 'dag_bits' in self._dag.__dict__.keys():
            self._decode_listener_data_bits(self._dag.dag_bits)
            pass
        else:
            self._dag = self._dag.getDAG(data[1])
            if self._dag == None:
                logging.debug("ignore data %s" % data[1])
            else:
                self.put_dagName(ss, es, self._dag)

    def _decode_listener_bits(self, ss, es, data) -> None:
        self._decode_listener_bits_last = (ss, es, data[1])
        pass

    def _decode_listener_init(self) -> None:
        self.decode_listener = {
            'ADDRESS WRITE': self._decode_listener_address_write,
            'DATA WRITE': self._decode_listener_data,
            'DATA READ': self._decode_listener_data,
            'BITS': self._decode_listener_bits,
        }
        pass
