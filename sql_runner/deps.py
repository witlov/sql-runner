import os
import re

import networkx as nx
from sql_runner.db import get_db_and_query_classes, DB
from sql_runner import parsing
from types import SimpleNamespace
from typing import Set, List, Dict
from functools import lru_cache


class Dependencies:
    def __init__(self, config: SimpleNamespace):
        self.config = config
        print("Parsing queries to determine dependencies")
        self.dependencies: List[Dict[str, str]] = []
        for root, _, file_names in os.walk(config.sql_path):
            if os.path.basename(root) in config.exclude_dependencies:
                continue

            for file_name in file_names:
                if file_name[-4:] != '.sql':
                    continue

                file_path = os.path.normpath(os.path.join(root, file_name))
                with open(file_path, 'r', encoding=getattr(self.config, 'encoding', 'utf-8')) as sql_file:
                    select_stmt = sql_file.read()
                    if select_stmt == '':
                        continue

                dependent_schema = os.path.basename(os.path.normpath(root))
                dependent_table = file_name[:-4]
                # deduplicate sources
                sources = set()
                for query in parsing.Query.get_queries(select_stmt):
                    for source in query.sources:
                        # Ignore sources without a specified schema
                        if source.schema:
                            source_schema = source.schema.lower()
                            source_table = source.relation.lower()
                            sources.add((source_schema, source_table))
                for source_schema, source_table in sources:
                    self.dependencies.append({
                        'source_schema': source_schema,
                        'source_table': source_table,
                        'dependent_schema': dependent_schema,
                        'dependent_table': dependent_table
                    })

    @property
    @lru_cache(maxsize=1)
    def db(self) -> DB:
        dbclass, _ = get_db_and_query_classes(self.config)
        return dbclass(self.config, cold_run=False)

    @property
    @lru_cache(maxsize=1)
    def dag(self) -> nx.MultiDiGraph:
        """Computes a DAG using networkx. Each node is a (schema, table) tuple.
        """
        dependency_tuples = [(f'{item["source_schema"]}.{item["source_table"]}',
                              f'{item["dependent_schema"]}.{item["dependent_table"]}'
                              ) for item in self.dependencies]
        dg = nx.MultiDiGraph()
        edges = [(from_, to_, {'fontsize': 10.0, 'penwidth': 1}) for from_, to_ in dependency_tuples]
        dg.add_edges_from(edges)
        return dg

    def clean_schemas(self, prefix: str):
        """ Drop schemata that have a specific name prefix
        """
        self.db.clean_schemas(prefix)

    def save(self, monitor_schema: str):
        """ Save dependencies list in the database in the `monitor_schema` schema
        """
        if not self.dependencies:
            return
        self.db.save(monitor_schema, self.dependencies)

    def viz(self):
        def lookup(node_name: str, config_attr: str) -> str:
            """ Look up `config_attr` value for the specified `node_name`
            """
            # defaults
            value = {
                'colors': 'white',
                'shapes': 'oval'
            }[config_attr]
            if hasattr(self.config, config_attr):
                for prefix, config_val in getattr(self.config, config_attr).items():
                    if node_name.startswith(prefix):
                        value = config_val
                        break
            return value

        dag = self.dag
        for node in dag.nodes:
            dag.node[node].update({
                'fillcolor': lookup(node, 'colors'),
                'shape': lookup(node, 'shapes'),
                'style': 'filled'
            })
        os.environ["PATH"] += os.pathsep + self.config.graphviz_path
        nx.drawing.nx_pydot.to_pydot(dag).write_svg('dependencies.svg')
        if self.config.s3_bucket:
            import boto3
            s3 = boto3.resource('s3')
            body = open('dependencies.svg', 'rb')
            key = f'{self.config.s3_folder}/dependencies.svg'
            s3.Bucket(self.config.s3_bucket).put_object(Key=key, Body=body)
