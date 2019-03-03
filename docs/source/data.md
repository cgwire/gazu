## Available data

### Model instances as dict

To make things simple and allow easy interoperability, all model instances are
returned as Python dicts. When you perform a query through the client you
retrieve either a list of dicts or a dict depending on the query.

### Date format


### Common fields

Each model instance provides at least the same three fields:

* id: a unique id made of letters, hyphens and numbers
* type: the model instance type
* created\_at: the creation date
* updated\_at: the update date

### Models

Here is the list of all available data tables (and related fields) you can
access through the Python client:

* Assets (constituants of a shot scene)
    * name
    * code: Utility field for the pipeline to identify the asset
    * description: Asset Brief
    * canceled: True if the asset has been delete one time.
    * project\_id: Project ID
    * entity\_type\_id: Asset type ID
    * source\_id: Field uset to set the episode\_id
    * preview\_file\_id: ID of preview file used as thumbnail
    * data: Free JSON field to add metadata
    * shotgun\_id: Used for synchronization with a Shotgun instance

* Asset instances (asset instance are instances of an asset in a layout scene)
    * asset\_id: Instantiated asset
    * number
    * name (try to not use this field)
    * description
    * active: True if 
    * data: Free JSON field to add metadata
    * scene\_id: target scene
    * target\_asset\_id: Use when instantiating an asset in an asset is required.

* Asset types
    * name

* Comments
    * object\_id: Unique ID of the commented model instance
    * object\_type: Model type of the comment model instance
    * text
    * task\_status\_id: Task status attached to comment
    * person\_id: The person who publishes the comment
    * previews: previews atached to the comment
    * data: Free JSON field to add metadata
    * shotgun\_id: Used for synchronization with a Shotgun instance

* Episodes
    * name
    * code: Utility field for the pipeline to identify the episode
    * description: Episode brief
    * canceled: True if the episode has been deleted one time.
    * project\_id: Project ID
    * source\_id: Field uset to set the episode\_id
    * preview\_file\_id: ID of preview file used as thumbnail
    * data: Free JSON field to add metadata
    * shotgun\_id: Used for synchronization with a Shotgun instance

* Events
    * name
    * user\_id: the user who made the action that emitted the event.
    * data: Free JSON field to add event data

* File status
    * name
    * color

* Metadata
    * project\_id: project for which metadata are added
    * entity\_type: 'Asset' or 'Shot'
    * name: Field name for GUI
    * field\_name: Technical field name
    * choices: Array of string that represents the available values for this metada (this metatada is considered as a free field if this array is empty).

* Notifications
    * read: True if user read it.
    * person\_id: The user to who the notification is aimed at.
    * change: True if there is status change related to this status
    * author\_id: Author of the event to notify
    * comment\_id: Comment related to the notification, if there is any.
    * task\_id: Task related to the notification if there is any.

* Output files
    * name 
    * extension
    * revision
    * size
    * checksum
    * description
    * comment
    * representation: to tell what kind of output it is (abc, jpgs, pngs, etc.)
    * nb\_elements: For image sequence
    * source: created by a script, a webgui or a desktop gui.
    * path: File path on the production hard drive
    * data: Free JSON field to add metadata
    * file\_status\_id
    * entity\_id: Asset or Shot concerned by the output file
    * task\_type\_id: Task type relate to this output file (modeling, animation, etc.)
    * output\_type\_id: Type of output (geometry, cache, etc.)
    * person\_id = Author of the file
    * source\_file\_id = Working file that led to create this output file
    * temporal\_entity\_id = Shot, scene or sequence, needed for output files related to an asset instance.
	
* Output types
	* name 
	* short\_name 
* Persons
    * email: Serve as login
    * desktop\_login: Login used on the desktop
    * first\_name
    * last\_name 
    * phone
    * active: If the person is still in the studio or not
    * last\_presence: Last time the person worked for the studio
    * shotgun\_id: Used for synchronization with a Shotgun instance
    * timezone
    * locale
    * role
    * has\_avatar: True if user has an avatar
    * data: Free JSON field to add metadata

* Playlists
	* name 
    * shots: JSON field describing shot and preview listed in the playlist
    * project\_id
    * episode\_id 

* Preview files
    * name
    * revision
    * extension: file extension
    * description
    * path: File path on the production hard drive
    * source: Webgui, desktop, script
    * annotations: Coordinates to display annotations in the preview player.
    * task\_id: task related to the preview file
    * person\_id: Autho of the preview
    * source\_file\_id: Working file that generated this preview
    * shotgun\_id: Used for synchronization with a Shotgun instance

* Projects
    * name
    * code
    * project\_status\_id
    * team: List of person working on the project
    * description
    * file\_tree: templates to use to build file paths
    * has\_avatar: True if project has an avatar
    * data: Free JSON field to add metadata
    * fps
    * ratio
    * resolution
    * production\_type: short, featurefilm or tvshow
    * shotgun\_id: Used for synchronization with a Shotgun instance

* Search filters
    * list\_type
    * entity\_type
    * name
    * search\_query
    * person\_id
    * project\_id
 
* Sequences 
    * name
    * code: Utility field for the pipeline to identify the asset
    * description: Sequence Brief
    * canceled: True if the asset has been delete one time.
    * project\_id: Project ID
    * parent\_id: Episode ID
    * source\_id: Field uset to set the episode\_id
    * preview\_file\_id: ID of preview file used as thumbnail
    * data: Free JSON field to add metadata
    * shotgun\_id: Used for synchronization with a Shotgun instance

* Shots
    * name
    * code: Utility field for the pipeline to identify the asset
    * description: Shot Brief
    * canceled: True if the asset has been delete one time.
    * project\_id: Project ID
    * parent\_id: Episode ID
    * entity\_type\_id: Shot type ID
    * source\_id: Field uset to set the episode\_id
    * preview\_file\_id: ID of preview file used as thumbnail
    * data: Free JSON field to add metadata
    * shotgun\_id: Used for synchronization with a Shotgun instance

* Software
    * name
    * short\_name
    * file\_extension: Main extension used for this software files
    * secondary\_extensions: Other extensions used for this software files

* Subscriptions to notifications
    * person\_id
    * task\_id
    * entity\_id
    * task\_type\_id
 
* Tasks
    * shotgun\_id: Used for synchronization with a Shotgun instance

* Task status
    * name
    * short\_name
    * color
    * is\_done
    * is\_artist\_allowed
    * is\_retake
    * shotgun\_id: Used for synchronization with a Shotgun instance
 
* Task types
    * name
    * short\_name
    * color
    * priority
    * allow\_timelog
    * for\_shots
    * for\_entity
    * shotgun\_id: Used for synchronization with a Shotgun instance
 
* Time spents
    * duration
    * date
    * task\_id: Related task
    * person\_id: The person who performed the working time
 
* Working files
    * name
    * description
    * comment
    * revision
    * size
    * checksum
    * path: File path on the production hard drive
    * task\_id: Task for which the working file is made for
    * entity\_id: Entity for which the working is made for
    * person\_id: File author
    * software\_id: Sofware used to build this working file
    * outputs: List of output files generated from this working file
    * data: Free JSON field to add metadata
