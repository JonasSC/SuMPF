# -*- coding: utf-8 -*-
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.append(os.path.abspath(".."))

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = "1.0"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = ["sphinx.ext.autodoc",
              "sphinx.ext.doctest",
              "sphinx.ext.githubpages",
              "sphinx.ext.graphviz",
              "sphinx.ext.intersphinx",
              "sphinx.ext.mathjax",
              "matplotlib.sphinxext.plot_directive"]
autoclass_content = "both"
intersphinx_mapping = {"python": ("https://docs.python.org/3", None),
                       "numpy": ("https://docs.scipy.org/doc/numpy", None),
                       "connectors": ("https://connectors.readthedocs.io/en/latest", None),
                       "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
                       "soundfile": ("https://pysoundfile.readthedocs.io/en/latest", None),
                       "numexpr": ("https://numexpr.readthedocs.io/en/latest", None),
                       "jack": ("https://jackclient-python.readthedocs.io/en/latest", None),
                       "setuptools": ("https://setuptools.readthedocs.io/en/latest", None),
                       "pytest": ("https://docs.pytest.org/en/latest", None),
                       "pytest-cov": ("https://pytest-cov.readthedocs.io/en/latest", None),
                       "hypothesis": ("https://hypothesis.readthedocs.io/en/latest", None),
                       "flake8": ("http://flake8.pycqa.org/en/latest/", None),
                       "sphinx": ("http://www.sphinx-doc.org/en/master", None),
                       "sphinx_rtd_theme": ("https://sphinx-rtd-theme.readthedocs.io/en/latest", None),
                       "matplotlib": ("https://matplotlib.org", None)}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "SuMPF"
copyright = "2018-2021, Jonas Schulte-Coerne"
author = "Jonas Schulte-Coerne"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = "0.17"
# The full version, including alpha/beta/rc tags.
release = "0.17 snapshot"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# If true, the references in the documentation are checked
nitpicky = True

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "SuMPFDoc"

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ("letterpaper" or "a4paper").
    #
    # "papersize": "letterpaper",

    # The font size ("10pt", "11pt" or "12pt").
    #
    # "pointsize": "10pt",

    # Additional stuff for the LaTeX preamble.
    #
    # "preamble": "",

    # Latex figure (float) alignment
    #
    # "figure_align": "htbp",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "SuMPF.tex", u"SuMPF Documentation",
     u"Jonas Schulte-Coerne", "manual"),
]

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, "SuMPF", u"SuMPF Documentation",
     [author], 1)
]

# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, "SuMPF", u"SuMPF Documentation",
     author, "SuMPF", "A signal processing package with a focus on acoustics",
     "Miscellaneous"),
]
