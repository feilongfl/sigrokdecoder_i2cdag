import yaml
import os
import logging
from enum import Enum

LOGGER = logging.getLogger(__name__)


class YAMLObject():
    def __init__(self, ymlObj: dict = {}, file=None, parent=None) -> None:
        if(file != None):
            with open(os.path.relpath(file)) as f:
                ymlObj = yaml.safe_load(f)

        self.parent = parent

        for k, v in ymlObj.items():
            match v:
                case dict():
                    LOGGER.debug(f"dict  : k={k}, t={type(v)}, v={v}")
                    if k not in self.__dict__.keys():
                        self.__dict__[k] = self.__class__(v, parent=self)

                case list():
                    LOGGER.debug(f"list  : k={k}, t={type(v)}, v={v}")
                    if k not in self.__dict__.keys():
                        self.__dict__[k] = []

                    for item in v:
                        self.__dict__[k].append(
                            self.__class__(item, parent=self))

                case _:
                    if(k == 'include'):
                        LOGGER.info(f"include yml file: {v}")
                        dir = os.path.dirname(os.path.realpath(__file__))
                        file = os.path.join(dir, 'devices', v)

                        for k, v in self.__class__(file=file, parent=self).items():
                            self.__dict__[k] = v
                    else:
                        LOGGER.debug(f"others: k={k}, t={type(v)}, v={v}")
                        self.__dict__[k] = v

    def __repr__(self) -> str:
        return yaml.dump(self.__dict__)

    def items(self):
        return self.__dict__.items()


class PageChanging(Enum):
    IDLE = 1
    PAGE = 2
    PUT = 3


class DAGObject(YAMLObject):
    SELF_PAGECHANGING_STATE = ['idle', 'waitPage', 'waitPut']

    def __init__(self, ymlObj: dict = {}, file=None, parent=None) -> None:
        super().__init__(ymlObj, file, parent)

        if 'info' in self.__dict__:
            if 'longname' not in self.info.__dict__:
                self.info.__dict__['longname'] = self.info.name

        if 'page' not in self.__dict__:
            self.page = None

        self.page_changing = PageChanging.IDLE

    def getName(self):
        if self.page_changing == PageChanging.PAGE:
            return ['PageChange']
        elif self.page_changing == PageChanging.PUT:
            self.page_changing = PageChanging.IDLE
            return ['PageChange: %s' % self.page.current, '%s' % self.page.current]

        return [self.info.longname, self.info.name]

    def nextDag(self):
        next = self.parent.parent
        next = next.parent if 'dag' not in next.__dict__.keys() else next

        return next.getDAG(self.id+1)

    def getDAG(self, id):
        ret = None

        if self.page != None:
            if self.page_changing == PageChanging.PAGE:
                self.setPage(id)
                self.page_changing = PageChanging.PUT
                return self
            elif self.page.address == id:
                self.page_changing = PageChanging.PAGE
                return self

        if 'dag' not in self.__dict__.keys():
            return None

        if id in self.dag.__dict__.keys():
            if self.page == None:
                ret = self.dag.__dict__[id]
            else:
                try:
                    ret = self.dag.__dict__[id].__dict__[self.page.current]
                except:
                    ret = None

            if ret != None:
                ret.id = id

        return ret

    def setPage(self, page) -> None:
        if self.page != None:
            self.page.current = page & self.page.mask
        else:
            logging.warning(f"DAG [{self}] not support setPage")

    def getDAGkeys(self):
        if 'dag' in self.__dict__:
            return self.dag.__dict__.keys()
        else:
            return []

    def __str__(self) -> str:
        return self.info.name
