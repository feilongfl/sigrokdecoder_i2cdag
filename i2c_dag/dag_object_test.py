from .dag_object import DAGObject
import os
import logging

LOGGER = logging.getLogger(__name__)


def test_dag():
    file = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'dag_demo.yml')
    LOGGER.info(DAGObject(file=file))
