# Job Scraper

For Seminar Algorithmic Auditing, FS24.

## Run

It is recommended to install microconda (works better with VSCode) or micromamba.

### Using Conda (recommended)

```sh
conda activate -p ./envs
python main.py
```

## Setup

### Python

#### Using Conda (recommended)

```sh
conda create -p ./envs python=3.12.*
conda activate -p ./envs
pip install -r requirements.txt
```

### VSCode

Copy `settings.json.default` to `settings.json`.

```sh
cp .vscode/settings.json.default .vscode/settings.json
```

Make sure you're using the correct interpreter with VSCode.

<kbd>CTRL</kbd> + <kbd>P</kbd> > "Python: Select Interpreter" > ".envs/bin/python".
