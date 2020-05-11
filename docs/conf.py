# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------

project = 'NTR Navigation Unit'
copyright = '2020, NTRobotics'
author = 'Alexander Evdokimov, Andrey Stepanov, Leonid Bulyga'

release = '1.0.0'


# -- General configuration ---------------------------------------------------

master_doc = 'index'

extensions = [
]

templates_path = ['_templates']

language = 'ru'

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']