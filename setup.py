from setuptools import setup, find_packages

def get_long_description():
    with open('README.md') as f:
        return f.read()

setup(
    name='sql-runner',
    version='0.2.9',

    description="LEROI SQL runner",
    long_description=get_long_description(),
    long_description_content_type='text/markdown',

    python_requires='~=3.6',

    install_requires=[
        'networkx==2.2',
        'pydot==1.4.1',
        'graphviz==0.10.1',
        'pythondialog'
    ],

    dependency_links=[
    ],

    extras_require={
        's3': ['boto3'],
        'snowflake': ['snowflake-connector-python==2.0.4'],
        'redshift': ['psycopg2-binary'],
        'postgres': ['psycopg2-binary'],
        'azuredwh': ['pyodbc']
    },

    packages=find_packages(),

    author='sql-runner contributors',
    license='Apache 2.0',

    entry_points={
        'console_scripts': [
            'runner = src.runner:main',
            # legacy
            'sqlrunner = src.runner:main',
            # Interactive
            'run_sql = src.run_sql:main'
        ],
    }
)