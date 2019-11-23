import click
# Put your Imports Here

@click.group()
def main():
	pass


@main.command()
@click.option('-var1', '--var1', help='Variable 1', required=True)
@click.option('-var2', '--var2', help='Variable 2', required=True)
def test_case_1(var1, var2):

	# Sum	

	print()  # Print the results here

@main.command()
@click.option('-var1', '--var1', help='Variable 1', required=True)
def test_case_2(var1):

	# Square
	print()  # Print the results here


@main.command()
@click.option('-var1', '--var1', help='Variable 1', required=True)
@click.option('-var2', '--var2', help='Variable 2', required=True)
def test_case_3(var1, var2):

	# Power
	print()  # Print the results here


if __name__ == "__main__":

	main()
