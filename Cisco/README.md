# Cisco AnyConnect

The AnyConnect munki recipe requires you to download the `webdeploy` package from the Cisco Software Download portal. AnyConnect Secure Mobility Client v4.x should be available at https://software.cisco.com/download/home/286281283/type/282364313. Note that AnyConnect 4.x is available to customers with active AnyConnect Apex, Plus or VPN Only term/contracts.

After you download the package, you point the recipe to it using the `-p` command line argument.

##### Example

```bash
autopkg run AnyConnect.munki -p ~/Downloads/anyconnect-macos-<version>-webdeploy-k9.pkg
```
