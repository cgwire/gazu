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

* person:new
* person:update
* person:deletetion
* notifications:new
* project:update
* metadata-descriptor:new
* metadata-descriptor:update
* metadata-descriptor:delete
* asset-type:new
* asset:new
* asset:update
* asset:delete
* asset:new-link
* asset:remove-link
* asset:deletion
* casting:update
* asset_instance:new
* asset_instance:add-to-shot
* asset_instance:remove-from-shot
* asset_instance:new
* shot:new
* shot:update
* shot:deletion
* scene:new
* scene:deletion
* sequence:new
* episode:new
* task:new
* task:update
* task:deletion
* task_type:new
* task:unassign
* task:assign
* task:start
* task:to-review
* task_status:new
* task_status:update
* comment:new
* comment:deletion
* preview:add
* preview-file:set-main
* working_file:new
* output_file:new
* preview_file:deletion
