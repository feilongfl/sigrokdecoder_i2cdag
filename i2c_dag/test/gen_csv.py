#!/usr/bin/env python
import fire


class IIC():
    def __init__(self, file):
        self.file = open(file, "w")

        self.process_dict = {
            'idle': self._process_idle,
            'start': self._process_start,
            'stop': self._process_stop,
            'ack': self._process_ack,
            'nack': self._process_nack,
        }

        self.write(['scl,sda'])

    def write(self, lines):
        self.file.write('\n'.join(lines) + '\n')

    def close(self):
        self.file.close()

    ################################
    # IIC Gen
    ################################
    def writeBit(self, byte, bit):
        data = (int(byte, 0) >> (7-bit)) & 0x01
        # print('writeBit', data)

        # self.write([f'0,{data}'])
        self.write([f'1,{data}'])
        self.write(['0,0'])

    def writeData(self, command):
        # print('writeData: ', command)
        index = 0
        while index < 8:
            self.writeBit(command, index)

            index += 1

    ################################
    # process
    ################################
    def process(self, command):
        self.write(['; %s' % command])
        if(command in self.process_dict.keys()):
            self.process_dict[command](command)
        else:
            self.writeData(command)

    def _process_idle(self, command):
        # print('_process_idle')
        self.write(['1,1', '1,1', '1,1', '1,1', '1,1'])

    def _process_start(self, command):
        # print('_process_start')
        self.write(['1,1', '1,0', '0,0'])

    def _process_stop(self, command):
        # print('_process_start')
        self.write(['0,0', '1,0', '1,1'])

    def _process_ack(self, command):
        # print('_process_ack')
        self.write(['0,0', '1,0', '0,0'])

    def _process_nack(self, command):
        # print('_process_nack')
        self.write(['0,1', '1,1', '0,1'])


def gen(file: str) -> None:
    iic = IIC(file + ".csv")

    with open(file) as f:
        for command in f:
            iic.process(command.strip())

    iic.close()


fire.Fire(gen)
