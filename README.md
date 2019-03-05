# latex-warnings
A commandline wrapper for a latex process that parses errors and warnings,
and appends to the output in a better understandable format.

## Usage:

Simply prefix your tex-output producing command with this wrapper:

```
latex_wrapper.py latex ...
latex_wrapper.py latexmk ...
latex_wrapper.py pdflatex ...
```

## Example Output:

```
<normal command output>
---Warnings and Errors---
File ./main.tex
  Latex Warning [...]
  Latex Warning [...]
  Overfull [...]
Fill ./subfile.tex
  ! Error [...]
```

## Options:

```
latex_wrapper.py -V COMMAND...
```

Increases verbosity:

- prints Over-/Underfull warnings.
- prints all filenames, not just tex files.


## How it works:

- It runs the command, and lets it print to stdout as usual.
- It capture stderr and redirects it into the stdout stream.
- It replaces the default 80-column line width of tex commands with a large value via a environment variable to effectively disable it.
- It collects the combined output, and scans it for warnings and errors.
