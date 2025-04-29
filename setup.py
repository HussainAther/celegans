from setuptools import setup, find_packages

# Read in your README.md for long description (optional but recommended)
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='c_elegans_lineage',                      # Project name
    version='0.1.0',                                # Version
    packages=find_packages(),                      # Automatically find package modules
    install_requires=[                             # Required dependencies
        'networkx',
        'matplotlib',
        'imageio'
    ],
    entry_points={                                 # CLI command mapping
        'console_scripts': [
            'lineage-cli = c_elegans_lineage.lineage_cli:main'
        ]
    },
    author='Your Name',                             # Author name
    author_email='your.email@example.com',          # Author email
    description='🧬 CLI Toolkit for Modeling and Visualizing C. elegans Lineage Trees',
    long_description=long_description,             # Pull long desc from README.md
    long_description_content_type="text/markdown", # This tells PyPI it's Markdown
    url='https://github.com/yourusername/c_elegans_lineage',  # Your project GitHub (optional now)
    classifiers=[                                  # PyPI classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
    python_requires='>=3.8',
    license='MIT',                                  # Specify license
)

