# Events

## Configuration

It's possible to listen to events and run a callback when it occurs. Because listening to events blocks the current thread, we recommend that you
set it up in a different thread than the main one.

```python
def my_callback(data):
    print("Asset created %s" % data["asset_id"])

event_client = gazu.events.init()
gazu.events.add_listener(event_client, "new:asset", my_callback)
gazu.events.run_client(event_client)
```

## Available events

* asset:new
* asset:update
* asset:delete
* asset:new-link
* asset:remove-link
* asset:deletion
* asset-type:new
* asset-instance:new
* asset-instance:add-to-shot
* asset-instance:remove-from-shot
* asset-instance:new
* comment:new
* comment:deletion
* casting:update
* episode:new
* metadata-descriptor:new
* metadata-descriptor:update
* metadata-descriptor:delete
* notifications:new
* output-file:new
* person:new
* person:update
* person:deletetion
* preview-file:deletion
* preview:add
* preview-file:set-main
* project:update
* sequence:new
* scene:new
* scene:deletion
* shot:new
* shot:update
* shot:deletion
* task:new
* task:update
* task:deletion
* task-type:new
* task:unassign
* task:assign
* task:start
* task:to-review
* task-status:new
* task-status:update
* working-file:new
