import sublime
import sublime_plugin

import codecs
import fnmatch
import json
import os
import re


def find_names():
    if sublime.platform() == "windows":
        return ["Default.sublime-keymap", "Default (Windows).sublime-keymap"]
    elif sublime.platform() == "osx":
        return ["Default.sublime-keymap", "Default (OSX).sublime-keymap"]
    else:
        return ["Default.sublime-keymap", "Default (Linux).sublime-keymap"]


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
            string = sublime.load_resource(name)
        else:
            with codecs.open(os.path.join(sublime.packages_path(), name[9:]), "r", "utf-8") as f:
                string = f.read()
    except:
        string = None

    return string if string else ""


def save_resource(name, string):
    with codecs.open(os.path.join(sublime.packages_path(), name[9:]), "w", "utf-8") as f:
        f.write(string)


def decode_value(string):
    try:
        if hasattr(sublime, 'decode_value'):
            value = sublime.decode_value(string)
        else:
            string = re.sub(re.compile(r"//.*?\n"), "", string)
            string = re.sub(re.compile(r"/\*.*?\*/", re.DOTALL), "", string)
            value = json.loads(string)
    except:
        value = None

    return value if value else []


def encode_value(value, pretty=True):
    lstItems = []
    for objItem in sorted(value, key=lambda x: x["keys"]):
        lstFields = []
        # strItem = "\n\t{"
        lstFields += ["\"keys\": " + json.dumps(objItem["keys"], ensure_ascii=False)]
        if "command" in objItem:
            lstFields += ["\"command\": " + json.dumps(objItem["command"], ensure_ascii=False) + (", \"args\": " + json.dumps(objItem["args"], ensure_ascii=False) if "args" in objItem else "")]
        if "context" in objItem:
            lstFields += ["\"context\": [" + ",".join(["\n\t\t\t" + json.dumps(item, ensure_ascii=False) for item in sorted(objItem["context"], key=lambda x: x["key"])]) + "\n\t\t]"]
        if "km_keys" in objItem:
            lstFields += ["\"km_keys\": " + json.dumps(objItem["km_keys"], ensure_ascii=False)]
        if "km_source" in objItem:
            lstFields += ["\"km_source\": " + json.dumps(objItem["km_source"], ensure_ascii=False)]
        lstItems += ["\n\t{\n\t\t" + ",\n\t\t".join(lstFields) + "\n\t}"]
    value = "[" + ",".join(lstItems) + "\n]"
    return value


def find_item(value, km_keys, km_source):
    for item in value:
        if "km_keys" in item and "km_source" in item:
            if item["km_keys"] == km_keys and item["km_source"] == km_source:
                # print("found", item)
                return item
    return None


# def update_item(value, km_keys, km_source):

def clear_resource(value, items):
    # print(items)
    for item in items:
        while True:
            try:
                value.remove(find_item(value, item["km_keys"], item["km_source"]))
            except:
                break
    return value
