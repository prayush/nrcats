import re

with open("paper.tex", "r") as f:
    text = f.read()

# Fix table math split
text = text.replace(
    r"$\chi_\perp < \varepsilon_\chi$, $ & \chi_{1z} & + & \chi_{2z} & < \varepsilon_\chi$, $e > \varepsilon_e$",
    r"$\chi_\perp < \varepsilon_\chi$, $|\chi_{1z}| + |\chi_{2z}| < \varepsilon_\chi$, $e > \varepsilon_e$",
)
text = text.replace(
    r"$\chi_\perp < \varepsilon_\chi$, $ & \chi_{1z} & + & \chi_{2z} & \geq \varepsilon_\chi$, $e > \varepsilon_e$",
    r"$\chi_\perp < \varepsilon_\chi$, $|\chi_{1z}| + |\chi_{2z}| \geq \varepsilon_\chi$, $e > \varepsilon_e$",
)
text = text.replace(
    r"$\chi_\perp < \varepsilon_\chi$, $ & \chi_{1z} & + & \chi_{2z} & < \varepsilon_\chi$, $e \leq \varepsilon_e$",
    r"$\chi_\perp < \varepsilon_\chi$, $|\chi_{1z}| + |\chi_{2z}| < \varepsilon_\chi$, $e \leq \varepsilon_e$",
)
text = text.replace(
    r"$\chi_\perp < \varepsilon_\chi$, $ & \chi_{1z} & + & \chi_{2z} & \geq \varepsilon_\chi$, $e \leq \varepsilon_e$",
    r"$\chi_\perp < \varepsilon_\chi$, $|\chi_{1z}| + |\chi_{2z}| \geq \varepsilon_\chi$, $e \leq \varepsilon_e$",
)

# Fix _et al._
text = text.replace(r"_et al._", r"\textit{et al.}")
text = text.replace(r"et al._", r"\textit{et al.}")  # Just in case
text = text.replace(r"_To be filled in._", r"\textit{To be filled in.}")
text = text.replace(r"parameter-space mismatch_", r"parameter-space mismatch")


# Fix backticks
def repl_backticks(m):
    inner = m.group(1).replace("_", r"\_")
    return r"\texttt{" + inner + "}"


text = re.sub(r"`([^`]+)`", repl_backticks, text)

# Fix \[ \] which is used for citations in the markdown but compiles as math in latex
# Actually I already replaced \[ and \] in a previous sed command! So they are just [ and ].
# But wait, looking at the grep output earlier, they are still \[ninja1\]!
# Why? Because my previous sed command did: sed -i 's/\\[/[/g' paper.tex which was wrong escaping.
text = text.replace(r"\[", "[")
text = text.replace(r"\]", "]")

with open("paper.tex", "w") as f:
    f.write(text)
