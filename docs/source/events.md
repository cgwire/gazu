# Events

## Configuration

It's possible to listen to events and run a callback when it occurs. Because listening to events blocks the current thread, we recommend that you
set it up in a different thread than the main one.

```python
gazu.set_event_host("https://kitsu.mystudio.com/socket.io")


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

Some actions on the database generate a special event. Here is the list of
events emitted that way:

* asset-instance:add-to-shot
* asset-instance:remove-from-shot
* organisation:set-thumbnail
* person:set-thumbnail
* project:set-thumbnail
* preview-file:add-file
* preview-file:set-main
* shot:casting-update
* task:unassign
* task:assign
* task:status-changed

## Event table

You can access to most recent events by doing a classic request: 

```
events = gazu.client.get("data/events/last?page_size=100")
events = gazu.client.get("data/events/last?page_size=100&before=2019-02-01")
events = gazu.client.get("data/events/last?page_size=100&before=2019-02-01&after=2019-01-01")
events = gazu.client.get("data/events/last?page_size=100&only_files=true")
```
