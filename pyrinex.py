
import sys
import datetime

# Set up the dictionary structure for possible measurements.
#   C => C/A code measurement  
#   P => P code measurement
#   L => Carrier phase
#   D => Doppler
#   S => Carrier noise density (dB-Hz)
#
#   Numbers indicate the signal band (1 => L1, 2 => L2, 3 => L5)
#   P2 is the P code measurment on the L2 band in compliance with the RINEX
#   2.11 speccification.

gpsRecord = dict(
  time = '0',
  prn = '0',
  C1 = '0',
  P1 = '0',
  L1 = '0',
  D1 = '0',
  S1 = '0',
  C2 = '0',
  P2 = '0',
  L2 = '0',
  D2 = '0',
  S2 = '0',
  C5 = '0',
  L5 = '0',
  D5 = '0',
  S5 = '0'
)

rinFileName = "cat20010.16n"
csvFileName = "cat20010.csv"
writeMode = "w"

csvFields = ["time", "prn", "C1", "P1", "L1", "D1", "S1", "C2", "P2", "L2", 
  "D2", "S2", "C5", "L5", "D5", "S5"]
rinFields = []

numFields = 0

# Parse the commnad line arguments
argc = len(sys.argv)
if argc < 2:
	print ("No arguments given, using default values")

else:
	if sys.argv[1] == "-h" or sys.argv[1] == "--help": # help
		print("RinexParser.py: Python utility for converting RINEX to CSV")
		print("Usage:")
		print("RinexParser.py [RINEX_File [CSV_File]] [-al] [-f Fields]")
		print("  RINEX_File : Name of Rinex file")
		print("  CSV_File   : Name of csv file, built from RINEX name if absent")
		print("  -a         : Append to csv file")
		print("  -l         : Legacy data only, supercedes -f")
		print("  -f Fields  : List of rinex fields as specified")
		print("    C => C/A code measurement")
		print("    P => P code measurement")
		print("    L => Carrier phase")
		print("    D => Doppler")
		print("    S => Carrier noise density (dB-Hz)")
		print("")
		print("    Numbers indicate the signal band (1 => L1, 2 => L2, 3 => L5)")
		print("    P2 is the P code measurment on the L2 band in compliance with the RINEX")
		print("    2.11 speccification.")
		exit(0) 

	rinFileName = sys.argv[1]
	csvFileName = rinFileName[:-3] + "csv" 
	
	i = 2
	while i < argc: 
		if i == 2 and sys.argv[i][0] != "-":
			csvFileName = sys.argv[2]
			i += 1
			continue
		
		if sys.argv[i] == "-f": # Use the user specified format
			i += 1
			csvFields = []
			while i < argc and sys.argv[i][0] != "-":
				csvFields.append(sys.argv[i])
				i += 1
	
		elif sys.argv[i] == "-l": # ``Legacy'' fields
			csvFields = ["time", "prn", "C1", "P1", "L1", "D1", "S1", "S2", 
			  "C2", "L2", "D2"]

		elif sys.argv[i] == "-a": # append mode
			writeMode = "a"

		else:
			print ("Unknown argument: {}".format(sys.argv[i]))
			exit(0)
		i += 1
	
# Open the rinex file and extract header data
rinFile = open(rinFileName, "r")
csvFile = open(csvFileName, writeMode)

currentLine = rinFile.readline()
while currentLine[60:].rstrip() != "END OF HEADER":
	if currentLine[60:].rstrip() == "# / TYPES OF OBSERV": # Extract header data
		numFields = int(currentLine[1:6])
		for j in range(int(numFields/9)):
			for i in range(9):
				rinFields.append(currentLine[(7+i*6):(12+i*6)].lstrip())
			currentLine = rinFile.readline()
		for i in range(int(numFields%9)):
			rinFields.append(currentLine[(7+i*6):(12+i*6)].lstrip())
	currentLine = rinFile.readline()

# Scroll through looking for valid epochs
currentLine = rinFile.readline()
while currentLine != "":
	if currentLine[27:30] == " 0 ":
		year = int(currentLine[1:3])
		if year < 80: 
			year = 2000 + year
		else: 
			1900 + year
		month = int(currentLine[4:6])
		day = int(currentLine[7:9])
		hour = int(currentLine[10:12])
		mm = int(currentLine[13:15])
		sec = float(currentLine[16:26])

		gpsRecord["time"] = str(datetime.date(year, month, day).isoweekday() \
		  % 7 * 24 * 3600 + hour * 3600 + mm * 60 + sec)
		  
		# Parse the PRN values for this epoch
		numSats = int(currentLine[30:32])
		epochPRN = []
		for j in range(int(numSats / 12)):
			for i in range(12):
				epochPRN.append(currentLine[33+i*3:35+i*3])
		for i in range(numSats % 12):
			epochPRN.append(currentLine[33+i*3:35+i*3])

		for prn in epochPRN:
			gpsRecord["prn"] = prn
			for j in range(int(numFields / 5)):
				currentLine = rinFile.readline()
				for i in range(5):
					record = currentLine[i*16+1:i*16+14].lstrip()
					if record == "":
						gpsRecord[rinFields[j*5+i]] = "0"
					else:
						gpsRecord[rinFields[j*5+i]] = record
			currentLine = rinFile.readline()
			for i in range(int(numFields % 5)):
				record = currentLine[i*16+1:i*16+14].lstrip()
				if record == "":
					gpsRecord[rinFields[int(numFields/5*5+i)]] = "0"
				else:
					gpsRecord[rinFields[int(numFields/5*5+i)]] = record

			csvLine = ""
			for field in csvFields:
				csvLine += gpsRecord[field] + ","
			csvFile.write(csvLine[:-1]+"\r\n")

	currentLine = rinFile.readline()

# Close files and clean up
rinFile.close()
csvFile.close()