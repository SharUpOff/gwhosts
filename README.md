# gwhosts
Route the list of hosts through the specified gateway (e.g. VPN).

Run it manually, using `cron`, or any other way.

## How this script works
1. Resolves IP addresses for hosts specified in a file;
2. Combines similar addresses into subnets;
3. Adds resulting subnets into static routes via specified gateway.

## Installation

### LT-Version (RECOMMENDED)
The lt-version has no external python dependencies and does not use `argparse`.
So it starts up to 10x faster on slow devices like OpenWRT routers.
```bash
curl https://raw.githubusercontent.com/SharUpOff/gwhosts/main/dist/gwhostslt.py -so - | sudo tee /usr/local/bin/gwhostslt > /dev/null
```
```bash
sudo chmod 755 /usr/local/bin/gwhostslt
```

### PR2-Version (SLOW)
The pr2-version uses `pyroute2` (if installed) and `argparse`.
So it starts up to 10x slower on slow devices like OpenWRT routers.
```bash
curl https://raw.githubusercontent.com/SharUpOff/gwhosts/main/dist/gwhosts.py -so - | sudo tee /usr/local/bin/gwhosts > /dev/null
```
```bash
sudo chmod 755 /usr/local/bin/gwhosts
```

## Usage
```bash
gwhostslt 192.168.1.1 /etc/gwhosts
```

`/etc/gwhosts` example:
```hosts
github.com
google.com
```

`crontab` example:
```crontab
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of the month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday;
# │ │ │ │ │                                   7 is also Sunday on some systems)
# │ │ │ │ │
# │ │ │ │ │
# * * * * * <command to execute>
* * * * * /usr/bin/python /usr/local/bin/gwhostslt 192.168.1.1 /etc/gwhosts
```

# Contribution
🛠 You are welcome to add support for other distributions, fix bugs or improve functionality.
