from setuptools import setup, find_packages

setup(
    name='c_elegans_lineage',                # Package name (used in pip)
    version='0.1.0',                         # Initial version
    packages=find_packages(),                # Auto-detects your package folder(s)
    install_requires=[                       # Dependencies
        'networkx',
        'matplotlib',
        'imageio'
    ],
    entry_points={                           # Defines CLI command
        'console_scripts': [
            'lineage-cli = c_elegans_lineage.lineage_cli:main'
        ]
    },
    author='Your Name',
    description='Toolkit for modeling and visualizing C. elegans cell lineage trees.',
    python_requires='>=3.8',
)

