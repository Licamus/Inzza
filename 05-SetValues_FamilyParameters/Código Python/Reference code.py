# Made by Gavin Crump
# Free for use
# BIM Guru, www.bimguru.com.au

# Boilerplate text
import clr

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager 

clr.AddReference("RevitAPI")
import Autodesk 
from Autodesk.Revit.DB import *

# Preparing input from dynamo to revit
famDocs  = IN[0]
famNames = [f.Title for f in famDocs]

# Get all the data we need to check vs excel
famTypesList, famTypeNamesList, famNames, famParamsList, famParamNamesList, = [],[],[],[],[]

for f in famDocs:
	# Get family name and manager
	famMan = f.FamilyManager
	famNames.append(f.Title)
	# Get type data
	famTypes  = list(famMan.Types)
	typeNames = [f.Name for f in famTypes]
	famTypesList.append(famTypes)
	famTypeNamesList.append(typeNames)
	# Get paramaters
	params = famMan.GetParameters()
	paramNames = [p.Definition.Name for p in params]
	famParamsList.append(params)
	famParamNamesList.append(paramNames)

# Function to set family parameter value for a type
def setFamilyParam(famDoc,p,t,v):
	try:
		famMan = famDoc.FamilyManager
		famMan.CurrentType = t
		famMan.Set(p,v)
		return True
	except:
		return False

# Work through excel data
paramNames = IN[1]
excelData  = IN[2]

outcomesList = []

for row in excelData:
	# Results for this row
	outcomes = []
	# Get the family
	famInd = famNames.index(row[0])
	famDoc = famDocs[famInd]
	# Get the type
	typeInd = famTypeNamesList[famInd].index(row[1])
	famType = famTypesList[famInd][typeInd]
	# Limit to the parameter columns
	values = row[2:]
	# Start a transaction in the family document
	t = Transaction(famDoc, row[0]+" - "+row[1])
	t.Start()
	# For each param/value pair for this type...
	for p,v in zip(paramNames,values):
		# Get the parameter
		parInd = famParamNamesList[famInd].index(p)
		famPar = famParamsList[famInd][parInd]
		# Set the parameter
		setParam = setFamilyParam(famDoc,famPar,famType,v)
		outcomes.append(setParam)
	# Commit the transaction
	t.Commit()
	# Append outcomes to list
	outcomesList.append(outcomes)

# Preparing output to Dynamo
OUT = outcomesList