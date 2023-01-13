"""
@Author = 'Mike Stanley'

A cli is provided to test that the credentials are functional and that the 
system can send e-mails.

============ Change Log ============
01/13/2023 = Added documentation.

08/10/2022 = Created.

============ License ============
Copyright (C) 2023 Michael Stanley

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
import click
import wmul_emailer


@click.command()
@click.option("--email", type=str, multiple=True, required=True,
              help="The e-mail address to which the results should be sent.")
@click.option("--server", type=str, required=True, help="The hostname or ip address of the smtp server.")
@click.option("--port", type=int, default=25, help="The port number on which the smtp server resides.  ")
@click.option("--username", type=str, required=True, help="The username to authenticate with the smtp server.")
@click.option("--password", type=str, required=True, help="The password to authenticate with the smtp server.")
@click.option("--from_address", type=str, required=True, help="The 'from' e-mail address.")
def send_test_email(email, server, port, username, password, from_address):
    emailer = wmul_emailer.EmailSender(
        server_host=server,
        port=port,
        user_name=username,
        password=password,
        destination_email_addresses=email,
        from_email_address=from_address
    )

    emailer.send_email(
        email_body="This is the test e-mail from wmul_emailer.py. "
                   "If you are reading this, the software is configured correctly.",
        email_subject="Test e-mail from wmul_emailer"
    )
