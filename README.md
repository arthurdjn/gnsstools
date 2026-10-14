<p align="center">
  <a href="" rel="noopener">
 <img width=400px src="https://raw.githubusercontent.com/arthurdjn/gnsstools/main/media/logo.png" alt="Project logo"></a>
</p>

<div align="center">

[![Tests](https://github.com/arthurdjn/gnsstools/actions/workflows/tests.yml/badge.svg)](https://github.com/arthurdjn/gnsstools/actions/workflows/tests.yml)
[![Code Quality](https://github.com/arthurdjn/gnsstools/actions/workflows/code-quality.yml/badge.svg)](https://github.com/arthurdjn/gnsstools/actions/workflows/code-quality.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://github.com/arthurdjn/gnsstools/blob/main/pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/arthurdjn/gnsstools/blob/main/LICENSE)

</div>

---

<p align="center"> Process <code>RINEX</code>, <code>SP3</code> and other GNSS files for orbit computation and geo-localization. Retrieve precise satellites and receptors position in a few lines of code.
    <br> 
</p>

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [GNSS Time](#gnsstime)
- [Rinex](#rinex)
- [Satellites](#satellites)
- [Contributing](#contributing)

## About <a name = "about"></a>

### Overview

This project will help you in your GNSS workflow. It provides tools for manipulating / converting GNSS dates (from datetime to Julian Day), readers for ``RINEX`` and ``SP3`` for version 2 and 3. 
Last but not least, ``gnsstools`` lets you correct GNSS orbits from raw files, and compute receptors' position.

### Status

| Development                  | Status      | Feature                                                                |
| ---------------------------- | ----------- | ---------------------------------------------------------------------- |
| GNSS Time                    | finished    | <ul><li>[x] DateTime</li><li>[x] GPS Time</li><li>[x] Julian Day</li><li>[x] Modified Julian Day</li></ul> |
| Rinex                        | in progress | <ul><li>[x] Rinex Observation</li><li>[x] Rinex Navigation</li><li>[x] SP3</li><li>[ ] Rinex Compact</li></ul> |
| Satellites                   | in progress | <ul><li>[ ] Position</li><li>[ ] Clock Offset</li><li>[ ] Pseudo Distance</li></ul> |

## Getting Started <a name = "getting_started"></a>

These instructions will show you the steps on how to install and use ``gnsstools`` straight from the box.

### Installing

``gnsstools`` requires Python 3.10 or later. It is not published on PyPI yet, so install it from this repository:

```
pip install git+https://github.com/arthurdjn/gnsstools
```

or, in a project managed by [uv](https://docs.astral.sh/uv/):

```
uv add git+https://github.com/arthurdjn/gnsstools
```

``rinex.load`` falls back to [georinex](https://github.com/geospace-code/georinex) for the formats it does not parse itself
(Hatanaka-compressed RINEX, for instance). Install the optional extra to enable it:

```
pip install "gnsstools[georinex] @ git+https://github.com/arthurdjn/gnsstools"
```

### Developing

Clone the repository and let [uv](https://docs.astral.sh/uv/) create the environment in ``.venv``:

```
git clone https://github.com/arthurdjn/gnsstools
cd gnsstools
make install  # or: uv sync --all-extras
```

Run ``make help`` to list the other development commands.

## GNSS Time <a name = "gnsstime"></a>

To handles and convert time in different time system you should use the module ``gnsstime``. It will create a time in the ``datetime.datetime`` format, and also process the provided arguments.

### Usage

The ``gnsstime`` object behave exactly like a ``datetime`` one, as it inherits from it.

```python
from gnsstools import gnsstime

# Create a datetime from GNSS information
# Year, Month, Day, Hour, Minute, Second, MicroSecond
date = gnsstime(18, 1, 1, 0, 0, 0)
date = gnsstime(2018, 1, 1, 0, 0, 0)
```

However, the ``gnsstime`` is not type sensitive: you can provide arguments as a ``string``, ``float`` or ``int``.
If the argument is a string, it will convert it first as a float. Then, depending on the argument, it will extract the decimal and update the other arguments.  
For example, if ``second=5.35``, the number of seconds will be ``5`` and the number of microsecond ``350000``. Same for ``day=2.74`` etc.

```python
# Provide arguments as a string
date = gnsstime("18", "1", "1", "0", "0", "0")
date = gnsstime("2018", "01", "01", "00", "00", "00.000000")

# Provide argument as a float
date = gnsstime(2018, 1, 1, 5.933, 4.36, 33.231)
```

You can also retrieve the number of days of the year, seconds of the day / weeks etc:

```python
date = gnsstime(2018, 1, 1, 0, 0, 0)

doy = date.doy # Day of the year
woy = date.woy # Week of the year
sod = date.sod # Second of the day
sow = date.sow # Second of the week
```

### GPS Time

You can retrieve the number of seconds, days and weeks from a the GPS origin (*GPS0*) with:

```python
date = gnsstime(2018, 1, 1, 0, 0, 0)

# From GPS0 defined at 1980-01-06T00:00:00 (UTC)
seconds0 = date.seconds0
days0 = date.days0
weeks0 = date.weeks0
```

### Julian Day

You can also retrieved the Julian Day:

```python
date = gnsstime(2000, 1, 1, 0, 0, 0)

# Julian Day for year 2000
jd = date.jd
# Julian Day for year 1950
jd50 = date.jd50
```

You can also create a ``gnsstime`` object from a Julian Day:

```python
jd = 2451545.0
date = gnsstime.fromjd(jd)

jd50 = 2433282.5
date = gnsstime.fromjd50(jd50)
```

### Modified Julian Day

Finally, you can extract modified Julian Day:

```python
date = gnsstime(2000, 1, 1, 0, 0, 0)

# Modified Julian Day
mjd = date.mjd
```

Again, you can create a ``gnsstime`` object from a modified Julian Day:

```python
mjd = 51544.5
date = gnsstime.frommjd(mjd)
```

## Rinex <a name="rinex"></a>

Load GNSS navigation and observation data as a ``pandas.DataFrame``.

The supported format are:
- ``.**o`` : Rinex 2 Observation,
- ``*O.rnx`` : Rinex 3 Observation,
- ``.**n``, ``.**g`` : Rinex 2 Navigation,
- ``*N.rnx`` : Rinex 3 Navigation,
- ``.SP3`` : SP3

### Observation

```python
from gnsstools import rinex

filename = "data/edf1285b.18o"
df = rinex.load(filename)
```

![Rinex2 Obs](https://raw.githubusercontent.com/arthurdjn/gnsstools/main/media/rinex2_obs.png)

### Navigation

```python
from gnsstools import rinex

filename = "data/BRDC00IGS_R_20182850000_01D_MN.rnx"
df = rinex.load(filename)
```

![Rinex3 Nav](https://raw.githubusercontent.com/arthurdjn/gnsstools/main/media/rinex3_nav.png)

Once loaded, you select an ephemeris / satellite for a specific date with:

```python
from gnsstools import gnsstime

date = gnsstime(2018, 10, 12, 0, 40, 15)
satellite = df.select("G", 2, date)
```

If ``date`` is not part of the dataset ``df``, it will return the closest satellite.

### SP3

```python
from gnsstools import rinex

filename = "data/COM20225_15M.SP3"
df = rinex.load(filename)
```

Positions are in meters and clocks in seconds, and the header of the file is in ``df.attrs``:

```
                                           X            Y            Z         Clock  Session
System PRN Date
G      1   2018-10-12 00:00:00 -17852839.089 -6014552.104 18675309.680 -9.926476e-05        1
           2018-10-12 00:15:00 -18806352.607 -7844840.304 17027746.191 -9.926918e-05        2
           2018-10-12 00:30:00 -19742315.869 -9449478.234 15086967.467 -9.927360e-05        3
```

### Compact

*Work in Progress*

## Satellites <a name = "satellites"></a>

*Work in Progress*

## Contributing <a name = "contributing"></a>

Contributions are welcome! [CONTRIBUTING.md](https://github.com/arthurdjn/gnsstools/blob/main/CONTRIBUTING.md) explains
how to set up the development environment, run the tests and the checks, and open a pull request. Notable changes are
listed in the [changelog](https://github.com/arthurdjn/gnsstools/blob/main/CHANGELOG.md).
