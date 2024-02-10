.. figure:: https://zou.cg-wire.com/kitsu.png
   :alt: Kitsu Logo


Gazu, Python client for the Kitsu API
=====================================

The Kitsu Python client allows you to fetch data easily from the Kitsu
collaboration platform. With Gazu, you bring assets and shots data into your
pipeline tools. It comes with extra features such as preview publishing and 
event stream listening.

It is made to be used with the `Kitsu API <https://zou.cg-wire.com>`__. It
requires an up-and-running instance of Kitsu to run correctly.

|CI badge| |Discord| |Downloads|

Quickstart
----------

Install Gazu in your application environment via pip:

.. code:: bash

    pip install gazu

The client requires a few extra configurations before being used. It
needs to know where is located the API server and to log in:

.. code:: python

    import gazu

    gazu.set_host("https://zou-server-url/api")
    gazu.log_in("user@yourdomain.com", "password")

Let's finish with an example. Fetch all the open projects:

::

    projects = gazu.project.all_open_projects()


Documentation
-------------

Documentation and specification are available on a dedicated website:

`https://gazu.cg-wire.com <https://gazu.cg-wire.com>`__


Projects using the Kitsu client
-------------------------------

Our community-built open-source tools connect your content creation tools to
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

The code must follow the pep8 convention.

You can use the pre-commit hook for Black (a Python code formatter) before committing :

.. code:: bash

    pip install pre-commit
    pre-commit install


Contributors
------------

* @aboellinger (Xilam)
* @BigRoy (Colorbleed)
* @col-one (Allegorithmic)
* @EvanBldy (CGWire) - *maintainer*
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

Kitsu is written by CGWire, a company based in France. We help animation and VFX studios to collaborate better through efficient tooling. We already work with more than 70 studios around the world.

Visit `cg-wire.com <https://cg-wire.com>`__ for more information.

|CGWire Logo|

.. |CI badge| image:: https://github.com/cgwire/gazu/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/cgwire/gazu/actions/workflows/ci.yml
.. |Discord| image:: https://badgen.net/badge/icon/discord?icon=discord&label
   :target: https://discord.com/invite/VbCxtKN
.. |CGWire Logo| image:: https://zou.cg-wire.com/cgwire.png
   :target: https://cg-wire.com
.. |Downloads| image:: https://static.pepy.tech/personalized-badge/gazu?period=total&units=international_system&left_color=grey&right_color=orange&left_text=Downloads
   :target: https://pepy.tech/project/gazu
