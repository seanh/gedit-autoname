import datetime, os, re, unicodedata

from gi.repository import GObject, Gedit, Gio


__all__ = ["AutonamePlugin"]


class AutonamePlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "AutonamePlugin"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.desktop_path = os.path.expanduser("~/Desktop/")
        self.path_regex = re.compile("^" + self.desktop_path + r".* \d{14}\.txt$")

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

    def tab_added(self, window, tab):
        self.maybe_set_name(tab.get_document())

    def active_tab_state_changed(self, window):
        self.maybe_rename(window.get_active_tab().get_document())

    def tab_removed(self, window, tab):
        self.maybe_delete(tab.get_document())

    def maybe_set_name(self, document):
        if not document.is_untitled():
            return

        datetimestr = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"Untitled {datetimestr}.txt"
        path = os.path.join(self.desktop_path, filename)
        document.get_file().set_location(Gio.file_new_for_path(path))

    def maybe_rename(self, document):
        if not self.is_autonamed(document):
            return

        original_path = document.get_file().get_location().get_path()
        title = self.title(document)

        if not title:
            return

        datetimestr = os.path.splitext(original_path)[0][-len("YYYYMMDDHHMMSS") :]
        filename = f"{title} {datetimestr}.txt"
        new_path = os.path.join(self.desktop_path, filename)

        try:
            os.rename(original_path, new_path)
        except FileNotFoundError:
            pass

        document.get_file().set_location(Gio.file_new_for_path(new_path))

        document.autoname_plugin_last_renamed_to = new_path

    def maybe_delete(self, document):
        if not self.is_autonamed(document):
            return

        path = document.get_file().get_location().get_path()
        filename = os.path.split(path)[1]

        if not self.title(document):
            try:
                os.remove(path)
            except FileNotFoundError:
                pass

    def is_autonamed(self, document):
        if not document:
            return False

        location = document.get_file().get_location()

        if not location:
            return False

        return self.path_regex.match(location.get_path())

    def title(self, document):
        if not document:
            return None

        text = document.get_text(
            document.get_start_iter(), document.get_iter_at_offset(1000), False
        )

        lines = text.split("\n")

        for line in lines:
            slugified_line = slugify(line)[:80]
            if not slugified_line:
                continue
            return slugified_line

        return None


def slugify(value):
    """
    Convert a string ``value`` into a filename-friendly ASCII string.

    Based on Django's slugify() utility, but modified to allow capital letters,
    to use spaces instead of -'s, and to remove the option to allow unicode
    characters.

    https://docs.djangoproject.com/en/2.2/ref/utils/#django.utils.text.slugify
    """
    value = str(value)
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    value = re.sub(r"[^\w\s-]", "", value).strip()
    return re.sub(r"[-\s]+", " ", value)
