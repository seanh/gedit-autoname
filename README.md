gedit-autoname
=============

Replace Gedit's "Untitled Document 1" with automatically generated filenames.

* When you open a new window or tab it'll open a file named
  name `~/Desktop/YYYY-MM-DD-HH-MM-SS Untitled Document.txt`,
  instead of the default behavior of opening an unnamed file and requiring you
  to pick a file name when you try to save it.

  You won't be asked for a filename when you save the file, it'll just save it to
  `~/Desktop/YYYY-MM-DD-HH-MM-SS Untitled Document.txt`.

  You can still use <kbd>Save As…</kbd> if you want to rename the file yourself.

* Gedit's **autosaving** will be working immediately as soon as you open a new
  window or tab, so you'll never be at risk of losing any work (normally it
  doesn't start autosaving an untitled document until you've saved it once
  manually, and chosen a filename).

  (You have to enable autosaving under <kbd>Preferences</kbd> → <kbd>Editor</kbd> → <kbd>File Saving</kbd>.)

* When you save a file it will be **renamed based on an excerpt of the contents** of the file.

  You end up with filenames like `~/Desktop/YYYY-MM-DD-HH-MM-SS My Pancake Recipe.txt`,
  so you can tell what the contents of each file are from the filename.

* If the file is empty when you save it, **the file will be deleted**.

  So you don't end up with empty `~/Desktop/YYYY-MM-DD-HH-MM-SS Untitled Document.txt`
  files lying around.

  You can also cause it to delete a file by opening it, deleting all its
  contents, and saving.

* It will only rename and delete files that match the
  `~/Desktop/YYYY-MM-DD-HH-MM-SS *.txt` pattern, so it won't touch files you've
  named yourself.


Installation
------------

```shellsession
mkdir -p ~/.local/share/gedit/plugins
git clone https://github.com/seanh/gedit-autoname.git ~/.local/share/gedit/plugins/gedit-autoname
```

Then in gedit go to <kbd>Preferences<kbd> → <kbd>Plugins</kbd> and enable the **Autoname** plugin.


TODO
----

- [ ] When creating a `~/Desktop/YYYY-MM-DD-HH-MM-SS Untitled Document.txt`
  file it should check whether the file already exists and append ` 1`, ` 2`
  etc to the filename as necessary.

- [ ] The directory where new files are created (`~/Desktop`) should be configurable.
