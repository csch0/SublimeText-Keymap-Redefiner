import sublime
import sublime_plugin

import codecs
import os


def find_resources(pattern):
    resources = []
    if hasattr(sublime, 'find_resources'):
        resources = sublime.find_resources(pattern)
    else:
        for root, dir_names, file_names in os.walk(sublime.packages_path()):
            for file_name in file_names:
                rel_path = os.path.relpath(os.path.join(root, file_name), sublime.packages_path())
                if fnmatch.fnmatch(rel_path.lower(), "*" + pattern.lower()):
                    resources += [os.path.join('Packages', rel_path)]
    return resources


def load_resource(name):
    try:
        if hasattr(sublime, 'load_resource'):
            return sublime.load_resource(name)
        else:
            with open(os.path.join(sublime.packages_path(), name[9:])) as f:
                return f.read()
    except:
        return None


def save_resource(name, string):
    with codecs.open(os.path.join(sublime.packages_path(), name[9:]), "w", "utf-8") as f:
        f.write(string)


def decode_value(string):
    if not string:
        return []
    if hasattr(sublime, 'decode_value'):
        return sublime.decode_value(string)
    else:
        lines = [line for line in string.split("\n") if not re.search(r'//.*', line)]
        return json.loads("\n".join(lines))


def encode_value(value, pretty=True):
    if hasattr(sublime, 'encode_value'):
        return sublime.encode_value(value, pretty)
    else:
        lines = [line for line in string.split("\n") if not re.search(r'//.*', line)]
        return json.loads("\n".join(lines))
