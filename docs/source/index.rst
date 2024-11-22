.. Gazu documentation master file, created by
   sphinx-quickstart on Sun Feb  3 14:10:47 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Gazu's documentation!
================================

|logo|

Gazu is a Python client for the Kitsu API. It allows you to fetch your production data easily. 
More than giving access to data, it allows
performing operations, like marking a task as started or setting a
thumbnail on a shot. 

*NB: It requires an up-and-running instance of the Kitsu API to run appropriately.*

Who is it for?
==============

The audience for this Python client is Technical Artists, Technical Directors, 
and Software Engineers from animation/VFX studios. With Gazu, they can augment their tools
with the production data. 

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


Use cases
=========

Here is a non-exhaustive list of use cases that allow Gazu:

* Ensure that every artist's workstations are on the same page when dealing
  with the file system.
* Build a to-do list for artists of the project.
* Get working file paths and output file paths for a given task.
* Get the next available working revision for a given task.
* Manage automatic validation changes.

Sources
=======

The source is available on Github_.

Projects based on Gazu
======================

Our community built open-source tools that connects your CG tools to your
Kitsu instance. They are listed below:

* `Qtazu <https://github.com/Colorbleed/qtazu>`__: Qt Widgets such as a login
  modal.
* `blender-kitsu <https://studio.blender.org/tools/addons/blender_kitsu>`__: A
  Blender add-on made by Blender to publish previews to Kitsu.
* `Bamboo <https://github.com/nervYu/Bamboo>`__: Pyside2 widgets to publish
  previews to Kitsu. 
* `Kitsu Publisher <https://github.com/cgwire/kitsu-publisher-next>`__: Our
  publish tool for Blender and Harmony.


Contents
========


.. toctree::
   :maxdepth: 1

   intro
   data
   examples
   raw
   cache
   events
   specs
   dccutils

Function References
===================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


About authors
=============

Gazu is written by CGWire, a company based in France. We help animation and VFX studios to collaborate better through efficient tooling. We already work with more than 70 studios around the world.

Visit our website_ for more information.

|cgwirelogo|


.. _Github: https://github.com/cgwire/gazu
.. _website: https://www.cgwire.com
.. |logo| image:: gazu.png
.. |cgwirelogo| image:: cgwire.png
