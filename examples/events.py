import gazu

gazu.set_host("https://your-instance.cg-wire.com/api")
gazu.set_event_host("https://your-instance.cg-wire.com")
gazu.log_in("your@email.com", "yourpassword")


def my_callback(event, data):
    print(f"event:{event}")
    print(f"data:{data}")


try:
    event_client = gazu.events.init()
    gazu.events.add_listener(event_client, "*", my_callback)
    gazu.events.run_client(event_client)
except KeyboardInterrupt:
    print("Stop listening.")
except TypeError:
    print("Authentication failed. Please verify your credentials.")
