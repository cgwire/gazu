[![Gazu Logo](/gazu.png)](https://github.com/cgwire/gazu)

# Welcome to the Gazu documentation

Gazu is a Python client that allows to fetch data easily from your CG
production environment. More than giving access to data, it allows to perform
operations like marking a task as started, setting a thumbnail on a shot and
many more. To make it short, it will boost your pipeline tools!

It is made to be used with the [Zou
API](https://github.com/cgwire/cgwire-api). It requires an up and running
instance of Zou to run properly.

The source is available on [Github](https://github.com/cgwire/gazu).


## Who is it for?

The audience for this tool are Technical Artists, Technical Directors and
Software Engineers from CG studios. With Gazu they can augment their tools with the CG production data. 

## Use cases

Here is a non exhaustive list of use cases that allows Gazu:

* Make sure that every artist workstations are on the same page when dealing
  with the file system.
* Build a todo list for artists of the project.
* Publication of files for validation.
* Manage automatic validition changes.

## Install 

Installation is pretty simple and straightforward:

```bash
pip install git+https://github.com/cgwire/cgwire-api-client.git
```

## Configuration 

The client requires a few extra configuration before being used. It needs
to know where is located the API server:

```python
import gazu

gazu.client.set_host("https://zou-server-url")
```

## Usage
 
Jump directly to the usage section to see the many examples of what is possible
to do.

## About authors

Gazu is written by CG Wire, a company based in France. We help small to
midsize CG studios to manage their production and build pipeline efficiently.

We apply software craftmanship principles as much as possible. We love
coding and consider that strong quality and good developer experience matter a lot.
Our extensive experience allows studios to get better at doing software and focus
more on the artistic work.

Visit [cg-wire.com](https://cg-wire.com) for more information.

[![CGWire Logo](/cgwire.png)](https://cgwire.com)
