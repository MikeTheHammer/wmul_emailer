"""
@Author = 'Mike Stanley'

============ Change Log ============
2023-Jan-13 = Added tests for when the e-mail addresses are missing from both 
              the constructor and the function. Added/Modified tests for when 
              a single destination e-mail address is passed in. Re-wrote tests 
              to make use of wmul_test_utils.make_namedtuple. 

2022-May-06 = Changed License from MIT to GPLv2.

2018-May-18 = Created.

============ License ============
Copyright (c) 2023 Michael Stanley

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
from wmul_test_utils import make_namedtuple, \
    generate_true_false_matrix_from_list_of_strings


setup_send_email_params, setup_send_email_ids = \
    generate_true_false_matrix_from_list_of_strings(
        "setup_send_email_options", 
        ["use_tuple_of_addresses"]
    )

@pytest.fixture(scope="function", params=setup_send_email_params, 
                ids=setup_send_email_ids)
def setup_send_email(mocker, request):
    use_tuple_of_addresses = request.param.use_tuple_of_addresses
    mock_server = mocker.Mock()

    @contextlib.contextmanager
    def mock_server_function(host, port):
        yield mock_server

    mock_smtp = mocker.patch(
        "wmul_emailer.SMTP",
        mocker.Mock(side_effect=mock_server_function)
    )

    mock_destination_email_addresses = ["foo@example.com", "bar@example.com"]
    if use_tuple_of_addresses:
        mock_destination_email_addresses = \
            tuple(mock_destination_email_addresses)
    mock_host = "mock_host"
    mock_port = "mock_port"
    mock_username = "mock_username"
    mock_password = "mock_password"
    mock_from_address = "mock_from_email_address"

    return make_namedtuple(
        "setup_send_email",
        mock_server=mock_server, 
        mock_smtp=mock_smtp, 
        mock_destination_email_addresses=mock_destination_email_addresses, 
        mock_host=mock_host, 
        mock_port=mock_port, 
        mock_username=mock_username,
        mock_password=mock_password, 
        mock_from_address=mock_from_address
    )


def test_send_email_dest_addresses_not_a_list_tuple_or_str(setup_send_email):
    with pytest.raises(TypeError):
        emailer = wmul_emailer.EmailSender(
            destination_email_addresses=object(),
            server_host=setup_send_email.mock_host,
            port=setup_send_email.mock_port,
            user_name=setup_send_email.mock_username,
            password=setup_send_email.mock_password,
            from_email_address=setup_send_email.mock_from_address
        )

    setup_send_email.mock_smtp.assert_not_called()
    setup_send_email.mock_server.assert_not_called()


@pytest.fixture(scope="function")
def setup_send_email_correctly_created(setup_send_email, mocker):
    emailer = wmul_emailer.EmailSender(
        destination_email_addresses=setup_send_email.mock_destination_email_addresses,
        server_host=setup_send_email.mock_host,
        port=setup_send_email.mock_port,
        user_name=setup_send_email.mock_username,
        password=setup_send_email.mock_password,
        from_email_address=setup_send_email.mock_from_address
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

    return make_namedtuple(
        "setup_send_email_correctly_created",
        emailer=emailer, 
        mock_body=mock_body, 
        mock_subject=mock_subject,
        setup_send_email=setup_send_email
    )


def test_send_email_called_correctly_normal_path(mocker, setup_send_email_correctly_created):
    setup_send_email = setup_send_email_correctly_created.setup_send_email

    setup_send_email_correctly_created.emailer.send_email(
        setup_send_email_correctly_created.mock_body,
        setup_send_email_correctly_created.mock_subject
    )

    setup_send_email.mock_smtp.assert_called_once_with(setup_send_email.mock_host, port=setup_send_email.mock_port)
    setup_send_email.mock_server.login.assert_called_once_with(user=setup_send_email.mock_username, password=setup_send_email.mock_password)

    expected_send_message_calls = []

    for this_email_address in setup_send_email.mock_destination_email_addresses:
        this_message = {
            "Body": setup_send_email_correctly_created.mock_body,
            "Subject": setup_send_email_correctly_created.mock_subject,
            "From": setup_send_email.mock_from_address,
            "To": this_email_address
        }
        expected_send_message_calls.append(mocker.call(this_message))

    setup_send_email.mock_server.send_message.assert_has_calls(expected_send_message_calls)
    assert setup_send_email.mock_server.send_message.call_count == len(setup_send_email.mock_destination_email_addresses)


def test_send_email_called_correctly_different_from_address(mocker, setup_send_email_correctly_created):
    setup_send_email = setup_send_email_correctly_created.setup_send_email

    new_mock_from_address = "new_mock_from_address"

    setup_send_email_correctly_created.emailer.send_email(
        setup_send_email_correctly_created.mock_body,
        setup_send_email_correctly_created.mock_subject,
        from_email_address=new_mock_from_address
    )

    setup_send_email.mock_smtp.assert_called_once_with(setup_send_email.mock_host, port=setup_send_email.mock_port)
    setup_send_email.mock_server.login.assert_called_once_with(user=setup_send_email.mock_username, password=setup_send_email.mock_password)

    expected_send_message_calls = []

    for this_email_address in setup_send_email.mock_destination_email_addresses:
        this_message = {
            "Body": setup_send_email_correctly_created.mock_body,
            "Subject": setup_send_email_correctly_created.mock_subject,
            "From": new_mock_from_address,
            "To": this_email_address
        }
        expected_send_message_calls.append(mocker.call(this_message))

    setup_send_email.mock_server.send_message.assert_has_calls(expected_send_message_calls)
    assert setup_send_email.mock_server.send_message.call_count == len(setup_send_email.mock_destination_email_addresses)


def test_send_email_called_correctly_different_destination_address(mocker, setup_send_email_correctly_created):
    setup_send_email = setup_send_email_correctly_created.setup_send_email

    new_mock_destination_addresses = ["new_mock_destination_address_1", "new_mock_destination_address_2"]

    setup_send_email_correctly_created.emailer.send_email(
        setup_send_email_correctly_created.mock_body,
        setup_send_email_correctly_created.mock_subject,
        destination_email_addresses=new_mock_destination_addresses
    )

    setup_send_email.mock_smtp.assert_called_once_with(setup_send_email.mock_host, port=setup_send_email.mock_port)
    setup_send_email.mock_server.login.assert_called_once_with(user=setup_send_email.mock_username, password=setup_send_email.mock_password)

    expected_send_message_calls = []

    for this_email_address in new_mock_destination_addresses:
        this_message = {
            "Body": setup_send_email_correctly_created.mock_body,
            "Subject": setup_send_email_correctly_created.mock_subject,
            "From": setup_send_email.mock_from_address,
            "To": this_email_address
        }
        expected_send_message_calls.append(mocker.call(this_message))

    setup_send_email.mock_server.send_message.assert_has_calls(expected_send_message_calls)
    assert setup_send_email.mock_server.send_message.call_count == len(setup_send_email.mock_destination_email_addresses)


def test_send_email_called_correctly_different_from_and_destination_address(mocker, setup_send_email_correctly_created):
    setup_send_email = setup_send_email_correctly_created.setup_send_email

    new_mock_from_address = "new_mock_from_address"
    new_mock_destination_addresses = ["new_mock_destination_address_1", "new_mock_destination_address_2"]

    setup_send_email_correctly_created.emailer.send_email(
        setup_send_email_correctly_created.mock_body,
        setup_send_email_correctly_created.mock_subject,
        from_email_address=new_mock_from_address,
        destination_email_addresses=new_mock_destination_addresses
    )

    setup_send_email.mock_smtp.assert_called_once_with(setup_send_email.mock_host, port=setup_send_email.mock_port)
    setup_send_email.mock_server.login.assert_called_once_with(user=setup_send_email.mock_username, password=setup_send_email.mock_password)

    expected_send_message_calls = []

    for this_email_address in new_mock_destination_addresses:
        this_message = {
            "Body": setup_send_email_correctly_created.mock_body,
            "Subject": setup_send_email_correctly_created.mock_subject,
            "From": new_mock_from_address,
            "To": this_email_address
        }
        expected_send_message_calls.append(mocker.call(this_message))

    setup_send_email.mock_server.send_message.assert_has_calls(expected_send_message_calls)
    assert setup_send_email.mock_server.send_message.call_count == len(setup_send_email.mock_destination_email_addresses)


def test_send_email_called_correctly_str_destination_address(setup_send_email_correctly_created):
    setup_send_email = setup_send_email_correctly_created.setup_send_email

    new_mock_from_address = "new_mock_from_address"
    new_mock_destination_address = "new_mock_destination_address_1"

    setup_send_email_correctly_created.emailer.send_email(
        setup_send_email_correctly_created.mock_body,
        setup_send_email_correctly_created.mock_subject,
        from_email_address=new_mock_from_address,
        destination_email_addresses=new_mock_destination_address
    )

    setup_send_email.mock_smtp.assert_called_once_with(setup_send_email.mock_host, port=setup_send_email.mock_port)
    setup_send_email.mock_server.login.assert_called_once_with(user=setup_send_email.mock_username, password=setup_send_email.mock_password)

    setup_send_email.mock_server.send_message.assert_called_once_with({
            "Body": setup_send_email_correctly_created.mock_body,
            "Subject": setup_send_email_correctly_created.mock_subject,
            "From": new_mock_from_address,
            "To": new_mock_destination_address
        })


def test_send_email_no_destination_email_addresses(setup_send_email, mocker):
    emailer = wmul_emailer.EmailSender(
        server_host=setup_send_email.mock_host,
        port=setup_send_email.mock_port,
        user_name=setup_send_email.mock_username,
        password=setup_send_email.mock_password,
        from_email_address=setup_send_email.mock_from_address
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

    with pytest.raises(ValueError) as ve:
        emailer.send_email(
            email_body=mock_body,
            email_subject=mock_subject
        )
        assert "destination_email_addresses must be provided to either the constructor or to the send_email function" in str(ve)

    setup_send_email.mock_smtp.assert_not_called()
    mock_mimetext.assert_not_called()
    setup_send_email.mock_server.login.assert_not_called()
    setup_send_email.mock_server.send_message.assert_not_called()


def test_send_email_no_from_email_address(setup_send_email, mocker):
    emailer = wmul_emailer.EmailSender(
        destination_email_addresses=setup_send_email.mock_destination_email_addresses,
        server_host=setup_send_email.mock_host,
        port=setup_send_email.mock_port,
        user_name=setup_send_email.mock_username,
        password=setup_send_email.mock_password
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

    with pytest.raises(ValueError) as ve:
        emailer.send_email(
            email_body=mock_body,
            email_subject=mock_subject
        )
        assert "from_email_address must be provided to either the constructor or to the send_email function." in str(ve)

    setup_send_email.mock_smtp.assert_not_called()
    mock_mimetext.assert_not_called()
    setup_send_email.mock_server.login.assert_not_called()
    setup_send_email.mock_server.send_message.assert_not_called()


def test_send_email_no_from_and_no_destination_email_address(setup_send_email, mocker):
    emailer = wmul_emailer.EmailSender(
        server_host=setup_send_email.mock_host,
        port=setup_send_email.mock_port,
        user_name=setup_send_email.mock_username,
        password=setup_send_email.mock_password
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

    with pytest.raises(ValueError) as ve:
        emailer.send_email(
            email_body=mock_body,
            email_subject=mock_subject
        )
        assert "must be provided to either the constructor or to the send_email function." in str(ve)

    setup_send_email.mock_smtp.assert_not_called()
    mock_mimetext.assert_not_called()
    setup_send_email.mock_server.login.assert_not_called()
    setup_send_email.mock_server.send_message.assert_not_called()
