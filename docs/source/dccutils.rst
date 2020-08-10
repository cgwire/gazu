DCC Utils
=========

This library offers a series of classes to abstract the most common features available in Digital Content Creation tools.

It supports Blender, Maya and Houdini. Find below, specifications of already
implemented functions. If you think that something is missing, feel free to
submit a Pull Request and add it.


Installation
------------

Install the library via Pip:

.. code-block:: bash

    pip install dccutils


Usage
-----

Then in your code (let's say you are working in Blender):

.. code-block:: python

    from dccutils import BlenderContext

    dcc_software_manager = BlenderContext()
    print(dcc_software_manager.list_cameras())


Specifications
--------------

.. autoclass:: dccutils.software.SoftwareContext
    :members:
