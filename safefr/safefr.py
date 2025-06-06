import argparse
import binascii
import re
import os
from collections import defaultdict


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(
        prog="safefr",
        description="Safe Find & Replace: find and replace a unique hexadecimal byte sequence in a file.",
    )
    parser.add_argument(
        "sequence",
        help="Specify your hexadecimal byte sequence as `prefix/find/replace/suffix` where the sequence `find` (preceded by `prefix` and succeeded by `suffix`) will be replaced with `replace`.",
    )
    parser.add_argument("file", help="The binary file to operate on.")

    args = parser.parse_args()
    seq = args.sequence
    file_path = args.file

    m = re.fullmatch(
        r"(?P<prefix>(?:[0-9a-fA-F]{2}\s*)*)/(?P<find>(?:[0-9a-fA-F]{2}\s*)+)/(?P<replace>(?:[0-9a-fA-F]{2}\s*)+)/(?P<suffix>(?:[0-9a-fA-F]{2}\s*)*)",
        seq,
    )
    if m is None:
        print("Your sequence does not match the expected format")
        return

    prefix_hex = re.sub(r"\s", "", m.group("prefix"))
    find_hex = re.sub(r"\s", "", m.group("find"))
    replace_hex = re.sub(r"\s", "", m.group("replace"))
    suffix_hex = re.sub(r"\s", "", m.group("suffix"))

    prefix = bytes.fromhex(prefix_hex) if len(prefix_hex) else b""
    find = bytes.fromhex(find_hex) if len(find_hex) else b""
    replace = bytes.fromhex(replace_hex) if len(replace_hex) else b""
    suffix = bytes.fromhex(suffix_hex) if len(suffix_hex) else b""
    if len(find) != len(replace):
        print("The length of the find and replace subsequences have to be equal")
        return

    search_hex = prefix_hex + find_hex + suffix_hex
    search = prefix + find + suffix
    if not os.path.exists(file_path):
        print(f"Could not find file: {file_path:}")
        return
    with open(file_path, "rb") as fd:
        data = fd.read()
        offsets = find_all_occurrences(data, search)
        if not offsets:
            print(f"Could not find sequence {search_hex:}")
        elif len(offsets) == 1:
            print(f"Found one occurrence of sequence {search_hex:}")
            update_file(file_path, data, search, prefix + replace + suffix)
        else:
            print(f"Found multiple occurrences of sequence {search_hex:}")
            print(
                "Identify the correct occurrence by its context, listed below, and re-run."
            )
            contexts = find_unique_contexts(data, offsets, prefix, find, suffix)
            max_pre = max(len(c[0]) for c in contexts)

            for i, (context_pre, search, context_post) in enumerate(
                sorted(contexts, key=lambda s: bytes(reversed(s[0])))
            ):
                context_pre_hex = binascii.hexlify(context_pre).decode("ascii")
                search_hex = binascii.hexlify(search).decode("ascii")
                context_post_hex = binascii.hexlify(context_post).decode("ascii")
                print(
                    f"{i:2}: {context_pre_hex: >{max_pre * 2}}/{search_hex:}/{replace_hex:}/{context_post_hex:}"
                )


def update_file(file_path, data, search, replace):
    data_mod = data.replace(search, replace)
    file_basename = os.path.basename(file_path)
    file_name_mod = file_basename + ".mod"
    if os.path.exists(file_name_mod):
        file_name_mod = find_uniq_filename(file_basename)
    with open(file_name_mod, "wb") as fd:
        print(f"Writing updated file to: {file_name_mod:}")
        fd.write(data_mod)


def find_uniq_filename(file_name):
    file_name_mod = file_name
    i = 1
    while os.path.exists(file_name_mod):
        file_name_mod = file_name + f".mod.{i:}"
        i += 1
    return file_name_mod


def find_unique_contexts(data, offsets, prefix, find, suffix):
    search = prefix + find + suffix
    i = 0
    assert all(data[o] == data[offsets[0]] for o in offsets)
    worklist = [offsets]
    # Those offsets that we have found the unique prefix context
    completed_pre_offsets = {}
    while worklist:
        new_worklist = []
        for offs in worklist:
            # We are assuming offs is sorted
            assert min(offs) == offs[0]
            if offs[0] - i < 0:
                assert offs[0] - i == -1
                # We've reached the edge, this makes this context unique
                completed_pre_offsets[offs[0]] = i - 1
                offs = offs[1:]
            freqs = defaultdict(list)
            for o in offs:
                # Group offsets with same byte
                freqs[data[o - i]].append(o)

            for freq_offs in freqs.values():
                if len(freq_offs) == 1:
                    # If this byte only occurred once, we're done with it
                    completed_pre_offsets[freq_offs[0]] = i
                else:
                    # If there are multiples, we need to search further
                    assert len(freq_offs) > 1
                    new_worklist.append(freq_offs)
        worklist = new_worklist
        i += 1

    i = 0
    assert all(
        data[o + len(search) - 1] == data[offsets[0] + len(search) - 1] for o in offsets
    )
    worklist = [offsets]
    # Those offsets that we have found the unique suffix context
    completed_post_offsets = {}
    while worklist:
        new_worklist = []
        for offs in worklist:
            # We are assuming offs is sorted
            assert max(offs) == offs[-1]
            if offs[-1] + len(search) + i >= len(data):
                assert offs[-1] + len(search) + i == len(data)
                # We've reached the edge, this makes this context unique
                completed_post_offsets[offs[-1]] = len(search) + i - 1
                offs.pop()
            freqs = defaultdict(list)
            for o in offs:
                # Group offsets with same byte
                freqs[data[o + len(search) + i]].append(o)
            for freq_offs in freqs.values():
                if len(freq_offs) == 1:
                    # If this byte only occurred once, we're done with it
                    completed_post_offsets[freq_offs[0]] = len(search) + i
                else:
                    # If there are multiples, we need to search further
                    assert len(freq_offs) > 1
                    new_worklist.append(freq_offs)
        worklist = new_worklist
        i += 1

    assert set(completed_post_offsets) == set(completed_pre_offsets)
    contexts = set()
    for o in completed_post_offsets:
        context_pre_i = completed_pre_offsets[o]
        context_post_i = completed_post_offsets[o]
        context_pre = data[o - context_pre_i : o + len(prefix)]
        search = data[o + len(prefix) : o + len(prefix) + len(find)]
        context_post = data[
            o + len(prefix) + len(find) : o + len(prefix) + len(find) + context_post_i
        ]
        assert (context_pre, search, context_post) not in contexts
        contexts.add((context_pre, search, context_post))
        assert (
            len(
                find_all_occurrences(
                    data, data[o - context_pre_i : o + context_post_i + 1]
                )
            )
            == 1
        )
    return contexts


def find_all_occurrences(data, search):
    offset = data.find(search)
    offsets = []
    while offset != -1:
        offsets.append(offset)
        offset = data.find(search, offset + 1)
    return offsets


if __name__ == "__main__":
    main()
