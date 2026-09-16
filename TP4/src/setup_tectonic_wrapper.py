import os
import json

# 1. Update LaTeX Workshop settings to use %DOCFILE_EXT% and %DOC_EXT%
tool_cfg = {
    "name": "tectonic",
    "command": "C:/Users/USER/AppData/Local/Programs/tectonic/tectonic-wrapper.bat",
    "args": [
        "--synctex",
        "--keep-logs",
        "%DOCFILE_EXT%"
    ],
    "env": {}
}

recipe_cfg = {
    "name": "tectonic",
    "tools": ["tectonic"]
}

# Update User settings
user_settings_path = r"C:\Users\USER\AppData\Roaming\Antigravity IDE\User\settings.json"
if os.path.exists(user_settings_path):
    with open(user_settings_path, "r", encoding="utf-8") as f:
        u_cfg = json.load(f)
    u_cfg["latex-workshop.latex.tools"] = [tool_cfg]
    u_cfg["latex-workshop.latex.recipes"] = [recipe_cfg]
    u_cfg["latex-workshop.latex.autoBuild.run"] = "onSave"
    u_cfg["latex-workshop.view.pdf.viewer"] = "tab"
    with open(user_settings_path, "w", encoding="utf-8") as f:
        json.dump(u_cfg, f, indent=4)
    print("User settings updated with %DOCFILE_EXT%")

# Update Workspace settings
ws_settings_path = r"d:\mateo\IndiaInData\.vscode\settings.json"
if os.path.exists(ws_settings_path):
    with open(ws_settings_path, "r", encoding="utf-8") as f:
        w_cfg = json.load(f)
    w_cfg["latex-workshop.latex.tools"] = [tool_cfg]
    w_cfg["latex-workshop.latex.recipes"] = [recipe_cfg]
    w_cfg["latex-workshop.latex.autoBuild.run"] = "onSave"
    w_cfg["latex-workshop.view.pdf.viewer"] = "tab"
    with open(ws_settings_path, "w", encoding="utf-8") as f:
        json.dump(w_cfg, f, indent=4)
    print("Workspace settings updated with %DOCFILE_EXT%")

# 2. Also create a pdflatex.bat and tectonic-wrapper.bat that automatically appends .tex if missing
wrapper_lines = [
    "@echo off",
    "setlocal enabledelayedexpansion",
    "set FINAL_ARGS=",
    ":loop",
    'if "%~1"=="" goto done',
    "set CURR=%~1",
    "set FIRST_CHAR=%CURR:~0,1%",
    'if not "%FIRST_CHAR%"=="-" (',
    '    if not exist "%CURR%" (',
    '        if exist "%CURR%.tex" (',
    "            set CURR=%CURR%.tex",
    "        )",
    "    )",
    ")",
    "set FINAL_ARGS=!FINAL_ARGS! !CURR!",
    "shift",
    "goto loop",
    ":done",
    '"C:\\Users\\USER\\AppData\\Local\\Programs\\tectonic\\tectonic.exe" !FINAL_ARGS!'
]
wrapper_text = "\r\n".join(wrapper_lines) + "\r\n"

tectonic_dir = r"C:\Users\USER\AppData\Local\Programs\tectonic"
for fname in ["tectonic-wrapper.bat", "pdflatex.bat"]:
    p = os.path.join(tectonic_dir, fname)
    with open(p, "w", encoding="utf-8") as f:
        f.write(wrapper_text)
    print(f"Created {fname} in {tectonic_dir}")
