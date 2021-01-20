import argparse
import os
import ssl
import sys
from getpass import getpass

import pika
from colorama import Fore
from colorama import init as color_init
from configobj import ConfigObj

CONFIG_FILE_PATH = os.path.expanduser("~/.amqpclirc")
if os.path.exists(CONFIG_FILE_PATH):
    USER_MAP = ConfigObj(infile=CONFIG_FILE_PATH, encoding="utf8")
else:
    USER_MAP = ConfigObj(encoding="utf8")
    USER_MAP.filename = CONFIG_FILE_PATH


def amqp_send(
    host,
    port,
    exchange,
    routing_key,
    message,
    file_path,
    user,
    persistent,
    vhost,
    ssl_,
):
    try:
        if not user:
            user = input(f"{Fore.GREEN}User: {Fore.RESET}")
        password = get_password(user)
        vhost = vhost or get_vhost(user)
    except KeyboardInterrupt:
        print_failure("\nTerminated from keyboard.")
        sys.exit(1)

    properties = pika.BasicProperties(delivery_mode=2 if persistent else 1)
    credentials = pika.PlainCredentials(user, password)
    sys.stdout.write(f"Connecting to queue @ {host}:{port}... ")
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                ssl_options=pika.SSLOptions(context=ssl.create_default_context())
                if ssl_
                else None,
                virtual_host=vhost,
                credentials=credentials,
            )
        )
    except pika.exceptions.AMQPError as e:
        print_failure("FAILED!", out=sys.stdout)
        print_failure(f"Failure reason: {repr(e)}")
        sys.exit(1)

    print_success("SUCCESS!")

    if message:
        body = message.encode("utf-8")
    else:
        with open(file_path, "rb") as f:
            body = f.read()
    channel = connection.channel()
    try:
        channel.basic_publish(
            exchange=exchange, routing_key=routing_key, body=body, properties=properties
        )
    finally:
        channel.close()
    print_success(f"Message successfully published to exchange [{exchange}]!")


def add_user():
    new_user = input(f"{Fore.GREEN}User: {Fore.RESET}")
    new_pass = getpass(f"{Fore.GREEN}Password: {Fore.RESET}")
    new_vhost = input(f"{Fore.GREEN}vhost? [/]: {Fore.RESET}") or "/"
    USER_MAP["users"] = USER_MAP.get("users", {})
    USER_MAP["users"][new_user] = {}
    USER_MAP["users"][new_user]["vhost"] = new_vhost
    USER_MAP["users"][new_user]["password"] = new_pass
    USER_MAP.write()


def delete_user(user):
    users = USER_MAP.get("users", {})
    if user not in users:
        print_failure(f"No such user '{user}' configured.")
        sys.exit(1)
    del users[user]
    USER_MAP.write()
    print_success(f"Configuration for user '{user}' deleted.")


def list_users():
    users = USER_MAP.get("users", {})
    for user in sorted(users.keys()):
        print_success(user)


def get_password(user):
    password = os.getenv("AMQP_PASSWORD", None)
    if password:
        return password
    user_record = USER_MAP.get("users", {}).get(user, None)
    if user_record:
        return user_record["password"]
    return getpass(f"{Fore.GREEN}Password: {Fore.RESET}")


def get_vhost(user):
    vhost = os.getenv("AMQP_VHOST", None)
    if vhost:
        return vhost
    user_record = USER_MAP.get("users", {}).get(user, None)
    if user_record:
        return user_record["vhost"]
    return "/"


def print_failure(message, out=sys.stderr):
    out.write(f"{Fore.RED}{message}{Fore.RESET}\n")


def print_success(message):
    sys.stdout.write(f"{Fore.GREEN}{message}{Fore.RESET}\n")


def add_no_colorize(parser):
    parser.add_argument(
        "-n",
        "--nocolor",
        action="store_true",
        default=False,
        help="Do not colorize output.",
    )


def main():
    parser = argparse.ArgumentParser(
        description="A command line interface for interacting with amqp exchanges"
    )
    subparsers = parser.add_subparsers(required=True, dest="operation")

    # Send

    send_parser = subparsers.add_parser("send", help="Send a message to an exchange.")
    add_no_colorize(send_parser)
    send_parser.add_argument("host", help="Address of the amqp server.")
    send_parser.add_argument("port", type=int, help="Port of the amqp server.")
    send_parser.add_argument("exchange", help="Name of the exchange being sent to.")
    send_parser.add_argument("routing_key", help="The routing key for the message.")
    group = send_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-m", "--message", help="String to use as the message body.")
    group.add_argument(
        "-f", "--file-path", help="Path of a file to use as the message body."
    )
    send_parser.add_argument(
        "-p",
        "--persistent",
        action="store_true",
        help="Make the message persistent if routed to a durable queue.",
    )
    send_parser.add_argument(
        "-s",
        "--ssl",
        action="store_true",
        help="Use ssl/tls as the connection protocol.",
    )
    send_parser.add_argument(
        "-u",
        "--user",
        default=os.getenv("AMQP_USER"),
        help="User to connect to the queue as.",
    )
    send_parser.add_argument("-v", "--vhost", help="The vhost to connect to.")
    send_parser.set_defaults(
        func=lambda args: amqp_send(
            args.host,
            args.port,
            args.exchange,
            args.routing_key,
            args.message,
            args.file_path,
            args.user,
            args.persistent,
            args.vhost,
            args.ssl,
        )
    )

    # Config

    config_parser = subparsers.add_parser(
        "config", help="Configure the amqpcli client."
    )
    cfg_subparsers = config_parser.add_subparsers(required=True, dest="operation")

    add_user_parser = cfg_subparsers.add_parser(
        "add_user", help="Add a new queue user to config or edit an existing one."
    )
    add_no_colorize(add_user_parser)
    add_user_parser.set_defaults(func=lambda _: add_user())

    delete_user_parser = cfg_subparsers.add_parser(
        "delete_user", help="Delete an existing user from the config."
    )
    delete_user_parser.add_argument("user", help="User to delete.")
    add_no_colorize(delete_user_parser)
    delete_user_parser.set_defaults(func=lambda args: delete_user(args.user))

    list_users_parser = cfg_subparsers.add_parser(
        "list_users", help="List existing users in config."
    )
    add_no_colorize(list_users_parser)
    list_users_parser.set_defaults(func=lambda _: list_users())

    args = parser.parse_args()
    if args.nocolor:
        Fore.GREEN, Fore.RED, Fore.RESET = "", "", ""

    args.func(args)


if __name__ == "__main__":
    main()
