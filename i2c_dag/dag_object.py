import yaml
import os


class YAMLObject():
    def __init__(self, parent: dict = {}, file=None) -> None:
        if(file != None):
            with open(os.path.relpath(file)) as f:
                parent = yaml.safe_load(f)

        for k, v in parent.items():
            match v:
                case dict():
                    print(f"dict  : k={k}, t={type(v)}, v={v}")
                    if k not in self.__dict__.keys():
                        self.__dict__[k] = self.__class__(v)

                case _:
                    print(f"unknow: k={k}, t={type(v)}, v={v}")
                    self.__dict__[k] = v

    def __str__(self) -> str:
        return yaml.dump(self.__dict__)


class DAGObject(YAMLObject):
    def getName(self):
        return [self.info.longname, self.info.name]

    def getDAG(self, id):
        if id in self.dag.__dict__.keys():
            return self.dag.__dict__[id]

        return None

# file = os.path.join(
#     os.path.dirname(os.path.realpath(__file__)), 'dag_demo.yml')

# with open(os.path.relpath(file)) as f:
#     dag: dict = yaml.safe_load(f)

#     dag = DAGObject(dag)
#     print(dag)
