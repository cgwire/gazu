# Events

## Configuration

It's possible to listen to events and run a callback when it occurs. Because listening to events blocks the current thread, we recommend that you
set it up in a different thread than the main one.

```python
def my_callback(data):
    print("Asset created %s" % data["asset_id"])

event_client = gazu.events.init()
gazu.events.add_listener(event_client, "asset:new", my_callback)
gazu.events.run_client(event_client)
```

## Available events

### Generic events

For each model listed in the *Available data section*, there are three events 
available: `new`, `update` and `delete`. The event is created that way: 

```
model_name.lower().replace(' ', '-') + ':' + action
```

Exemples:

* asset:new
* asset:update
* asset:delete
* task-type:new
* task-type:update
* task-type:delete

Data: 

All generic events provide the ID of related data.


### Special events

Some actions on the database require to generate a special event. Here is the
list of events generated that way:

* asset-instance:add-to-shot
* asset-instance:remove-from-shot
* preview-file:add-file
* preview-file:set-main
* shot:casting-update
* task:unassign
* task:assign
