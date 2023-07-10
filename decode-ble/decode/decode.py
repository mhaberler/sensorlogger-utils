import click

# pass_dict = click.make_pass_decorator(dict, ensure=True)


# @click.group()
# @click.option('-d', '--debug', default=False, help="more debugging stuff")
# @click.option( '--repeat', default=1, help="the count")
# @click.pass_context
# def main(ctx, debug):
#     ctx.obj['DEBUG'] = debug

# @main.command()
# @click.pass_context

@click.command()
@click.option('-d', '--debug', default=False, help="more debugging stuff")
@click.argument('out', type=click.File('w'), default='-')
# @click.argument('name')

# def cli(ctx, out):
def cli(debug, out):
    """Say hello name
    """
    if debug:
        print("debug == True")
    print("hello mah")

