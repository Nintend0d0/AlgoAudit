# Job Scraper & Evaluation

For Seminar Algorithmic Auditing, FS24.

## Setup

### Python

#### Using Conda (recommended)

```sh
# at project root
conda create -p ./envs python=3.12.*
conda activate ./envs
pip install -r requirements.txt
```

### VSCode

Copy `settings.json.default` to `settings.json`.

```sh
# at project root
cp .vscode/settings.json.default .vscode/settings.json
```

Make sure you're using the correct interpreter with VSCode.

<kbd>CTRL</kbd> + <kbd>P</kbd> > "Python: Select Interpreter" > ".envs/bin/python".

## Run Scraper

It is recommended to install microconda (works better with VSCode) or micromamba.

### Using Conda (recommended)

```sh
conda activate ./envs
cd scraper/ # important
python main.py
```

## Run Evaluation

### Using Conda (recommended)

```sh
# TODO
```
