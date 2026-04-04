import subprocess
import re

def extract_and_run_code(text: str, auto_run: bool = False):
    pattern = r"```(python|bash|shell|cmd|c|cpp)\n(.*?)```"
    blocks = re.findall(pattern, text, re.DOTALL)

    if not blocks:
        return

    for lang, code in blocks:
        print(f"\n[Executor] [{lang}]:\n{code.strip()}")
        
        if not auto_run:
            confirm = input("Execute? (y/n): ").strip().lower()
            if confirm != "y":
                continue

        try:
            if lang == "python":
                result = subprocess.run(
                    ["python", "-c", code],
                    capture_output=True, text=True, timeout=15
                )
                print("[Output]:", result.stdout or result.stderr)

            elif lang in ("bash", "shell", "cmd"):
                result = subprocess.run(
                    code, shell=True,
                    capture_output=True, text=True, timeout=15
                )
                print("[Output]:", result.stdout or result.stderr)

            elif lang in ("c", "cpp"):
                ext = "c" if lang == "c" else "cpp"
                compiler = "gcc" if lang == "c" else "g++"
                src = f"temp_autoagent.{ext}"
                exe = "temp_autoagent.exe"

                with open(src, "w") as f:
                    f.write(code)

                compile_result = subprocess.run(
                    [compiler, src, "-o", exe],
                    capture_output=True, text=True
                )
                if compile_result.returncode != 0:
                    print("[Compile Error]:", compile_result.stderr)
                else:
                    run_result = subprocess.run(
                        [f".\\{exe}"],
                        capture_output=True, text=True, timeout=15
                    )
                    print("[Output]:", run_result.stdout or run_result.stderr)

        except Exception as e:
            print("[Error]:", e)