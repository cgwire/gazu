import gazu

gazu.set_host("http://localhost:8080/api")
gazu.set_event_host("http://localhost:8080/")
gazu.log_in("jhon@doe.com", "password")


def my_callback(data):
    print("Task status changed:")
    print(data)


try:
    event_client = gazu.events.init()
    gazu.events.add_listener(event_client, "task:status-changed", my_callback)
    gazu.events.run_client(event_client)
except KeyboardInterrupt:
    print("Stop listening.")
except TypeError:
    print("Authentication failed. Please verify your credentials.")
