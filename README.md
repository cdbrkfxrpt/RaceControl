About
==
Controller Are Network (CAN) bus is a data transportation system widely used in
the automotive and aerospace industry because it is robust and simple. It
features
+ data transmission over twisted pair cable which gives it very good
electromagnetic immunity without additional shielding
+ daisy chaining is possible if done correctly
+ an exceedingly low residual failure probability of
_message_error_rate * 4.7 * 10^-11_
and it implements the physical and the data link layer in the OSI model. For
more information, the
[official Bosch document](http://www.bosch-semiconductors.de/media/ubk_semiconductors/pdf_1/canliteratur/can2spec.pdf)
has it. Another good source is the
[CAN bus Wikipedia page](https://en.wikipedia.org/wiki/CAN_bus).

If you've ever had to operate any vehicle carrying data on the CAN bus, there's
a fair chance that you have been required to use licensed, closed source,
non adaptable software. There are open source programming libraries available
(`socketcan` and `can4linux` are the best known examples, but there is more),
but starting this deep down may be cumbersome to you or you just want to (or
have to) get something running quickly. In any case, the licensed tools are
still widely used and in fairness well supported, but generally bundled with
hardware and, by trend, rather expensive.

`RaceControl` provides a free and open source alternative that runs on Linux,
thus leaving the choice of hardware to you (it's tested on Raspberry Pi,
Raspberry Pi 2 and several Intel CPU based laptops). It uses `socketcan`, which
means the choice of CAN adapter is also left to you as long as it's supported
by `socketcan`.

What does it do?
--
`RaceControl` logs CAN data to files, the name of which you can specify through
the configuration file, and it provides data as a web service to be consumed by
your browser. That means you can use more or less any device to look at your
data (small screens don't work as well for plots and currently, they don't
resize either, so you may want to use something upward of iPad size). The data
it provides via web service is also configurable via DBC files, uploaded to the
`.config/racecontrol/dbc` directory, which sits in the home directory of the
user you are running `RaceControl` as. Your loggings can be accessed through a
browser as well, given that your `nginx` is also configured correctly. For more
on this see _Install and Setup_.

What doesn't it do?
--
It doesn't guarantee full data integrity. More precisely, it doesn't guarantee
to preserve message order or to even fully cover data. Realistically, you can
expect it to log about 20% of bus load on a 1MBit/s CAN bus. Furthermore, it
specifically doesn't provide a sophisticated data analysis user interface. The
data analysis interface it provides is very basic. You are provided with a CSV
file to read into a data analysis tool of your own choosing.

How is it licensed?
--
It uses the GNU Public License version 3.



Install
==
When in the project directory, execute `sudo pip3 install .` (or alternatively
`python3 setup.py install`) to install it and its dependencies for your local
`python3`.

CAN bus and web server
--
For it to work, you need to fire up your CAN interfaces and configure your
`nginx` web server. The CAN interfaces, aside from the hardware need the Linux
kernel modules called `can` and `can-raw` and if you're using a serial CAN
interface also `slcan`. `vcan` provides a virtual CAN interface to be used on
machines where no CAN hardware is installed and of course for testing. Other
modules for different drivers are also available; please consult the respective
documentation for your system. On a Raspbian, you need the tool
[`rpi-source`](https://github.com/notro/rpi-source/wiki) to download, build and
install the missing modules. Elsewhere, just get the code for your kernel
(`uname -a`) from [kernel.org](https://www.kernel.org) and build and install
using that (the `rpi-source` page has tutorials for this which are helpful even
if you're not using `rpi-source` but are compiling from kernel code downloaded
directly). As soon as you have these modules compiled and installed and loading
on boot (put them in a file called `/etc/modules-load.d/can.conf` for this,
with each module name on a new line), you can use the scripts provided in this
package to start. `vcan_start` starts the virtual CAN interface, `slcan_start`
starts the serial CAN interface. `slcan_start` has to be provided with two
arguments specifying bus speed and and interface name of your choosing (for
more information on the bus speed, execute `slcan_start` without arguments on
the command line).

As for the web server: I recommend you use `nginx`, although any other web
server capable of proxying WSGI applications should work. `nginx`, if you are
using it, must be configured thusly:

    events {
        worker_connections  1024;
    }

    http {
        include       mime.types;
        default_type  application/octet-stream;

        server {
            listen       80;
            server_name  your.racecontrol.server;

            location ^~ /loggings {
              alias /var/www/loggings/;
              autoindex on;
            }

            location / {
                proxy_pass      http://127.0.0.1:5000/;
                proxy_redirect  off;

                proxy_set_header Host           $host;
                proxy_set_header X-Real-IP      $remote_addr;
                proxy_set_header X-Forwared-For $proxy_add_x_forwarded_for;

                proxy_set_header Connection '';
                proxy_http_version 1.1;
                chunked_transfer_encoding off;

                proxy_buffering off;
                proxy_cache off;
            }
        }
    }

This is not a complete `nginx` configuration. Please see the default nginx.conf
for details.

In order to make your system plug and play, it is suggested to have the init
system (`systemd`, `runit`, ...) start `nginx` and also `RaceControl`. Chances
are `nginx` already  exists as a `systemd`-service in your system (if it uses
`systemd`; otherwise, consult the corresponding documentation) and you only
need to enable it (`sudo systemctl enable nginx`) after installing. For
`RaceControl`, you have to create a service. Please consult the documentation
of your init system for details.

Further Information
--
This documentation contains only information concerning the Python backend of
RaceControl. Please refer to [the Twitter Bootstrap
documentation](http://getbootstrap.com/) for information concerning the HTML in
use, and to the code itself located in `racecontrol/static/js/raceflot.js`,
which has been heavily commented, for information concerning the JavaScript.
