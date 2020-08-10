.. Gazu documentation master file, created by
   sphinx-quickstart on Sun Feb  3 14:10:47 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Gazu's documentation!
================================

|logo|

Gazu is a Python client for the Kitsu API. It allows fetching easily
your CG production data. More than giving access to data, it allows
performing operations on it like marking a task as started or setting a
thumbnail on a shot. 

*NB: It requires an up and running instance of the Kitsu API to run properly.*

Who is it for?
==============

The audience for this Python client is Technical Artists, Technical Directors
and Software Engineers from CG studios. With Gazu they can augment their tools
with the CG production data. 

Use cases
=========

Here is a non exhaustive list of use cases that allows Gazu:

* Make sure that every artist workstations are on the same page when dealing
  with the file system.
* Build a todo list for artists of the project.
* Get working file paths and output file paths for a given task.
* Get next available working revision for a given task.
* Manage automatic validation changes.

Sources
=======

The source is available on Github_.

Projects based on Gazu
======================

Our community built open-source tools to connect your CG tools to your
Kitsu instance. They are listed below:

* `Qtazu <https://github.com/Colorbleed/qtazu>`__: Qt Widgets such as a login
  modal.
* `Nagato <https://github.com/eaxum/nagato>`__: Publishing and file versioning
  for Blender.
* `Bamboo <https://github.com/nervYu/Bamboo>`__: Pyside2 widgets to publish
  previews to Kitsu. 
* `Gazu Publisher <https://github.com/cgwire/gazu-publisher>`__: Our work in
  progress publisher tool based on Qt.py. 


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
   publisher
   dccutils

Function References
===================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


About authors
=============

Gazu is written by CG Wire, a company based in France. We help small to
midsize CG studios to manage their production efficiently.
We apply software craftmanship principles as much as possible. We love
coding and consider that good developer experience matters.

Visit our website_ for more information.

|cgwirelogo|


.. _Github: https://github.com/cgwire/gazu
.. _website: https://www.cgwire.com
.. |logo| image:: gazu.png
.. |cgwirelogo| image:: cgwire.png
