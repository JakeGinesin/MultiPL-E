from pathlib import Path
from safe_subprocess import run
import subprocess

# return codes for coqc:
# 0: compilation goes through 
# 1: some sort of error (nondescript)

def eval_script(path: Path):
    cleanup_extensions = ['.vo', '.vok', '.vos']

    try:
        # sadly there seems to be no way to verify proofs in a coq file without compiling
        output = subprocess.run(["coqc -noglob", str(path)], capture_output=True, timeout=5)
        outmessage = str(output)

        if output.returncode == 0:
            status = "OK"
            # cleanup: remove files generated by coqc
            for ext in cleanup_extensions:
                file_to_remove = path.with_suffix(ext)
                if file_to_remove.exists():
                    file_to_remove.unlink()

        elif "Unable to unify" in outmessage:
            status = "AssertionError"
            returncode = -1
        else:
            status = "SyntaxError"

    except subprocess.TimeoutExpired as exc:
        status = "Timeout"
        output = exc
        returncode = -1
    return {
        "status": status,
        "exit_code": returncode,
        "stdout": "" if output.stdout is None else output.stdout.decode("utf-8"),
        "stderr": "" if output.stderr is None else output.stderr.decode("utf-8"),
    }
