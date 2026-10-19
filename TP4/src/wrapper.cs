using System;
using System.Diagnostics;
using System.IO;
using System.Collections.Generic;

class Program {
    static int Main(string[] args) {
        string tectonicExe = @"C:\Users\USER\AppData\Local\Programs\tectonic\tectonic.exe";
        if (!File.Exists(tectonicExe)) {
            Console.Error.WriteLine("Tectonic not found at: " + tectonicExe);
            return 1;
        }

        List<string> cleanArgs = new List<string>();
        cleanArgs.Add("--synctex");
        cleanArgs.Add("--keep-logs");

        foreach (var raw in args) {
            string a = raw.Trim('"');
            if (string.IsNullOrEmpty(a)) continue;

            if (a.StartsWith("-interaction=") || a.StartsWith("-halt-on-error") ||
                a.StartsWith("-file-line-error") || a == "-shell-escape" || a == "-no-shell-escape") {
                continue;
            }
            if (a.StartsWith("-synctex=") || a == "--synctex" || a == "-synctex") {
                continue;
            }
            if (a.StartsWith("-output-directory=")) {
                string dir = a.Substring("-output-directory=".Length);
                cleanArgs.Add("-o");
                cleanArgs.Add(dir);
                continue;
            }

            if (!a.StartsWith("-")) {
                if (!File.Exists(a) && File.Exists(a + ".tex")) {
                    a = a + ".tex";
                }
            }

            cleanArgs.Add(a);
        }

        ProcessStartInfo psi = new ProcessStartInfo();
        psi.FileName = tectonicExe;
        psi.Arguments = string.Join(" ", cleanArgs.ConvertAll(x => x.Contains(" ") ? "\"" + x + "\"" : x).ToArray());
        psi.UseShellExecute = false;

        try {
            using (Process p = Process.Start(psi)) {
                p.WaitForExit();
                return p.ExitCode;
            }
        } catch (Exception ex) {
            Console.Error.WriteLine("Error running tectonic: " + ex.Message);
            return 1;
        }
    }
}
