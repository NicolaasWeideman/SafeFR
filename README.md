# SafeFR
Safe Find &amp; Replace: Find and replace a unique hexadecimal sequence in a file.
If the provided hexadecimal sequence is not unique (there are multiple occurrences), SafeFR identifies a unique context around each occurrences.

## Install
```sh
git clone git@github.com:NicolaasWeideman/SafeFR.git
cd SafeFR
python3 -m pip install .
```

## Run Test Cases
```sh
python3 -m pytest ./test/test_safefr.py
```
