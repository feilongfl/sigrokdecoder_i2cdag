import yaml
import os
import logging

LOGGER = logging.getLogger(__name__)


class YAMLObject():
    def __init__(self, parent: dict = {}, file=None) -> None:
        if(file != None):
            with open(os.path.relpath(file)) as f:
                parent = yaml.safe_load(f)

        for k, v in parent.items():
            match v:
                case dict():
                    LOGGER.debug(f"dict  : k={k}, t={type(v)}, v={v}")
                    if k not in self.__dict__.keys():
                        self.__dict__[k] = self.__class__(v)

                case _:
                    LOGGER.debug(f"unknow: k={k}, t={type(v)}, v={v}")
                    if(k == 'include'):
                        LOGGER.info(f"include yml file: {v}")
                        dir = os.path.dirname(os.path.realpath(__file__))
                        file = os.path.join(dir, 'devices', v)

                        for k, v in self.__class__(file=file).items():
                            self.__dict__[k] = v
                    else:
                        self.__dict__[k] = v

    def __repr__(self) -> str:
        return yaml.dump(self.__dict__)

    def items(self):
        return self.__dict__.items()


class DAGObject(YAMLObject):
    def getName(self):
        return [self.info.longname, self.info.name]

    def getDAG(self, id):
        if id in self.dag.__dict__.keys():
            return self.dag.__dict__[id]

        return None

    def __str__(self) -> str:
        return self.info.name
