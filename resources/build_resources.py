
import glob
import os

fl = []

for file in glob.glob("*.png"):
	fl.append(f"<file>{file}</file>")

rfiles = "\n".join(fl)

out = f"""
<RCC>
<qresource>
{rfiles}
</qresource>
</RCC>
"""

print(out)
