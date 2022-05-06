"""
@Author = 'Mike Stanley'

============ Change Log ============
2022-May-06 = Changed License from MIT to GPLv2.

2018-May-18 = Created.

============ License ============
Copyright (c) 2018 Michael Stanley

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
import contextlib
import pytest
import wmul_emailer


@pytest.fixture(scope="function")
def setup_send_email(mocker):
    mock_server = mocker.Mock()

    @contextlib.contextmanager
    def mock_server_function(host, port):
        yield mock_server

    mock_smtp = mocker.patch(
        "wmul_emailer.SMTP",
        mocker.Mock(side_effect=mock_server_function)
    )

    mock_destination_email_addresses = ["foo@example.com", "bar@example.com"]
    mock_host = "mock_host"
    mock_port = "mock_port"
    mock_username = "mock_username"
    mock_password = "mock_password"
    mock_from_address = "mock_from_email_address"

    yield mock_server, mock_smtp, mock_destination_email_addresses, mock_host, mock_port, mock_username, \
          mock_password, mock_from_address


def test_send_email_dest_addresses_not_a_list_or_tuple(setup_send_email):
    mock_server, mock_smtp, mock_destination_email_addresses, mock_host, \
    mock_port, mock_username, mock_password, mock_from_address = setup_send_email

    with pytest.raises(TypeError):
        emailer = wmul_emailer.EmailSender(
            destination_email_addresses="foo",
            server_host=mock_host,
            port=mock_port,
            user_name=mock_username,
            password=mock_password,
            from_email_address=mock_from_address
        )

    mock_smtp.assert_not_called()
    mock_server.assert_not_called()


@pytest.fixture(scope="function", params=[True, False])
def setup_send_email_correctly_created(setup_send_email, mocker, request):
    mock_server, mock_smtp, mock_destination_email_addresses, mock_host, mock_port, mock_username, mock_password, \
        mock_from_address = setup_send_email
    use_tuple_of_addresses = request.param

    if use_tuple_of_addresses:
        mock_destination_email_addresses = tuple(mock_destination_email_addresses)

    emailer = wmul_emailer.EmailSender(
        destination_email_addresses=mock_destination_email_addresses,
        server_host=mock_host,
        port=mock_port,
        user_name=mock_username,
        password=mock_password,
        from_email_address=mock_from_address
    )

    def mock_mimetext_function(data):
        mimetext_contents = {"Body": data}
        return mimetext_contents

    mock_mimetext = mocker.patch(
        "wmul_emailer.MIMEText",
        mocker.Mock(side_effect=mock_mimetext_function)
    )

    mock_body = "mock_body"
    mock_subject = "mock_subject"

    yield emailer, mock_body, mock_subject


def test_send_email_called_correctly_normal_path(mocker, setup_send_email, setup_send_email_correctly_created):
    mock_server, mock_smtp, mock_destination_email_addresses, mock_host, mock_port, mock_username, mock_password, \
        mock_from_address = setup_send_email

    emailer, mock_body, mock_subject = setup_send_email_correctly_created

    emailer.send_email(
        mock_body,
        mock_subject
    )

    mock_smtp.assert_called_once_with(mock_host, port=mock_port)
    mock_server.login.assert_called_once_with(user=mock_username, password=mock_password)

    expected_send_message_calls = []

    for this_email_address in mock_destination_email_addresses:
        this_message = {
            "Body": mock_body,
            "Subject": mock_subject,
            "From": mock_from_address,
            "To": this_email_address
        }
        expected_send_message_calls.append(mocker.call(this_message))

    mock_server.send_message.assert_has_calls(expected_send_message_calls)
    assert mock_server.send_message.call_count == len(mock_destination_email_addresses)


def test_send_email_called_correctly_different_from_address(setup_send_email, mocker,
                                                            setup_send_email_correctly_created):
    mock_server, mock_smtp, mock_destination_email_addresses, mock_host, mock_port, mock_username, mock_password, \
        mock_from_address = setup_send_email

    emailer, mock_body, mock_subject = setup_send_email_correctly_created

    new_mock_from_address = "new_mock_from_address"

    emailer.send_email(
        mock_body,
        mock_subject,
        from_email_address=new_mock_from_address
    )

    mock_smtp.assert_called_once_with(mock_host, port=mock_port)
    mock_server.login.assert_called_once_with(user=mock_username, password=mock_password)

    expected_send_message_calls = []

    for this_email_address in mock_destination_email_addresses:
        this_message = {
            "Body": mock_body,
            "Subject": mock_subject,
            "From": new_mock_from_address,
            "To": this_email_address
        }
        expected_send_message_calls.append(mocker.call(this_message))

    mock_server.send_message.assert_has_calls(expected_send_message_calls)
    assert mock_server.send_message.call_count == len(mock_destination_email_addresses)


def test_send_email_called_correctly_different_destination_address(setup_send_email, mocker,
                                                            setup_send_email_correctly_created):
    mock_server, mock_smtp, mock_destination_email_addresses, mock_host, mock_port, mock_username, mock_password, \
        mock_from_address = setup_send_email

    emailer, mock_body, mock_subject = setup_send_email_correctly_created

    new_mock_destination_addresses = ["new_mock_destination_address_1", "new_mock_destination_address_2"]

    emailer.send_email(
        mock_body,
        mock_subject,
        destination_email_addresses=new_mock_destination_addresses
    )

    mock_smtp.assert_called_once_with(mock_host, port=mock_port)
    mock_server.login.assert_called_once_with(user=mock_username, password=mock_password)

    expected_send_message_calls = []

    for this_email_address in new_mock_destination_addresses:
        this_message = {
            "Body": mock_body,
            "Subject": mock_subject,
            "From": mock_from_address,
            "To": this_email_address
        }
        expected_send_message_calls.append(mocker.call(this_message))

    mock_server.send_message.assert_has_calls(expected_send_message_calls)
    assert mock_server.send_message.call_count == len(mock_destination_email_addresses)


def test_send_email_called_correctly_different_from_and_destination_address(setup_send_email, mocker,
                                                            setup_send_email_correctly_created):
    mock_server, mock_smtp, mock_destination_email_addresses, mock_host, mock_port, mock_username, mock_password, \
        mock_from_address = setup_send_email

    emailer, mock_body, mock_subject = setup_send_email_correctly_created

    new_mock_from_address = "new_mock_from_address"
    new_mock_destination_addresses = ["new_mock_destination_address_1", "new_mock_destination_address_2"]

    emailer.send_email(
        mock_body,
        mock_subject,
        from_email_address=new_mock_from_address,
        destination_email_addresses=new_mock_destination_addresses
    )

    mock_smtp.assert_called_once_with(mock_host, port=mock_port)
    mock_server.login.assert_called_once_with(user=mock_username, password=mock_password)

    expected_send_message_calls = []

    for this_email_address in new_mock_destination_addresses:
        this_message = {
            "Body": mock_body,
            "Subject": mock_subject,
            "From": new_mock_from_address,
            "To": this_email_address
        }
        expected_send_message_calls.append(mocker.call(this_message))

    mock_server.send_message.assert_has_calls(expected_send_message_calls)
    assert mock_server.send_message.call_count == len(mock_destination_email_addresses)
