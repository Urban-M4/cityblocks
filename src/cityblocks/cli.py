import click

@click.group()
def cli():
    pass

@cli.command()
def download():
    click.echo('Downloading dataset')

@cli.command()
def extract():
    click.echo('Extracing area')

@cli.command()
def convert():
    click.echo("Converting dataset to input for QGIS")
