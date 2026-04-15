---
name: modal
description: Run code on Modal's cloud infrastructure via `uvx modal run`. Use whenever the user wants to (1) validate handbook tutorial shell commands on a fresh Debian container from scratch (uv, pip, build tooling, etc. with no cached state from Tim's laptop), (2) test GPU-specific Python code (torch, CUDA, cupy, transformers, CUDA wheels) on real hardware, or (3) reproduce a "does this actually work from zero?" check. Trigger on phrases like "run this on modal", "test on a fresh machine", "try this on a GPU", "validate from scratch", "does the tutorial work end-to-end", "test this without my venv state", or any mention of modal.com / cloud GPUs / ephemeral containers for verification. Also trigger when the user is writing a handbook tutorial that involves GPU installs (PyTorch, CUDA wheels) and they want to confirm the commands work.
---

# Modal: ephemeral cloud execution

Modal runs Python and shell workloads in ephemeral cloud containers. This skill drives it through `uvx modal run` — no persistent install needed. The Modal token is already configured on this machine, so never run `modal setup`.

Two reasons to use this skill:

1. **Fresh-environment validation** — verify a handbook tutorial's commands (`uv init`, `uv add`, `uv sync`, `pip install`, build/publish flows) work end-to-end on a clean Debian container with none of Tim's laptop state leaking in.
2. **GPU code testing** — run code that needs an actual CUDA device on a real GPU. Tim's laptop has no NVIDIA GPU, so anything involving `torch.cuda`, CUDA wheels, or `--index` selection for `cu128` etc. must be validated remotely.

Default GPU: **T4**. It's the cheapest, fits comfortably in the free monthly credit, and is sufficient for validating that `torch.cuda.is_available()` is True and imports work. Only pick A10G/A100/H100 when the workload actually needs the memory or speed — and say why in a comment.

All runs are ephemeral. Write a throwaway script to `/tmp/`, run it, read the output, delete it. Don't create named persistent apps, Volumes, or Secrets for validation work.

## Workflow

1. Pick the right template (shell validation vs GPU Python). See templates below.
2. Write the script to `/tmp/modal_<short-name>.py`.
3. Run it: `uvx modal run /tmp/modal_<short-name>.py`.
4. Stream output back. stdout/stderr from the remote function appears inline as the container runs.
5. Delete `/tmp/modal_<short-name>.py` when the validation is complete.

The first run for a given image spec takes a minute or two to build. Subsequent runs with the same image definition reuse Modal's cached layers and start in seconds — this is why the templates below bias toward declaring dependencies on the image rather than installing them at runtime.

## Template: shell validation on fresh Debian + uv

Use this to validate handbook tutorials whose steps are shell commands. The handbook's canonical stack is `uv`, so the image pre-installs it.

```python
import modal

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("uv")
    .run_commands("uv --version")  # sanity-check that uv is on PATH
)
app = modal.App("validate-shell")

@app.function(image=image, timeout=900)
def run():
    import subprocess, sys

    def sh(cmd: str, cwd: str | None = None) -> None:
        print(f"$ {cmd}" + (f"  (cwd={cwd})" if cwd else ""), flush=True)
        # Inherit stdio so output streams live and stderr shows up regardless
        # of exit code. uv writes most of its progress to stderr, so a captured
        # run where stderr only prints on failure looks deceptively silent.
        r = subprocess.run(cmd, shell=True, cwd=cwd)
        if r.returncode != 0:
            raise SystemExit(f"command failed: {cmd!r} (exit {r.returncode})")

    # --- edit below: the tutorial steps to validate ---
    sh("uv init myproj")
    sh("uv add requests httpx", cwd="myproj")
    sh("uv sync", cwd="myproj")
    sh("uv run python -c 'import requests, httpx; print(requests.__version__, httpx.__version__)'", cwd="myproj")

@app.local_entrypoint()
def main():
    run.remote()
```

