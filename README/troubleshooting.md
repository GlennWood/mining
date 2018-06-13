TroubleShooting
===============

1. `Version mismatch: this is the 'cffi' package version 1.11.5`

* Detail

        Exception: Version mismatch: this is the 'cffi' package version 1.11.5, located in '/usr/local/lib/python3.5/dist-packages/cffi/api.py'.  When we import the top-level '_cffi_backend' extension module, we get version 1.5.2, located in '/usr/lib/python3/dist-packages/_cffi_backend.cpython-35m-x86_64-linux-gnu.so'.  The two versions should be equal; check your installation.

* Solution

        root:~# mv /usr/lib/python3/dist-packages/_cffi_backend.cpython-35m-x86_64-linux-gnu.so /usr/lib/python3/dist-packages/_cffi_backend.cpython-35m-x86_64-linux-gnu.so-1.5.2
        root:~# ln /usr/local/lib/python3.5/dist-packages/_cffi_backend.cpython-35m-x86_64-linux-gnu.so /usr/lib/python3/dist-packages/_cffi_backend.cpython-35m-x86_64-linux-gnu.so

Your version numbers (python3.5? crypto-1.5.2?) may differ.

