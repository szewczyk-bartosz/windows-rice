import sys
import pywal
from pathlib import Path

def gen_section(imgpath, word="hello"):
    finalString = ""
    colors = pywal.colors.get(imgpath)
    print("output is:", colors)

    for name, color in colors["colors"].items():
        print(color)
    
    finalString += f"<img src='{imgpath}' style='width: 900px; height: 600px;'>\n"
    finalString += f"<table>\n"
    finalString += "<tr>"

    for name, color, in colors["colors"].items():
        finalString += f"<th style='background-color: {color}'>{name[-2:]}</th>"
    finalString += "</tr>"
    for name_, color in colors["colors"].items():
        tmp = f"<tr style='color: {color}'>"
        i = 0
        for name, color in colors["colors"].items():
            if i == 0:
                tmp += f"<td style='background-color: {color}'>{name_}</td>"
            else:
                tmp += f"<td style='background-color: {color}'>{name}</td>"
        tmp += "</tr>"
        finalString += tmp

    finalString += f"</table>\n"
    finalString += "<hr></hr>"
    return finalString

if __name__ == "__main__":


    imgpath = pywal.image.get(sys.argv[1])
    outStr = ""

    for img in sys.argv[1:]:
        outStr += gen_section(img)

    with open("base.html", "r") as base:
        with open("output.html", "w") as out:
            out.write(base.read().replace("#REPLACE#", outStr))








