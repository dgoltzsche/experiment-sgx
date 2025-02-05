from invoke import task
from requests import get
from subprocess import check_output, run
from tasks.util.env import BIN_DIR, SGX_INSTALL_DIR


def do_configure(repo_url, write_file, key_url):
    # Modify the sources list
    with open("/etc/apt/sources.list.d/{}.list".format(write_file), "w+") as f:
        f.write("deb [arch=amd64] {} bionic main\n".format(repo_url))

    # Add key
    run("apt-key adv --fetch-keys {}".format(key_url), shell=True)


@task
def configure():
    # Configure Intel APT repo
    do_configure(
        "https://download.01.org/intel-sgx/sgx_repo/ubuntu",
        "intel-sgx",
        "https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key",
    )

    # Configure Microsoft APT repo
    do_configure(
        "https://packages.microsoft.com/ubuntu/18.04/prod",
        "msprod",
        "https://packages.microsoft.com/keys/microsoft.asc",
    )


def do_install(url, fname):
    # Download binary
    r = get(url)
    full_path = "{}/{}".format(SGX_INSTALL_DIR, fname)
    with open(full_path, "wb+") as f:
        f.write(r.content)

    # Make executable
    run("chmod a+x {}".format(full_path), shell=True)

    # Run
    run(full_path)


@task
def install_dcap():
    print("Installing Intel SGX DCAP driver...")
    do_install(
        "https://download.01.org/intel-sgx/sgx-dcap/1.9/linux/distro/ubuntu18.04-server/sgx_linux_x64_driver_1.36.2.bin",
        "sgx_linux_x64_driver.bin",
    )


@task
def install_sgxsdk():
    print("Installing Intel SGX SDK...")
    do_install(
        "https://download.01.org/intel-sgx/sgx-dcap/1.9/linux/distro/ubuntu18.04-server/sgx_linux_x64_sdk_2.12.100.3.bin",
        "sgx_linux_x64_sdk.bin",
    )

    # Update .bashrc
    with open("/home/faasm/.bashrc", "a") as f:
        f.write("source {}/sgxddk/environment\n".format(SGX_INSTALL_DIR))


@task
def install():
    install_dcap()
    install_sgxsdk()
