Specifications
==============

The philosophy behind this client is to allow you to make common
operation as simply as possible. We want to provide helpers to make your
development faster. If you think that one is missing, feel free to ask for
it in the Github issues.
Even better, you can contribute by directly adding it to the code.

The client is divided in multiple modules:

* *asset*: functions related to asset and asset types.
* *cache*: functions related to the cache.
* *casting*: functions related to casting.
* *client*: generic functions to deal with the API.
* *edit*: functions related to edits.
* *entity*: functions related to entities.
* *exceptions*: exceptions raised by Gazu.
* *files*: functions related to file path generation.
* *person*: functions related to studio members.
* *playlist*: functions related to project playlists.
* *project*: functions related to running productions.
* *scene*: functions related to layout scenes (which will lead to shots).
* *shot*: functions related to shots, sequences and episodes.
* *sync*: functions related to sync.
* *task*: functions related to tasks, task types and assignations.
* *user*: functions related to current user data.

In the following, we are going to describe all functions available in the Gazu
client.

gazu
-----------

.. autofunction:: gazu.log_in

.. autofunction:: gazu.get_host

.. autofunction:: gazu.set_host

.. autofunction:: gazu.send_email_otp

.. autofunction:: gazu.log_out

.. autofunction:: gazu.refresh_token

.. autofunction:: gazu.get_event_host

.. autofunction:: gazu.set_event_host

gazu.asset
-----------

.. automodule:: gazu.asset
    :members:

gazu.cache
-------------

.. automodule:: gazu.cache
    :members:

gazu.casting
-------------

.. automodule:: gazu.casting
    :members:

gazu.client
------------

.. automodule:: gazu.client
    :members:

gazu.edit
---------------

.. automodule:: gazu.edit
    :members:


gazu.entity
-----------

.. automodule:: gazu.entity
    :members:

gazu.exceptions
---------------

.. automodule:: gazu.exception
    :members:


gazu.files
----------

.. automodule:: gazu.files
    :members:

gazu.person
-----------

.. automodule:: gazu.person
    :members:

gazu.playlist
-------------

.. automodule:: gazu.playlist
    :members:


gazu.project
------------

.. automodule:: gazu.project
    :members:

gazu.scene
-----------

.. automodule:: gazu.scene
    :members:

gazu.shot
-----------

.. automodule:: gazu.shot
    :members:

gazu.sync
-----------

.. automodule:: gazu.sync
    :members:

gazu.task
-----------

.. automodule:: gazu.task
    :members:

gazu.user
-----------

.. automodule:: gazu.user
    :members: