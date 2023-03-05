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
import debugpy

from .dag_object import DAGObject

logfile = os.path.join(tempfile.gettempdir(), 'sigrok_decoder_i2c_dag.log')
logging.basicConfig(filename=logfile,
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    format='%(asctime)s %(message)s',
                    encoding='utf-8', level=logging.INFO)


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

    def __init_debuger__(self):
        debugpy.listen(5678)
        logging.info("I²C DAG: waiting debugger")
        debugpy.wait_for_client()
        logging.info("I²C DAG: debugger connect")
        debugpy.breakpoint()
        logging.info("I²C DAG: debugger run")

    def __init__(self):
        logging.info("I²C DAG: init")
        print(f"I²C DAG: log storage to {logfile}")

        self.dagfile = ""
        self.dag = None

        self._decode_listener_init()
        # self.__init_debuger__()

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

    def put_bitName(self, ss, es, bitdesc, data):
        mask = 1 << (bitdesc.mask.end+1) - 1 << bitdesc.mask.start
        desc = "%s: %s" % (
            bitdesc.longname, bitdesc.value.__dict__[data & mask])
        self.put(ss, es, self.out_ann, [1, [desc, bitdesc.name]])

    ###########################
    # decord listeners
    ###########################
    def _decode_listener_address_write(self, ss, es, data) -> None:
        self._dag = self.dag.getDAG(data[1])
        if self._dag == None:
            logging.warning("ignore addr %s" % data[1])
        else:
            self.put_dagName(ss, es, self._dag)

        self._last_bits = None
        pass

    # subfunc by: _decode_listener_data
    def _decode_listener_data_bits_each(self, bitdesc, data):
        (_, _, bits) = self._decode_listener_bits_last

        ss, es = bits[bitdesc.mask.end][1], bits[bitdesc.mask.start][2]
        self.put_bitName(ss, es, bitdesc, data)

    # subfunc by: _decode_listener_data
    def _decode_listener_data_bits(self, dag_bits, data):
        for bitdesc in dag_bits:
            self._decode_listener_data_bits_each(bitdesc, data)

    def _decode_listener_data(self, ss, es, data) -> None:
        if self._dag == None:
            return

        if 'dag_bits' in self._dag.__dict__.keys():
            self._decode_listener_data_bits(self._dag.dag_bits, data[1])
            self._dag = self._dag.nextDag()
            pass
        else:
            self._dag = self._dag.getDAG(data[1])
            if self._dag == None:
                logging.warning("ignore data %s" % data[1])
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
