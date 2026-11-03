# Stream Video from Online

**Category:** Graphics and Multimedia

## Problem

Try to create your own online streaming video player.

## Solution

A stdlib HTTP server with proper `Range: bytes=start-end` handling (206 Partial Content, `Content-Range`, `Accept-Ranges`) plus an HTML5 `<video>` page. Browsers can seek instantly because only the requested byte range is read from disk. The demo checks a 100-byte range against a generated file.

## How to run

Requires Python 3.8+ and no third-party packages.

```bash
python3 main.py movie.mp4 --port 8003    # open http://127.0.0.1:8003/
python3 main.py --demo
```

## Example

```text
player page: True
range status: 206 | bytes: 100
content-range: bytes 100-199/1024012
file size: 1024012
```

## Attribution

The problem statement is from [karan/Projects](https://github.com/karan/Projects), a list of practical projects that anyone can solve in any programming language (MIT License, Copyright (c) 2013 Karan Goel). The Python solution in this repository was implemented by [bspreston-esq](https://github.com/bspreston-esq).

This repository is part of the [Projects-Python-All](https://github.com/bspreston-esq/Projects-Python-All) collection.
