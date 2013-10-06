import sublime
import sublime_plugin

import os

from .keymap_redefiner import tools


class KeyReRemapKeyCommand(sublime_plugin.WindowCommand):

    items = []

    def run(self):

        items = []
        for resource in sorted(tools.find_resources("*.sublime-keymap"), key=lambda x: x.lower()):
            # Filter platform keymap
            if not any([n in resource for n in tools.find_names()]) or resource[:14] == "Packages/User/":
                continue

            keys = []
            for key in tools.decode_value(tools.load_resource(resource)):
                item = {"resource": resource, "keys": key["keys"]}
                items += [item] if item not in items else []

        # Save items sorted
        self.items = sorted(items, key=lambda x: [x["resource"], " ".join(x["keys"]).lower()])

        message = [["%s: %s" % (os.path.dirname(item["resource"][9:]), " ".join(item["keys"])), item["resource"]] for item in self.items]
        self.window.show_quick_panel(message, self.on_done_quick_panel)

    def on_done_quick_panel(self, i):
        if i < 0:
            return

        self.source_keys = self.items[i]["keys"]
        self.source_resource = self.items[i]["resource"]

        keys = " ".join(self.source_keys)
        self.window.show_input_panel("New Keymap for %s" % keys, keys, self.on_done_input_panel, None, None)

    def on_done_input_panel(self, s):
        if not s:
            return

        self.target_key = s
        self.on_done()

    def on_done(self):
        # Load resource
        resource = tools.decode_value(tools.load_resource("Packages/User/%s" % os.path.basename(self.source_resource)))

        # Remove old keymaps
        resource = tools.clear_resource(resource, [{"km_keys": self.source_keys, "km_source": self.source_resource}])

        # Add new keymaps
        for item in [item for item in tools.decode_value(tools.load_resource(self.source_resource)) if item["keys"] == self.source_keys]:
            # Save infos to handle later updates and update keys itself
            item["km_keys"] = self.source_keys
            item["km_source"] = self.source_resource
            item["keys"] = [s.strip() for s in self.target_key.split(" ")]

            resource += [item]

        # Save resource
        tools.save_resource("Packages/User/%s" % os.path.basename(self.source_resource), tools.encode_value(resource))
        sublime.status_message("Keymap Redefiner: %s was successfully redefined to %s" % (" ".join(self.source_keys), " ".join(self.target_key)))


class KeyReUpdateKeysCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        # Search through all file names
        for name in tools.find_names():
            # Load resource
            resource = tools.decode_value(tools.load_resource("Packages/User/%s" % name))

            items = []
            for key in resource:
                if "km_keys" in key and "km_source" in key:
                    items += [{"keys": key["keys"], "km_keys": key["km_keys"], "km_source": key["km_source"]}] if [key["km_keys"], key["km_source"]] not in [[item["km_keys"], item["km_source"]] for item in items] else []

            # Clear old keys
            resource = tools.clear_resource(resource, items)

            for item in items:
                target_key = item["keys"]
                source_keys = item["km_keys"]
                source_resource = item["km_source"]

                # Add new keymaps
                for item in [item for item in tools.decode_value(tools.load_resource(source_resource)) if item["keys"] == source_keys]:
                    # Save infos to handle later updates and update keys itself
                    item["km_keys"] = source_keys
                    item["km_source"] = source_resource
                    item["keys"] = target_key

                    resource += [item]

            tools.save_resource("Packages/User/%s" % name, tools.encode_value(resource))


class KeyReRemoveKeyCommand(sublime_plugin.WindowCommand):

    def run(self):

        items = []
        for resource in sorted(tools.find_resources("*.sublime-keymap"), key=lambda x: x.lower()):

            # Filter platform keymap
            if not any([n in resource for n in tools.find_names()]) or resource[:14] != "Packages/User/":
                continue

            for key in tools.decode_value(tools.load_resource(resource)):
                if "km_keys" in key and "km_source" in key:
                    item = {"keys": key["keys"], "km_keys": key["km_keys"], "km_source": key["km_source"]}
                    items += [item]

        # Save items sorted
        self.items = sorted(items, key=lambda x: " ".join(x["keys"]).lower())

        message = [["%s: %s" % (os.path.dirname(item["km_source"][9:]), " ".join(item["keys"])), item["km_source"]] for item in self.items]
        self.window.show_quick_panel(message, self.on_done_quick_panel)

    def on_done_quick_panel(self, i):
        if i < 0:
            return

        self.key = self.items[i]["keys"]
        self.km_keys = self.items[i]["km_keys"]
        self.km_source = self.items[i]["km_source"]

        if sublime.ok_cancel_dialog("Remove\n\t%s\nand use\n\t%s" % (" ".join(self.key), " ".join(self.km_keys)), "Reset"):
            self.on_done()

    def on_done(self):
        # Load resource
        resource = tools.decode_value(tools.load_resource("Packages/User/%s" % os.path.basename(self.km_source)))

        # Remove old keymaps
        resource = tools.clear_resource(resource, [{"km_keys": self.km_keys, "km_source": self.km_source}])

        # Save resource
        tools.save_resource("Packages/User/%s" % os.path.basename(self.km_source), tools.encode_value(resource))
        sublime.status_message("Keymap Redefiner: %s was successfully and reset to %s" % (" ".join(self.km_keys), " ".join(self.key)))


def plugin_loaded():
    s = sublime.load_settings("Keymap Redefiner.sublime-settings")
    if s.get("auto_update"):
        sublime.run_command("key_re_update_keys")
