# Installation

Set up the analysis environment once, then connect the plugin to your assistant.
The Python environment runs the calculations on your computer or server. The
assistant reads the Skills, chooses the relevant steps with you and runs those
calculations. Installing a plugin does not install Python packages.

## 1. Check what you need

- Git and Python 3.12 on the machine that will run the analysis.
- Codex, Claude Code or DeepSeek Harness with access to that machine's files and terminal.
- Internet access for cloning and installing dependencies.
- A writable folder with room for the environment, input matrices and results.

Start with the CPU scVI example below; it does not need a GPU or public downloads.
For a real study, memory needs depend on the number of cells and genes. The plugin
does not automatically reduce your dataset to fit memory.

## 2. Download the repository and prepare Python

Choose the instructions for your operating system. Run each command in order.
If a command reports an error, resolve it before moving on.

### Windows: PowerShell, with files on D:

Open PowerShell. Check the prerequisites:

```powershell
git --version
py -3.12 --version
```

If a command is missing, install Git or Python 3.12 and reopen PowerShell. If you
already use Conda, you can instead create an environment with
`conda create -n scrna-workbench python=3.12`, activate it, and use `python` where
these instructions use `py -3.12`.

Clone into a new folder. If you already cloned it, change to that folder instead.

```powershell
Set-Location D:\
git clone https://github.com/Sculptor815/scrna-seq-workbench.git
Set-Location D:\scrna-seq-workbench
```

Keep this session's Python caches and temporary files on D: too:

```powershell
New-Item -ItemType Directory -Force D:\scrna-cache\tmp, D:\scrna-cache\pip, D:\scrna-cache\numba, D:\scrna-cache\matplotlib | Out-Null
$env:TEMP = 'D:\scrna-cache\tmp'
$env:TMP = 'D:\scrna-cache\tmp'
$env:PIP_CACHE_DIR = 'D:\scrna-cache\pip'
$env:NUMBA_CACHE_DIR = 'D:\scrna-cache\numba'
$env:MPLCONFIGDIR = 'D:\scrna-cache\matplotlib'
py -3.12 -m venv .venv
```

Install the core dependencies and check the package:

```powershell
.\.venv\Scripts\python.exe -m pip install -r plugins/scrna-seq-workbench/requirements-scvi.txt
.\.venv\Scripts\python.exe scripts/validate_package.py
.\.venv\Scripts\python.exe scripts/verify_benchmark.py
```

Both checks should print `PASS`. These commands use the environment directly,
so PowerShell does not need permission to run an activation script. In later
examples, replace `python` with `.\.venv\Scripts\python.exe`.

The cache variables apply to this PowerShell session and programs started from it.
An already-open desktop assistant does not inherit them. Give the assistant these
cache paths and the full interpreter path when starting an analysis. Your host's
own settings and plugin cache may still be stored on C:.

### Linux or macOS: terminal

Choose a location on the drive where you want to work:

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/Sculptor815/scrna-seq-workbench.git
cd scrna-seq-workbench
python3.12 -m venv .venv
.venv/bin/python -m pip install -r plugins/scrna-seq-workbench/requirements-scvi.txt
.venv/bin/python scripts/validate_package.py
.venv/bin/python scripts/verify_benchmark.py
```

Use `.venv/bin/python` wherever the examples below say `python`. If the system
does not provide `python3.12` or the venv module, install them through your system
administrator or Python distribution first.

### Default scVI, optional Harmony and condition differential expression

requirements-scvi.txt includes the core packages for the default representation
workflow. For explicitly selected Harmony, install requirements-harmony.txt instead;
it includes harmonypy and needs no PyTorch/scVI installation. Harmony requires
verified technical batches. Add condition DE dependencies when needed:

```text
python -m pip install -r plugins/scrna-seq-workbench/requirements-scvi.txt
python -m pip install -r plugins/scrna-seq-workbench/requirements-de.txt
```

For the selected Harmony route:

```text
python -m pip install -r plugins/scrna-seq-workbench/requirements-harmony.txt
```

The full pipeline may exceed 1 hour. scVI defaults to --device auto, using an
available compatible CUDA GPU or otherwise CPU. CPU scVI remains available if
you accept a longer wait; Harmony is an explicit CPU alternative, not an automatic
fallback. For GPU use, follow the
[PyTorch installation selector](https://pytorch.org/get-started/locally/) for your
system, then check `python -c "import torch; print(torch.cuda.is_available())"`.
Use `--device gpu` only when the environment can access a compatible GPU.

## 3. Connect your assistant

Follow the section for your software in [Host setup](HOSTS.md). Installing the
plugin and configuring Python are separate steps; the assistant needs both.

For your first session, give it the actual interpreter and checkout paths:

> Use scRNA-seq Workbench from D:/scrna-seq-workbench.
> Run Python with D:/scrna-seq-workbench/.venv/Scripts/python.exe.
> Use D:/scrna-cache for temporary files and package caches.
> List the six available Skills and check that their scripts can be read.
> Then help me run the synthetic example in docs/QUICKSTART.md.

Replace the paths if you chose a different location. You can write your requests
in your preferred language; the bundled documentation is in English.

## 4. Run the first example

Follow [Your first analysis](QUICKSTART.md). It creates 400 artificial cells,
checks QC, trains a short scVI model and computes UMAP and proposes two broad cell types. This checks that
the environment works before you provide experimental data.

After that, follow [Analyze your own data](USAGE.md), which covers required files,
sample metadata, parameter choices, annotation review and condition comparisons.

## Updating

In a clean checkout, run `git pull --ff-only`, then install the requirements for
the stages you use again. Refresh the plugin through your host as described in
[Host setup](HOSTS.md). Tell the assistant which checkout and Python environment
to use. Keep previous results in their existing run directories.

## Troubleshooting

| Problem | What to check |
|---|---|
| `ModuleNotFoundError` | Install the relevant requirements using the same Python executable that runs the analysis. |
| Skill not listed | Check the project root and marketplace, enable the plugin, and start a fresh session. See Host setup. |
| Output directory already exists | Choose a new run name. Completed and failed runs retain their reports. |
| No mitochondrial genes matched | Check species and gene identifiers. Ensembl-only names need a documented symbol mapping before symbol-based QC. |
| Metadata must match all cell IDs | Provide one row per matrix barcode, including any sample prefix or barcode suffix. |
| Windows cache path error | Use the short cache paths above in the process that starts Python. |
| Permission or network error | Check access in the assistant's execution environment; a command working in your own terminal may have different permissions. |

## Using a remote server

XFTP can transfer the repository and data; Xshell can open the remote terminal.
Set up Python on the server and run commands there using server paths, rather
than Windows drive letters. For a cluster, use the site's scheduler and resource
limits. The plugin does not submit scheduler jobs automatically. A local assistant
needs an authorized remote execution connection to operate that environment;
otherwise it can prepare commands for you to run in Xshell.