Key detail: let `subprocess` inherit stdout/stderr rather than using `capture_output=True`. `uv` (and many other tools) write progress to stderr even on success, so a captured helper that only prints stderr on failure makes a successful `uv add` or `uv sync` look silent and broken. Streaming also means Modal's log forwarder shows output as it happens instead of in one block at the end.

## Template: GPU Python (T4 + torch)

```python
import modal

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("torch", "numpy")
)
app = modal.App("gpu-check")

@app.function(image=image, gpu="T4", timeout=900)
def run():
    import torch
    print("cuda available:", torch.cuda.is_available())
    print("device:", torch.cuda.get_device_name(0))
    x = torch.randn(2048, 2048, device="cuda")
    print("matmul norm:", (x @ x).norm().item())

@app.local_entrypoint()
def main():
    run.remote()
```

For CUDA-wheel validation (the PyTorch handbook pages care about this), install torch via its CUDA-specific index inside the image:

```python
image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "torch",
    index_url="https://download.pytorch.org/whl/cu124",
)
```

## Template: run a handbook example script against a fresh container

If the code to validate already lives on disk (e.g. in the handbook repo), mount it rather than inlining it.

```python
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("uv")
    .add_local_file("/Users/tdhopper/repos/python-developer-tooling-handbook/examples/foo.py", "/work/foo.py")
)

@app.function(image=image, timeout=600)
def run():
    import subprocess
    subprocess.run(["uv", "run", "/work/foo.py"], check=True)
```

`add_local_dir` is the directory equivalent. Both happen at container start, not image build, so they don't invalidate the image cache.

## Rules of thumb

- Always include `@app.local_entrypoint()`. Inside it, call `your_func.remote()` — `.remote()` runs in the cloud, `.local()` runs on the host (not what you want). `modal run` needs an entrypoint to invoke.
- Declare dependencies on the `Image`, not inside the function body. `image.pip_install(...)`, `image.apt_install(...)`, `image.run_commands(...)`. Runtime pip installs defeat Modal's layer cache and slow every run.
- Set an explicit `timeout=` in seconds on `@app.function`. Default is 5 minutes; bump to 900–1800 for tutorials that download big wheels (torch ~2GB) or do cold CUDA installs.
- Use `gpu="T4"` unless a specific reason argues otherwise. Valid alternatives in ascending cost: `"L4"`, `"A10G"`, `"A100"`, `"A100-80GB"`, `"H100"`.
- Prefer explicit failure over silent success — use `check=True` on `subprocess.run` (or the manual pattern shown in the shell template).
- Delete the `/tmp/modal_*.py` script after the run so the workspace stays clean.

## What NOT to do

- Don't run `modal setup` — the token is already configured.
- Don't create named apps, Volumes, or Secrets for validation work. Ephemeral only; a crashed or forgotten named app can keep running and burn credit.
- Don't `uv add modal` or `pip install modal` into the handbook project. Invocation is always `uvx modal run ...`.
- Don't use a bigger GPU "just in case". The free tier is finite.
- Don't validate on the handbook repo's real `pyproject.toml` from inside the Modal container — mount a minimal reproducer or let the container start from scratch.

## Troubleshooting

- **`ModuleNotFoundError` inside the function**: missing from `image.pip_install(...)`. Add it to the image, not the function.
- **Very slow first run**: Modal is building the image. Subsequent runs with the same image spec are fast. If you're iterating on the function body but not the image, leave the image definition alone so it stays cached.
- **`modal.exception.InvalidError: no app running`**: `.remote()` was called outside a `local_entrypoint` or an enclosing `with app.run():` block. Wrap it.
- **`function timed out`**: increase `timeout=`.
- **GPU capacity error on T4**: fall back to `"L4"` or `"A10G"`. T4 capacity is occasionally tight.
- **Tutorial step works locally, fails on Modal**: that's the point of this skill — it's telling you the tutorial depends on something on Tim's laptop (pre-installed binary, cached venv, environment variable, `~/.config` state). Fix the tutorial, not the Modal script.
