.. figure:: https://gazu.cg-wire.com/_images/gazu.png
   :alt: Gazu Logo


Gazu, Python client for the Kitsu API 
=====================================

Gazu is a Python client that allows to fetch data easily from your animation
production environment (tasks, shots, assets, casting and dependencies).
More than giving access to data, it allows to perform operations like
generating file paths, marking a task as started, setting a thumbnail on
a shot and many more. To make it short, it will boost your pipeline
tools!

It is made to be used with the `Zou API <https://zou.cg-wire.com>`__. It
requires an up and running instance of Zou to run properly.

|Build status|

|Slackin badge|

Quickstart
----------

Install Gazu in your application environment via pip:

.. code:: bash

    pip install gazu

The client requires a few extra configuration before being used. It
needs to know where is located the API server and to log in:

.. code:: python

    import gazu

    gazu.set_host("https://zou-server-url/api")
    gazu.log_in("user@yourdomain.com", "password")

Let's finish with an example. Fetch all the open projects:

::

    projects = gazu.project.all_open_projects()

Then jump to the `documentation <https://gazu.cg-wire.com>`__ to see
what features are available!

Documentation
-------------

Documentation is available on a dedicated website:

`https://gazu.cg-wire.com <https://gazu.cg-wire.com>`__


Projects based on Gazu
----------------------

Our community built open-source tools to connect your content creation tools to
your Kitsu instance. They are listed below:

* `Qtazu <https://github.com/Colorbleed/qtazu>`__: Qt Widgets such as a login
  modal.
* `Nagato <https://github.com/eaxum/nagato>`__: Publishing and file versioning
  for Blender.
* `Bamboo <https://github.com/nervYu/Bamboo>`__: Pyside2 widgets to publish
  previews to Kitsu. 
* `Gazu Publisher <https://github.com/cgwire/gazu-publisher>`__: Our work in
  progress publisher tool. 


Contributions
-------------

All contributions are welcome as long as they respect the `C4
contract <https://rfc.zeromq.org/spec:42/C4>`__.

Code must follow the pep8 convention.

Contributors
------------

* @aboellinger (Xilam)
* @BigRoy (Colorbleed)
* @col-one (Allegorithmic)
* @flablog (Les Fées Spéciales)
* @frankrousseau (CGWire) - *maintainer*
* @kguyaux
* @LedruRollin (Xilam)
* @g-Lul (TNZPV)
* @jdrese (HEAJ)
* @pcharmoille (Unit Image)
* @tokejepsen (Bumpybox)
* @tpodeva

About authors
-------------

Gazu is written by CG Wire, a company based in France. We help indie creative
studios to build their pipeline and workflow efficiently.

We apply software craftmanship principles as much as possible. We love
coding and consider that strong quality and good developer experience
matter a lot. Our extensive knowledge allows studios to get better at
managing production and doing software. They can focus more on the artistic
work.

Visit `cg-wire.com <https://cg-wire.com>`__ for more information.

|CGWire Logo|

.. |Build status| image:: https://api.travis-ci.org/cgwire/gazu.svg?branch=master
   :target: https://travis-ci.org/cgwire/gazu
.. |Slackin badge| image:: https://slack.cg-wire.com/badge.svg
   :target: https://slack.cg-wire.com
.. |CGWire Logo| image:: https://zou.cg-wire.com/cgwire.png
   :target: https://cg-wire.com
