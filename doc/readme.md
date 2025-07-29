# Getting started

First make sure you install all the necessary packages for geqo in your environment. See the instructions in the geqo Readme in the main folder.

To view the site, in a Terminal window, navigate to the `docs-site` directory and run
```
./serve_docs.sh
```
The site will be served at `10.8.0.1.8301`.


# Adding content
Jupyter Book is able to render Jupyter notebooks and MyST markdown files and MyST markdown notebooks.

To add a new page to the site, the table of contents must be updated via editing the YAML file `_toc.yml`. Pay attention to the indentation.
* To add a markdown file as a page to the site with path `qegq/docs-site/new_file.md`, add a new item to the chapters list as shown below. Build the site and check the table of contents to see that you've successfully added the page.
```
chapters:
- file: new_file    .. add this line
```
* To add a new tutorial notebook named `tutorial.ipynb`, put the notebook inside the `docs-site/notebooks` directory, and add a new item to the sections list of the `using_geqo` chapter as shown below. Make sure to check that you can run all the cell in the notebook before building the website. If a cell fails to run, the site will not build. Once you have checked that, build the site again and check the 'Using geqo' section to see if the new notebook has been successfully added.
```
- file: using_geqo
  sections:
  - file: notebooks/tutorial    .. add this line
```

To add a new module to the API reference, go to the corresponding `.rst` file for the parent module in the `api` directory, and then add the name of the new module at the bottom of the file. For example, to add a new module `risk_model.py` under the parent module `algorithms`, add the following to `/api/algorithms.rst`:
```
algorithms
==========

.. automodule:: geqo.algorithms
    :members:
    :undoc-members:
    :show-inheritance:
    :imported-members:

.. autosummary::
   :toctree: .
   :recursive:

   algorithms
   risk_model   .. add this line
```

# Formatting Jupyter Notebooks
Jupyter Book will not render Jupyter Notebooks that lack a title. The first cell in any Jupyter Notebook must therefore be a markdown cell with the desired title.

For Jupyter Book to correctly render the very useful UI feature of a sidebar with hyperlinks to the different sections of your notebook, you should use hashes ('#') to specify sections, subsections, etc. For example, the title should have one hash (#Title), the section headers should have two hashes (##Section 1), the subsections should have three hashes (###Subsection 1.1) and so on.

If you do not follow this convention, the site will still be built, but warning messages will show up in the command line.

# Formatting docstrings in source code
Jupyter Book uses the Sphinx extension Napoleon to render Google- or Numpy-style docstrings.

For how to write Google-style docstrings, see [here](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).

For how to write Numpy-style docstrings, see [here](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html).
