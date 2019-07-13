import datetime, os, re

from gi.repository import GObject, Gedit, Gio


__all__ = ["AutonamePlugin"]


class AutonamePlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "AutonamePlugin"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.desktop_path = os.path.expanduser("~/Desktop/")
        self.path_regex = re.compile(
            "^" + self.desktop_path + r"\d\d\d\d-\d\d-\d\d-\d\d-\d\d-\d\d.*\.txt$"
        )

    def do_activate(self):
        self.window.autoname_plugin_handler_ids = [
            self.window.connect("tab-added", self.tab_added),
            self.window.connect(
                "active-tab-state-changed", self.active_tab_state_changed
            ),
            self.window.connect("tab-removed", self.tab_removed),
        ]

    def do_deactivate(self):
        for handler_id in self.window.autoname_plugin_handler_ids:
            self.window.disconnect(handler_id)

    def do_update_state(self):
        pass

    def tab_added(self, window, tab):
        self.maybe_set_name(tab.get_document())

    def active_tab_state_changed(self, window):
        self.maybe_rename(window.get_active_tab().get_document())

    def tab_removed(self, window, tab):
        self.maybe_delete(tab.get_document())

    def maybe_set_name(self, document):
        if not self.is_unnamed(document):
            return

        datetimestr = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"{datetimestr} Untitled Document.txt"
        path = os.path.join(self.desktop_path, filename)
        document.set_location(Gio.file_new_for_path(path))

    def maybe_rename(self, document):
        if not self.is_autonamed(document):
            return

        original_path = document.get_location().get_path()
        excerpt = self.excerpt(document)

        if not excerpt:
            return

        datetimestr = os.path.split(original_path)[1][: len("YYYY-MM-DD-HH-MM-SS")]
        filename = f"{datetimestr} {excerpt}.txt"
        new_path = os.path.join(self.desktop_path, filename)

        try:
            os.rename(original_path, new_path)
        except FileNotFoundError:
            pass

        document.set_location(Gio.file_new_for_path(new_path))

        if new_path != getattr(document, "autoname_plugin_last_renamed_to", None):
            notify(f"Renamed to: {filename}")

        document.autoname_plugin_last_renamed_to = new_path

    def maybe_delete(self, document):
        if not self.is_autonamed(document):
            return

        path = document.get_location().get_path()
        filename = os.path.split(path)[1]

        if not self.excerpt(document):
            try:
                os.remove(path)
                notify(f"Deleted: {filename}")
            except FileNotFoundError:
                pass

    def is_unnamed(self, document):
        if not document:
            return False

        return not document.get_location()

    def is_autonamed(self, document):
        if not document:
            return False

        if not document.get_location():
            return False

        return self.path_regex.match(document.get_location().get_path())

    def excerpt(self, document):
        if not document:
            return ""

        excerpt = document.get_text(
            document.get_start_iter(), document.get_iter_at_offset(10000), False
        )

        words = []
        for word in excerpt.split():
            safe_word = "".join([char for char in word if char.isalnum()])
            if safe_word:
                words.append(safe_word)

        return " ".join(words)[:200]


def notify(message):
    os.system(
        "notify-send -i gedit -u low 'Autoname plugin' '{message}'".format(
            message=message.replace("'", "'\\''")
        )
    )
