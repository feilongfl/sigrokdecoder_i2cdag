from .dag_object import DAGObject
import os
import logging
import pydot

LOGGER = logging.getLogger(__name__)


class TestDAGObject:
    def setup_class(self) -> None:
        self.file = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'dag_demo.yml')
        self.dag = DAGObject(file=self.file)
        pass

    def test_dump_yaml(self):
        LOGGER.info(repr(self.dag))

    def test_get_dag_keys(self):
        def pk(dag, pad):
            LOGGER.info("%s %s" % (pad, str(dag)))
            pad += '\t'
            for k in dag.getDAGkeys():
                child = dag.getDAG(k)
                if(child != None):
                    pk(child, pad)

        pk(self.dag, '')

    def test_gen_dag_dot(self):
        graph = pydot.Dot('dag', graph_type='graph')
        root_node = pydot.Node('root', label='root')
        graph.add_node(root_node)

        def pk(dag, parent):
            name = "%s>%s" % (parent, str(dag))
            node = pydot.Node(name, label=str(dag))
            graph.add_node(node)
            graph.add_edge(pydot.Edge(parent, name))

            dag.setPage(0)
            for k in dag.getDAGkeys():
                child = dag.getDAG(k)
                if(child != None and k!='parent'):
                    pk(child, name)

        pk(self.dag, 'root')
        graph.write_dot('dag.dot')
        graph.write_png('dag.png')
