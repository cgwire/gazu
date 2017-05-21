![Gazu Logo](https://gazu.cg-wire.com/gazu.png)

## Gazu, steroïds for your CG tools

Gazu is a Python client that allows to fetch data easily from your CG production
environment (tasks, shots, assets, casting and dependencies). 
More than giving access to data, it allows to perform operations
like generating file paths, marking a task as started, setting a thumbnail on a
shot and many more. To make it short, it will boost your pipeline tools!

It is made to be used with the [Zou API](https://zou.cg-wire.com). It requires
an up and running instance of Zou to run properly.

### Quickstart

Install Gazu in your application environment via pip:

```bash
pip install git+https://github.com/cgwire/gazu.git
```

or clone this repository in a directory contained in your PYTHONPATH
environment variable.

```bash
git clone https://github.com/cgwire/gazu.git
```

The client requires a few extra configuration before being used. It needs
to know where is located the API server:

```python
import gazu

gazu.client.set_host("https://zou-server-url")
```

Let's finish with an example. Fetch all the open projects:

```
projects = gazu.projects.open_projects()
```

Then jump to the [documentation](https://gazu.cg-wire.com) to see what features are available!


### Documentation

Documentation is available on a dedicated website:

[https://gazu.cg-wire.com/](https://gazu.cg-wire.com)


### About authors

Gazu is written by CG Wire, a company based in France. We help small to
midsize CG studios to manage their production and build pipeline efficiently.

We apply software craftmanship principles as much as possible. We love
coding and consider that strong quality and good developer experience matter a
 lot.
Our extensive experience allows studios to get better at doing software and
 focus
more on the artistic work.

Visit [cg-wire.com](https://cg-wire.com) for more information.

[![CGWire Logo](https://gazu.cg-wire.com/cgwire.png)](https://cg-wire.com)
