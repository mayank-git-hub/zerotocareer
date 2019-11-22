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
	# Add the variables here

	return  # Put the return statement here

@main.command()
@click.option('-var1', '--var1', help='Variable 1', required=True)
def test_case_2(var1):

	# Square
	return


@main.command()
@click.option('-var1', '--var1', help='Variable 1', required=True)
@click.option('-var2', '--var2', help='Variable 2', required=True)
def test_case_3(var1, var2):

	# Power
	return


if __name__ == "__main__":

	main()
