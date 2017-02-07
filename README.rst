==================
osa-gate-parser.py
==================

This script provides an easy method for getting timing data for tasks in
OpenStack-Ansible CI (or "gate") jobs. Simply run the script with a URL as the
argument:

.. code-block:: console

    ./osa-gate-parser.py http://logs.openstack.org/42/429842/2/check/gate-openstack-ansible-openstack-ansible-aio-ubuntu-xenial/7c83603/console.html

The script will read the data as a stream and process it on the fly without
loading the entirety of the URL's content into memory.

Sample output:

.. code-block:: text

    PLAY: Install horizon server ---------------------------------------------------
      0:00:32 | os_horizon : Collect and compress static files
      0:00:08 | os_horizon : Install distro packages
      0:00:06 | os_horizon : Install requires pip packages
      0:00:06 | pip_install : Install apt packages
      0:00:05 | os_horizon : Unarchive pre-built venv
      0:00:05 | Wait for container ssh
      0:00:05 | os_horizon : Compile messages for translation
      0:00:03 | pip_install : Install PIP
      0:00:03 | galera_client : Install galera packages
      0:00:03 | os_horizon : Load service
      0:00:03 | os_horizon : Update virtualenv path
      0:00:02 | os_horizon : Perform a horizon DB sync
      0:00:02 | Update apt when proxy is added
      0:00:01 | galera_client : Find old sources
      0:00:01 | Start Container
      0:00:01 | os_horizon : Enable the trove-dashboard Horizon panel
      0:00:01 | os_horizon : Enable the magnum-ui-dashboard Horizon panel
      0:00:01 | Lxc container restart
      0:00:01 | os_horizon : Attempt venv download
      0:00:01 | os_horizon : Ensure Apache ServerName

Pull requests are welcome!

*-- Major*
