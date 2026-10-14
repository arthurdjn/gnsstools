import math
from collections import defaultdict

from gnsstools import gnsstime

from .datasets import PositionDataFrame
from .reader import ABCReader, Record

# Clocks and clock rates of the SP3 records that are bad or absent. Absent positions are 0.000000.
ABSENT_CLOCK = 999999.999999

# Factors from the units of SP3 files to SI units.
KILOMETER = 1e3  # Positions (km)
DECIMETER = 0.1  # Velocities (dm/s)
MICROSECOND = 1e-6  # Clocks (microseconds)
CLOCK_RATE = 1e-10  # Clock rates (10^-4 microseconds/s)

COLUMNS = ["X", "Y", "Z", "Clock", "VX", "VY", "VZ", "ClockRate", "Session"]


class SP3Reader(ABCReader):
    """
    Reads `SP3` files (versions a to d) of precise orbits.

    Each row is a satellite at an epoch, with its position ``X``, ``Y``, ``Z`` (m) and its ``Clock`` (s) and, when the
    file has velocities, its velocity ``VX``, ``VY``, ``VZ`` (m/s) and its ``ClockRate`` (s/s). Absent values are NaN.
    The header is stored in the ``attrs`` of the DataFrame.

    * :attr:`lines` (list): List of lines to process.

    """

    def __init__(self, lines: list[str]) -> None:
        super().__init__(lines)

    @staticmethod
    def is_sp3(lines: list[str]) -> bool:
        """Whether the lines are those of an SP3 file."""
        return len(lines) > 0 and len(lines[0]) > 2 and lines[0][0] == "#" and lines[0][1] in "abcd"

    def _read_header(self) -> Record:
        line = self.lines[0]
        header: Record = {
            "Version": line[1],
            # "P" for positions only, "V" for positions and velocities.
            "PosVelFlag": line[2],
            "StartDate": gnsstime(line[3:7], line[8:10], line[11:13], line[14:16], line[17:19], line[20:31]),
            "NumEpoch": self._eval(line[32:39]),
            "DataUsed": self._eval(line[40:45]),
            "CoordSystem": self._eval(line[46:51]),
            "OrbitType": self._eval(line[52:55]),
            "Agency": self._eval(line[56:60]),
        }
        line = self.lines[1]
        header.update(
            {
                "GPSWeek": self._eval(line[3:7]),
                "SecondsOfWeek": self._eval(line[8:23]),
                "Interval": self._eval(line[24:38]),
                "MJD": self._eval(line[39:44]),
                "FractionalDay": self._eval(line[45:60]),
            }
        )
        for line in self.lines[2:]:
            if line.startswith("*"):
                break
            if line.startswith("%c"):
                header.setdefault("FileType", self._eval(line[3:5]))
                header.setdefault("TimeSystem", self._eval(line[9:12]))
        header["Satellites"] = self._read_sat()
        return header

    def _read_sat(self) -> list[str]:
        """The satellites of the "+" header records."""
        satellites: list[str] = []
        lines = [line for line in self.lines if line.startswith("+ ")]
        sat_num = int(lines[0][3:6])
        for line in lines:
            # There are maximum 17 satellites per row
            # e.g. satellites_sequence = "G01G02G03G04G05G06G07G08G09G10G11G12G13G14G15G16G17"
            satellites_sequence = line[9:60]
            for isat in range(17):
                # Extract and save the id of the satellite
                satellite = satellites_sequence[isat * 3 : (isat + 1) * 3].strip()
                if satellite not in ("", "0", "00"):
                    # Replace blank space by 0 (e.g. "G 2" -> "G02")
                    satellites.append(satellite.replace(" ", "0"))
        return satellites[:sat_num]

    def _read_values(self, line: str, unit: float, clock_unit: float) -> tuple[float, float, float, float]:
        """The 3 coordinates of a position or velocity record, and its clock or clock rate, in SI units."""
        x, y, z = (self._eval_float(line[4 + 14 * k : 18 + 14 * k]) for k in range(3))
        if x == y == z == 0:
            x, y, z = math.nan, math.nan, math.nan
        clock = self._eval(line[46:60])
        if not isinstance(clock, (int, float)) or clock >= ABSENT_CLOCK:
            clock = math.nan
        return x * unit, y * unit, z * unit, clock * clock_unit

    def read(self) -> PositionDataFrame:
        self._cursor = 0
        header = self._read_header()

        # One record per satellite and epoch, holding its position and velocity.
        records: dict[tuple[str, gnsstime], Record] = {}
        epochs: defaultdict[str, int] = defaultdict(int)
        date: gnsstime | None = None
        for line in self.lines:
            # If the end is reached, break.
            if line.startswith("EOF"):
                break
            # Read the date for a set of observations.
            elif line.startswith("*"):
                year, month, day, hour, minute, second = (
                    line[3:7],
                    line[8:10],
                    line[11:13],
                    line[14:16],
                    line[17:19],
                    line[20:31],
                )
                date = gnsstime(year, month, day, hour, minute, second)
            # Position and velocity records. The correlation records ("EP", "EV") are not read.
            elif line[:1] in ("P", "V") and date is not None:
                system, prn = self._eval(line[1]), self._eval(line[2:4])
                satellite = f"{system}{prn}"
                if (satellite, date) not in records:
                    epochs[satellite] += 1
                    records[satellite, date] = {
                        "Date": date,
                        "System": system,
                        "PRN": prn,
                        "Session": epochs[satellite],
                    }
                record = records[satellite, date]
                if line.startswith("P"):
                    record["X"], record["Y"], record["Z"], record["Clock"] = self._read_values(
                        line, KILOMETER, MICROSECOND
                    )
                else:
                    record["VX"], record["VY"], record["VZ"], record["ClockRate"] = self._read_values(
                        line, DECIMETER, CLOCK_RATE
                    )

        # Create the DataFrame
        df = PositionDataFrame(list(records.values()))
        # Make it pretty
        df = df.set_index(["System", "PRN", "Date"])
        columns = [col for col in COLUMNS if col in df.columns]
        df = df.reindex(columns, axis=1)
        df = df.sort_index()
        df.attrs = dict(header.items())
        return df
