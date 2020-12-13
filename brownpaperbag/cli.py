# -*- coding: utf-8 -*-

"""Console script for brownpaperbag."""
import asyncio
import logging
import sys

import click
from click import ClickException

from brownpaperbag import BpbCommandSession, BpbEventSession


def get_session(ctx, session_event=True):
    """ return an open connection. """
    if session_event:
        gate = BpbEventSession(ctx.obj["host"], ctx.obj["port"], ctx.obj["password"])
    else:
        gate = BpbCommandSession(ctx.obj["host"], ctx.obj["port"], ctx.obj["password"])
    if ctx.obj["verbose"] == 1:
        logging.basicConfig(level=logging.INFO)
    elif ctx.obj["verbose"] == 2:
        logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(gate.connect())
    except (ConnectionError, NotImplementedError) as err:
        raise ClickException(str(err)) from err
    return gate


@click.group()
@click.version_option()
@click.option("--host", envvar="BPB_HOST", prompt=True, help="MyHomeServer1 IP")
@click.option(
    "--port", envvar="BPB_PORT", default=20000, prompt=True, help="MyHomeServer1 port"
)
@click.option(
    "--password",
    envvar="BPB_PASSWORD",
    prompt=True,
    hide_input=True,
    help="OPEN password",
)
@click.option("-v", "--verbose", count=True, help="Verbose mode, can be used twice")
@click.pass_context
def main(ctx, host, port, password, verbose):
    """Console script for brownpaperbag.

    Provides interaction with myhomeserver1
    """
    ctx.ensure_object(dict)
    ctx.obj = {"host": host, "port": port, "password": password, "verbose": verbose}
    return 0


@main.command()
@click.option("--human", is_flag=True, help="Human readable")
@click.pass_context
def event(ctx, human):
    """Subscribe to gateway events."""
    gate = get_session(ctx, True)
    loop = asyncio.get_event_loop()
    statuses = {}
    while True:
        message = loop.run_until_complete(gate.readevent_exploded())
        if not human:
            click.echo(message)
        else:
            (who, what, where) = message
            if who not in statuses.keys():
                statuses[who] = {}
            if where not in statuses[who].keys() or what != statuses[who][where]:
                statuses[who][where] = what
                if who == "1":
                    status = "OFF"
                    if what == "1":
                        status = "ON"
                    click.echo("light %s is %s (%s)" % (where, status, message))
                if who == "2":
                    status = "STOPPED"
                    if what == "1":
                        status = "UP"
                    elif what == "2":
                        status = "DOWN"
                    click.echo("cover %s is %s (%s)" % (where, status, message))


@main.command()
@click.argument("command")
@click.pass_context
def raw(ctx, command):
    """Send raw openwebnet command."""
    gate = get_session(ctx, False)
    loop = asyncio.get_event_loop()
    click.echo(loop.run_until_complete(gate.send_raw(command)))


@main.command()
@click.option(
    "--status", "operation", flag_value="status", default=True, help="Get status"
)
@click.option("--on", "operation", flag_value="on", help="Turn On")
@click.option("--off", "operation", flag_value="off", help="Turn Off")
@click.argument("id")
@click.pass_context
def light(ctx, operation, light_id):
    """Interact with a light."""
    gate = get_session(ctx, True)
    loop = asyncio.get_event_loop()
    if operation == "on":
        loop.run_until_complete(gate.turn_on_light(light_id))
    elif operation == "off":
        loop.run_until_complete(gate.turn_off_light(light_id))

    if loop.run_until_complete(gate.is_light_on(light_id)):
        click.echo("ON")
    else:
        click.echo("OFF")


@main.command()
@click.option(
    "--status", "operation", flag_value="status", default=True, help="Get status"
)
@click.option("--up", "operation", flag_value="up", help="Open")
@click.option("--down", "operation", flag_value="down", help="Close")
@click.option("--stop", "operation", flag_value="stop", help="Stop")
@click.argument("cover_id")
@click.pass_context
def cover(ctx, operation, cover_id):
    """Interact with a cover."""
    gate = get_session(ctx, False)
    loop = asyncio.get_event_loop()
    if operation == "up":
        loop.run_until_complete(gate.open_cover(cover_id))
    elif operation == "down":
        loop.run_until_complete(gate.close_cover(cover_id))
    elif operation == "stop":
        loop.run_until_complete(gate.stop_cover(cover_id))

    click.echo(loop.run_until_complete(gate.get_cover_state(cover_id)))


@main.command("list")
@click.option("--lights/--no-lights", default=True, help="Include lights")
@click.option("--covers/--no-covers", default=True, help="Include covers")
@click.pass_context
def list_devices(ctx, lights, covers):
    """List known devices."""
    gate = get_session(ctx, False)
    loop = asyncio.get_event_loop()
    if lights:
        click.echo("Lights: ")
        bpb_lights = loop.run_until_complete(gate.get_light_ids())
        for index, value in bpb_lights.items():
            click.echo("%s: %s" % (index.rjust(5), value))
    if covers:
        click.echo("Covers: ")
        bpb_covers = loop.run_until_complete(gate.get_cover_ids())
        for index, value in bpb_covers.items():
            click.echo("%s: %s" % (index.rjust(5), value))


if __name__ == "__main__":
    # pylint: disable=unexpected-keyword-arg,no-value-for-parameter
    sys.exit(main(auto_envvar_prefix="BPB", obj={}))
