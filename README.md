# SafeFR
Safe Find &amp; Replace: Find and replace a unique byte sequence in a file.
If the provided byte sequence is not unique (there are multiple occurrences), SafeFR identifies a unique context around each occurrences.

## Install
```sh
git clone git@github.com:NicolaasWeideman/SafeFR.git
cd SafeFR
python3 -m pip install .
```

## Example
We have a `hello_world` binary that we want to modify to print `Hello, SafeFR` instead of `Hello, world.`.
We use `SafeFR` to replace `world.` in the string in the binary with `SafeFR` (note these two strings are equally long).
First, we find the hexadecimal representation of the two strings:
```bash
$ echo -n 'world.' | xxd -p
776f726c642e
$ echo -n 'SafeFR' | xxd -p
536166654652
```
Then, we instruct `SafeFR` to replace `776f726c642e` (`world.`) with `536166654652` (`SafeFR`).
```bash
$ safefr '/776f726c642e/536166654652/' hello_world
Found multiple occurrences of sequence 776f726c642e
Identify the correct occurrence by its context, listed below, and re-run.
 0: 20/776f726c642e/536166654652/00
 1: 5f/776f726c642e/536166654652/63
```
But, `SafeFR` identifies two instances of the string `world.` in the binary and asks us which we want to replace.
It lists each occurence of this string it discovered in a unique context.
We know strings in `C` are `NULL` terminated, so we know the `20/776f726c642e/536166654652/00` option is the one we want (note the suffix `/00` indicating the `NULL` byte).
We re-run `SafeFR` with this string.
```bash
$ safefr 20/776f726c642e/536166654652/00 hello_world
Found one occurrence of sequence 20776f726c642e00
Writing updated file to: hello_world.mod
```
We run `hello_world.mod` and confirm the binary has been modified.
```bash
$ ./hello_world.mod
Hello, SafeFR
```

## Run Test Cases
```sh
python3 -m pytest ./test/test_safefr.py
```
