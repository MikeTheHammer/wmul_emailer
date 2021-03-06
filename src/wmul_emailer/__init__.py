"""
@Author = 'Mike Stanley'

Utility to send an email to multiple addresses.

============ Change Log ============
2022-May-06 = Changed License from MIT to GPLv2.

2018-May-23 = Reworked API to be class based.

2018-May-18 = Imported from Titanium_Monticello

              Fresh start, so no longer need two API endpoints for one function.

2017-Nov-15 = Bugfix for the destination email addresses not being a list.

2017-Nov-14 = Added SendEmailArguments to encapsulate the arguments and send_email2 to consume those arguments.

2017-Jun-27 = Created.

============ License ============
Copyright (c) 2017 Michael Stanley

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
from email.mime.text import MIMEText
from smtplib import SMTP


__all__ = ["EmailSender"]


class EmailSender:

    def __init__(self, server_host, port, user_name, password, from_email_address, destination_email_addresses):
        if not (isinstance(destination_email_addresses, list) or isinstance(destination_email_addresses, tuple)):
            raise TypeError("destination_email_addresses must be a list or tuple.")

        self.server_host = server_host
        self.port = port
        self.user_name = user_name
        self.password = password
        self.from_email_address = from_email_address
        self.destination_email_addresses = destination_email_addresses

    def send_email(self, email_body, email_subject, from_email_address=None, destination_email_addresses=None):
        if destination_email_addresses:
            if not isinstance(destination_email_addresses, list):
                raise TypeError("destination_email_addresses must be a list.")
        else:
            destination_email_addresses = self.destination_email_addresses

        if not from_email_address:
            from_email_address = self.from_email_address

        with SMTP(self.server_host, port=self.port) as server:
            server.login(user=self.user_name, password=self.password)
            for email_address in destination_email_addresses:
                msg = MIMEText(email_body)
                msg['Subject'] = email_subject
                msg['From'] = from_email_address
                msg['To'] = email_address
                server.send_message(msg)
