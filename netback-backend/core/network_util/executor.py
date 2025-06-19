from netmiko import ConnectHandler


def executeCommandOnDevice(device, command):
    if not device.customUser and not device.VaultCredential:
        return "No credentials found for this device"

    connection = {
        "device_type": device.manufacturer.netmiko_type or "generic",
        "host": device.ipAddress,
        "username": device.customUser or device.VaultCredential.username,
        "password": device.customPass or device.VaultCredential.get_plain_password(),
    }

    try:
        with ConnectHandler(**connection) as net_connect:
            result = net_connect.send_command(command)
        return result
    except Exception as e:
        return str(e)
