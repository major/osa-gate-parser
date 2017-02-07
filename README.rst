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

Pull requests are welcome!

*-- Major*
