import sublime
import sublime_plugin

import os

from .keymap_manager import tools


class KmRemapKeyCommand(sublime_plugin.WindowCommand):

    items = []

    def run(self):

        items = []
        names = ["Default.sublime-keymap"]
        if sublime.platform() == "windows":
            names += ["Default (Windows).sublime-keymap"]
            platforms = ["(OSX)", "(Linux)"]
        elif sublime.platform() == "osx":
            names += ["Default (OSX).sublime-keymap"]
        else:
            names += ["Default (Linux).sublime-keymap"]

        for resource in sorted(tools.find_resources("*.sublime-keymap"), key=lambda x: x.lower()):
            # Filter platform keymap
            if not any([n in resource for n in names]) or resource[:14] == "Packages/User/":
                continue

            keys = []
            # items[resource] = []
            for key in tools.decode_value(tools.load_resource(resource)):
                keys += [key["keys"]] if key["keys"] not in keys else []
            items += [{"resource": resource, "keys": sorted(keys, key=lambda x: " ".join(x).lower())}]

        # Save items sorted
        self.items = [[key, item["resource"]] for item in items for key in item["keys"]]

        message = [["%s: %s" % (os.path.dirname(key[9:]), " ".join(item)), key] for item, key in self.items]
        self.window.show_quick_panel(message, self.on_done_quick_panel)

    def on_done_quick_panel(self, i):
        if i < 0:
            return

        self.source_keys = self.items[i][0]
        self.source_resource = self.items[i][1]

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
        for item in resource:
            if item["km_keys"] == self.source_keys:
                resource.remove(item)

        # Add new keymaps
        for item in [item for item in tools.decode_value(tools.load_resource(self.source_resource)) if item["keys"] == self.source_keys]:
            # Save infos to handle later updates and update keys itself
            item["km_keys"] = self.source_keys
            item["km_source"] = self.source_resource
            item["keys"] = [s.strip() for s in self.target_key.split(" ")]

            resource += [item]

        # Save resource
        tools.save_resource("Packages/User/%s" % os.path.basename(self.source_resource), tools.encode_value(resource))

sublime.set_timeout(lambda: sublime.active_window().run_command("km_remap_key"), 300)
