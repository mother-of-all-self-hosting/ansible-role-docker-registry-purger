<!--
SPDX-FileCopyrightText: 2020 Aaron Raimist
SPDX-FileCopyrightText: 2020 Chris van Dijk
SPDX-FileCopyrightText: 2020 Dominik Zajac
SPDX-FileCopyrightText: 2020 Mickaël Cornière
SPDX-FileCopyrightText: 2020-2024 MDAD project contributors
SPDX-FileCopyrightText: 2020-2024 Slavi Pantaleev
SPDX-FileCopyrightText: 2022 François Darveau
SPDX-FileCopyrightText: 2022 Julian Foad
SPDX-FileCopyrightText: 2022 Warren Bailey
SPDX-FileCopyrightText: 2023 Antonis Christofides
SPDX-FileCopyrightText: 2023 Felix Stupp
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024-2026 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up Docker Registry Purger

This is an [Ansible](https://www.ansible.com/) role which installs [Docker Registry Purger](https://github.com/klausmeyer/docker-registry-purger) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

Docker Registry Purger is a web interface for the Docker Registry HTTP API V2, written in Ruby on Rails.

See the project's [documentation](https://github.com/klausmeyer/docker-registry-purger/blob/master/README.md) to learn what Docker Registry Purger does and why it might be useful to you.

## Adjusting the playbook configuration

To enable Docker Registry Purger with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

```yaml
########################################################################
#                                                                      #
# docker_registry_purger                                               #
#                                                                      #
########################################################################

docker_registry_purger_enabled: true

########################################################################
#                                                                      #
# /docker_registry_purger                                              #
#                                                                      #
########################################################################
```

### Set the hostname

To enable Docker Registry Purger you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
docker_registry_purger_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the domain to your server.

### Specify a full URL to the container registry

It is also necessary to set a URL to a Distribution Registry instance by adding the following configuration to your `vars.yml` file. Make sure to replace `registry.example.com` with your own value.

```yaml
docker_registry_purger_docker_registry_url: https://registry.example.com
```

### Enabling image deletion (optional)

Image deletion is disabled by default. If you need it, you have to explicitly enable it as below:

```yaml
docker_registry_purger_enabled_delete_images: true
```

### Configuring HTTP Basic authentication (optional)

If Docker Registry Purger will be able to delete images and live on the same private container network as the registry itself, it is recommended to protect it with HTTP Basic authentication by adding the following configuration to your `vars.yml` file:

```yaml
docker_registry_purger_basic_auth_enabled: true

docker_registry_purger_basic_auth_username: admin

# You can put any string here, but generating a strong one is preferred (e.g. `pwgen -s 64 1`).
docker_registry_purger_basic_auth_password: ""
```

### Extending the configuration

There are some additional things you may wish to configure about the service.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file. You can override settings (even those that don't have dedicated playbook variables) using the `docker_registry_purger_environment_variables_additional_variables` variable

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, Docker Registry Purger becomes available at the specified hostname like `https://example.com`.

You should be able to browse the images and possibly delete them (if enabled via `docker_registry_purger_enabled_delete_images`).

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu docker-registry-purger` (or how you/your playbook named the service, e.g. `mash-docker-registry-purger`).
