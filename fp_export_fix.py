import os

fp_to_edit = "/Users/willmitchell/Documents/CPSOS_Faceplates/CPSOS_Brain_Guide.wrl"

replacements = {}
replacements["0.07 0.30000001 0.12"] = "0.9 0.9 0.9"
replacements["0.0099999998 0.029999999 0.0099999998"] = "0.03 0.03 0.03"
replacements["0.079999998 0.5 0.1"] = "0.8 0.8 0.8"
replacements["0.0099999998 0.050000001 0.0099999998"] = "0.05 0.05 0.05"

contents = ""

with open(fp_to_edit, "r") as fp_file:
    contents = fp_file.read()

for key in replacements:
    contents = contents.replace(key, replacements[key])

with open(fp_to_edit, "w") as fp_file:
    fp_file.write(contents)