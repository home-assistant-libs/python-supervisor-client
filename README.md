# Home Assistant Supervisor Client

## Client Library for Home Assistant Supervisor

Python client for interfacing with the [Home Assistant Supervisor](https://github.com/home-assistant/supervisor)
via its [REST API](https://developers.home-assistant.io/docs/api/supervisor/endpoints).
Currently used in the [Home Assistant Supervisor integration](https://www.home-assistant.io/integrations/hassio/)
in Home Assistant.

Add-ons which interface with Supervisor can also leverage it. The library expects
to find the access token in the `SUPERVISOR_TOKEN` env which is set automatically
by Supervisor for add-ons. Currently there is no way to get a long-lived access
token for Supervisor outside these use cases so the library's usage is limited
to these.

## Installation

The library is published on `pip` and can be installed that way:

```sh
pip install aiohasupervisor
```

And then used via import

```py
import asyncio
import supervisor_client

asyncio.run(supervisor_client.info())
```

Output would look like the example response in `/info` from [here](https://developers.home-assistant.io/docs/api/supervisor/endpoints#root)

## Developing & contributing

### Prerequisites

The client can interact remotely with the Home Assistant Supervisor using the
`remote_api` add-on from the [developer add-ons repository](https://github.com/home-assistant/addons-development).

After installing and starting the add-on, a token is shown in the `remote_api`
add-on log, which is needed for further development.

It is also recommended you use Visual Studio Code for development with the devcontainer
extension. This will read the published devcontainer configuration and setup the
development environment for you.

### Get the source code

Fork ([https://github.com/home-assistant-libs/python-supervisor-client/fork](https://github.com/home-assistant/python-supervisor-client/fork)) or clone this repository.

### Using it in development

From within the devcontainer, open terminal and do the following:

```shell
uv pip install -e .
export SUPERVISOR_API_URL=http://192.168.1.2
export SUPERVISOR_TOKEN=replace_this_with_remote_api_token
python examples/connectivity_test.py
```

Output should match the example response in `/info` as shown/linked above in [Installation](#installation).

**Note**: Replace the `192.168.1.2` with the IP address of your Home Assistant
instance running the `remote_api` add-on and use the token provided.

### Contributing a change

1. Create a feature branch on your fork/clone of the git repository.
2. Commit your changes.
3. Rebase your local changes against the `main` branch.
4. Run test suite with the `pytest tests` command or use Test Explorer and confirm that it passes.
5. Use `ruff` to format your code with the rules configured in this project
6. Create a new Pull Request

## Release

Any time the API changes for Home Assistant Supervisor a corresponding release
should be published here. Once that release is available on pip a PR should be
created to [Home Assistant Core](https://github.com/home-assistant/core) updating
its [Home Assistant Supervisor integration](https://github.com/home-assistant/core/blob/dev/homeassistant/components/hassio).
Follow the directions for updating [Requirements](https://developers.home-assistant.io/docs/creating_integration_manifest#requirements)
in the Integration manifest.
