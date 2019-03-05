# latex-warnings
A commandline wrapper for a latex process that parses errors and warnings,
and appends to the output in a better understandable format.

## Usage:

Simply prefix your tex-output producing command with this wrapper:

```
latex_warnings.py latex ...
latex_warnings.py latexmk ...
latex_warnings.py pdflatex ...
```

## Output:

```
<normal command output>
---Warnings and Errors---
File ./main.tex
  Latex Warning [...]
  Latex Warning [...]
  Overfull [...]
File ./subfile.tex
  ! Error [...]
```

## Options:

```
latex_warnings.py -V COMMAND...
```

Increases verbosity:

- prints Over-/Underfull warnings.
- prints all filenames, not just tex files.


## How it works:

- It runs the command, and lets it print to stdout as usual.
- It capture stderr and redirects it into the stdout stream.
- It replaces the default 80-column line width of tex commands with a large value via a environment variable to effectively disable it.
- It collects the combined output, and scans it for warnings and errors.
- It will try to open all `.tex` files encountered in the output
  and case-insensitive search it for `todo` or `fixme` annotations.
- It will _colorize_ the processed list ot warnings to make it easier to read.
