#!/usr/bin/python

WEIGHT_WO_START=10
WEIGHT_2SYLL_ENDING=5
WEIGHT_FIXED_WITH_PREFIX=10
WEIGHT_FIXED_WITH_SUFFIX=5
WEIGHT_FIXED_COMPLETE=20

# I tried creating multiple sets with different maximum lengths,
# but it did not work sufficiently. There were way too many similar names,
# missing out on the wide range of parts being provided from the inputs.
# Probably because pf the way how ottd applies randomness when choosing town names,
# is not adequate for this number of combinations.
# so currently, only one length group is used, including all names.

# tuples: (name list, minimum name length for the *next* group, group name in nml file, weight in nml file, style string ID in language file)
#LENGTH_GROUPS=[ ([], 10, "short_names", 1, "STR_STYLE_NAME_SHORT"), ([], 18, "medium_names",14, "STR_STYLE_NAME_MEDIUM"), ([], 50, "long_names",1, "STR_STYLE_NAME_LONG") ]
#LENGTH_GROUPS=[ ([], 10, "short_names", 1, "STR_STYLE_NAME_SHORT"), ([], 50, "long_names",1, "STR_STYLE_NAME_LONG") ]
LENGTH_GROUPS=[ ([], 50, "long_names",1, "STR_STYLE_NAME_LONG") ]

INPUT_NAMES=["name_prefixes","name_suffixes","name_starts","name_endings_frequent","name_endings_rare","name_endings_two_syllables","name_cores","names_fixed_main","names_fixed_complete" ]
OUTPUT="German-ish_Town_Names"


INPUTS={}
CUSTOM_TAGS={}
DISPVERSION=""
INTVERSION=""
MIN_COMPAT_VERSION=""

LENGTHCOUNTS=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
MAXNAMELENGTH=0
CUMCOUNT=0
TOTALCOUNT=0

with open("custom_tags.txt") as input_file:
	CUSTOM_TAGS=dict([line.split() for line in input_file])
	DISPVERSION=CUSTOM_TAGS["DISPVERSION"][1:]
	#print(DISPVERSION)
	INTVERSION=CUSTOM_TAGS["INTVERSION"][1:]
	#print(INTVERSION)
	MIN_COMPAT_INTVERSION=CUSTOM_TAGS["MIN_COMPAT_INTVERSION"][1:]
	#print(MIN_COMPAT_INTVERSION)
	exit


def DoLetterDupCheck(First,Second):
	f=First[len(First)-2:].lower()
	s=Second[0:2].lower()
	#print("DoLetterDupCheck: First=",First,"f=",f,"Second=",Second,"s=",s)
	if len(f)<2:
		return True
	return not (f[0] in s or f[1] in s or s[0] in f or s[1] in f)

def DoPartDupCheck(First,Second):
	f=First.lower().strip()
	s=Second.lower().strip()
	if len(f)<2:
		return True
	return not (f in s or s in f)
	

def AddOutput(Weight, LetterDupCheck, *Parts):
	global TOTALCOUNT
	global MAXNAMELENGTH
	Result=""
	#print("Weight=",Weight,"LetterDupCheck=",LetterDupCheck, "Parts=",Parts)
	for Part in Parts:
		if Part=="":
			#print("... failed due to empty part")
			return
		if not DoPartDupCheck(Result,Part):
			#print("... failed due to part dupcheck")
			return
		if LetterDupCheck and not DoLetterDupCheck(Result,Part):
			#print("... failed due to letter dupcheck")
			return
		Result+=Part

	if len(Result)>0:
		#print(Result, Weight)
		NameLength=len(Result)
		for g in LENGTH_GROUPS:
			#print(g, g[1])
			if NameLength < g[1]:
				g[0].append((Result,Weight))
				break
		if NameLength>MAXNAMELENGTH:
			MAXNAMELENGTH=NameLength
		LENGTHCOUNTS[NameLength]+=1
		TOTALCOUNT+=1
		#print(LENGTHCOUNTS)


for i in INPUT_NAMES:
	with open("input_"+i+".txt") as input_file:
		INPUTS[i]=input_file.read().splitlines()
	#print(f"INPUTS[{i}]=", INPUTS[i])

if not "" in INPUTS["name_starts"]: INPUTS["name_starts"].append("")

for i in INPUTS["name_prefixes"]:
	for j in INPUTS["names_fixed_main"]:
		AddOutput(WEIGHT_FIXED_WITH_PREFIX,False,i,j)

for i in INPUTS["name_suffixes"]:
	for j in INPUTS["names_fixed_main"]:
		AddOutput(WEIGHT_FIXED_WITH_SUFFIX,False,j,i)

for s in INPUTS["name_starts"]:
	if not s.startswith("//"):
		for i in INPUTS["name_endings_frequent"]:
			for j in INPUTS["name_cores"]:
				#print ("Start=",s,"core=",j,"endings-freq",i)
				if s=="":
					if len(i+j)%2==0:
						AddOutput(WEIGHT_WO_START,True,j,i.lower())
				elif len(i+j)%2==1:
					AddOutput(1,True,s,j.lower(),i)

		for i in INPUTS["name_endings_rare"]:
			for j in INPUTS["name_cores"]:
				if (s==""):
					if (len(i+j)%2==0):
						AddOutput(WEIGHT_WO_START,True,j,i.lower())
				elif (not s.lower() in (i+j).lower()) and len(i+j)%2==1:
					AddOutput(1,True,s,j.lower(),i)

for i in INPUTS["name_endings_two_syllables"]:
	for j in INPUTS["name_cores"]:
		AddOutput(WEIGHT_2SYLL_ENDING,True,j,i.lower())

for i in INPUTS["names_fixed_complete"]:
		AddOutput(WEIGHT_FIXED_COMPLETE,False,i)


with open(OUTPUT+"-"+DISPVERSION+".nml","w") as output_file:
	output_file.write('''grf {
	grfid: "\\8e\\14\\d3\\00";
	name: string(STR_GRF_NAME);
	desc: string(STR_GRF_DESC);
    ''')
	output_file.write(f"\tversion: {INTVERSION};\n\tmin_compatible_version: {MIN_COMPAT_INTVERSION};"+"\n}\n\n")

	for i in LENGTH_GROUPS:
		output_file.write('town_names('+i[2]+')\t{\n\t{\n')
		for j in i[0]:
			output_file.write('\t\ttext(\"'+j[0]+'\",'+f"{j[1]}"+'),\n')
		output_file.write('\t}\n}\n')
	gc=1
	for i in LENGTH_GROUPS:
		output_file.write('town_names\t{\n\tstyles : string('+i[4]+');\n\t{\n')
		for j in LENGTH_GROUPS[0:gc]:
			output_file.write('\ttown_names('+j[2]+','+f'{j[3]}'+'),\n')
			gc+=1
		output_file.write('\t}\n}\n')

print("Len Count             Cumulative")
for i in range(1,MAXNAMELENGTH-1):
	CUMCOUNT+=LENGTHCOUNTS[i]
	print(f"{i:2d}: {LENGTHCOUNTS[i]:5d} => cum. {CUMCOUNT:5d} = {100*CUMCOUNT/TOTALCOUNT:5.1f}%")
