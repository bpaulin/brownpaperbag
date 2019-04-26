# -*- coding: utf-8 -*-

"""Console script for brownpaperbag."""
import sys
import click
import asyncio
from brownpaperbag import BpbGate, SESSION_EVENT


@click.group()
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
@click.pass_context
def main(ctx, host, port, password):
    """Console script for brownpaperbag."""
    gate = BpbGate(host, port, password)
    ctx.ensure_object(dict)
    ctx.obj["GATE"] = gate
    return 0


@main.command()
@click.pass_context
def event(ctx):
    """Subscribe to raw gateway events."""
    gate = ctx.obj["GATE"]
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(gate.command_session(SESSION_EVENT))
    except (ConnectionError, NotImplementedError) as e:
        click.secho(str(e), fg="red")
        return 1

    while True:
        click.echo(loop.run_until_complete(gate.readevent()))


@main.command()
@click.argument("command")
@click.pass_context
def raw(ctx, command):
    """Send raw command."""
    gate = ctx.obj["GATE"]
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(gate.command_session())
    except (ConnectionError, NotImplementedError) as e:
        click.secho(str(e), fg="red")
        return 1

    click.echo(loop.run_until_complete(gate.send_raw(command)))


@main.command()
@click.option("--status", "operation", flag_value="status", default=True)
@click.option("--on", "operation", flag_value="on")
@click.option("--off", "operation", flag_value="off")
@click.argument("id")
@click.pass_context
def light(ctx, operation, id):
    """Interact with a light."""
    gate = ctx.obj["GATE"]
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(gate.command_session())
    except (ConnectionError, NotImplementedError) as e:
        click.secho(str(e), fg="red")
        return 1
    if operation == "on":
        loop.run_until_complete(gate.turn_on_light(id))
    elif operation == "off":
        loop.run_until_complete(gate.turn_off_light(id))

    if loop.run_until_complete(gate.is_light_on(id)):
        click.echo("ON")
    else:
        click.echo("OFF")


@main.command()
@click.option("--status", "operation", flag_value="status", default=True)
@click.option("--up", "operation", flag_value="up")
@click.option("--down", "operation", flag_value="down")
@click.option("--stop", "operation", flag_value="stop")
@click.argument("id")
@click.pass_context
def cover(ctx, operation, id):
    """Interact with a light."""
    gate = ctx.obj["GATE"]
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(gate.command_session())
    except (ConnectionError, NotImplementedError) as e:
        click.secho(str(e), fg="red")
        return 1
    if operation == "up":
        loop.run_until_complete(gate.open_cover(id))
    elif operation == "down":
        loop.run_until_complete(gate.close_cover(id))
    elif operation == "stop":
        loop.run_until_complete(gate.stop_cover(id))

    click.echo(loop.run_until_complete(gate.get_cover_state(id)))


@main.command()
@click.option("--lights/--no-lights", default=True)
@click.option("--covers/--no-covers", default=True)
@click.pass_context
def list(ctx, lights, covers):
    """List known devices."""
    gate = ctx.obj["GATE"]
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(gate.command_session())
    except (ConnectionError, NotImplementedError) as e:
        click.secho(str(e), fg="red")
        return 1
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
    sys.exit(main(auto_envvar_prefix="BPB", obj={}))  # pragma: no cover
