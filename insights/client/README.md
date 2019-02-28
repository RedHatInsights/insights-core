## Developer Setup
Instructions are for RHSM-subscribed machines only.
1. Clone this repo and https://github.com/RedHatInsights/insights-client to the same directory.

```
$ git clone git@github.com:RedHatInsights/insights-client.git
$ git clone git@github.com:RedHatInsights/insights-core.git
```
2. Build the egg and install the client.

```
$ cd insights-client
$ sh lay-the-eggs.sh
```

3. Run the client with the following options to disable GPG since this egg is unsigned.

```
$ sudo BYPASS_GPG=True EGG=/etc/insights-client/rpm.egg insights-client --no-gpg
```

4. Repeat steps 2 & 3 upon making code changes. The majority of the client code lives in this directory, `insights-core/insights/client`.
