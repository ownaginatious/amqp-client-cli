[![PyPI Version](https://badge.fury.io/py/amqp-client-cli.svg)](https://pypi.org/project/amqp-client-cli/)
[![Supported Versions](https://img.shields.io/pypi/pyversions/amqp-client-cli.svg)](https://pypi.org/project/amqp-client-cli)

# amqp-client-cli
A simple CLI tool for sending amqp messages to exchanges.

## What is the purpose of `amqp-client-cli`?

The purpose of this command line tool is to make sending messages to exchanges as simple as possible. Uses include:

- In `cron` scripts that periodically send simple messages to an `ampq` server for workers to pick up.
- Unit testing during implementation of an `amqp` system into a workflow.
- Simple one-off queue messages where anything more than a simple command line tool is a hassle to use.

## What does `amqp-client-cli` **not** do?

This tool is **not** intended for configuration. It assumes your entire infrastructure is already in place. It can **only** send to existing exchanges and vhosts and provide a routing key.

It is up to you to configure your infrastructure elsewhere before using this tool (i.e. through your queue workers, through something like `rabbitmqadmin`, through a web management console. etc).

## How do I get it?

Install via pip:

```
pip install amqp_client_cli
```

## How do I use it?

`amqp-client-cli` is run via the `amqpcli` command. Run the `help` subcommand to see the list of options:

```
$ amqpcli --help
usage: amqpcli [-h] {send,config} ...

A command line interface for interacting with amqp exchanges

positional arguments:
  {send,config}
    send         Send a message to an exchange.
    config       Configure the amqpcli client.

optional arguments:
  -h, --help     show this help message and exit
```

### Let's send a message!

Sending messages can be done using the `amqpcli send` command.

```
$amqpcli send --help
usage: amqpcli send [-h] [-n] (-m MESSAGE | -f FILE_PATH) [-p] [-s] [-u USER] [-v VHOST]
                    host port exchange routing_key

positional arguments:
  host                  Address of the amqp server.
  port                  Port of the amqp server.
  exchange              Name of the exchange being sent to.
  routing_key           The routing key for the message.

optional arguments:
  -h, --help            show this help message and exit
  -n, --nocolor         Do not colorize output.
  -m MESSAGE, --message MESSAGE
                        String to use as the message body.
  -f FILE_PATH, --file-path FILE_PATH
                        Path of a file to use as the message body.
  -p, --persistent      Make the message persistent if routed to a durable queue.
  -s, --ssl             Use ssl/tls as the connection protocol.
  -u USER, --user USER  User to connect to the queue as.
  -v VHOST, --vhost VHOST
                        The vhost to connect to.
```

Let's assume we have a [RabbitMQ](https://www.rabbitmq.com) server listening at `localhost:5671` with an exchange we would like to send a message to named `exchange_a` on a vhost `my_vhost` with a routing key of `simple_message`. We are going to send via the `guest` user.

#### Let's define our message on the command line!

```
$ amqpcli send localhost 5671 exchange_a simple_message -m "Hello there" -v my_vhost -s
User: guest
Password:
Connecting to queue @ localhost:5671... SUCCESS!
Message successfully published to exchange [exchange_a]!
```

#### Let's define our message as a file!

The message body can also be a file. It will be interpreted as binary.

**Warning:** Although *any* binary content can be sent, it is **not** recommended to insert large payloads into the queue for performance reasons.

```bash
$ echo "I'm a message in a file" > my_message.txt
```
```
$ amqpcli send localhost 5671 exchange_a simple_message -f my_message.txt -v my_vhost -s
User: guest
Password:
Connecting to queue @ localhost:5671... SUCCESS!
Message successfully published to exchange [exchange_a]!
```

### How can I specify credentials/configurations for a script?

You can optionally add user credentials to a config file for use with the tool (`~/.amqpclirc`). There is no limit to the number of users that can be added.

Configuration options can be seen from the command line.

```
$ amqpcli config --help
usage: amqpcli config [-h] {add_user,delete_user,list_users} ...

positional arguments:
  {add_user,delete_user,list_users}
    add_user            Add a new queue user to config or edit an existing one.
    delete_user         Delete an existing user from the config.
    list_users          List existing users in config.

optional arguments:
  -h, --help            show this help message and exit
```

With `add_user`, you will be prompted for a username, password, and vhost (default is `/`).

A user can also be specified in the environment variables by defining `AMQP_USER`, `AMQP_PASSWORD`, and `AMQP_VHOST`.

```
$ amqpcli config add_user
User: guest
Password:
vhost? [/]: my_vhost
$ amqpcli send localhost 5671 exchange_a simple_message -m "Hello there" -u guest
Connecting to queue @ localhost:5671... SUCCESS!
Message successfully published to exchange [exchange_a]!
```
