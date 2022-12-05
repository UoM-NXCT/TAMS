Usage
=====

Actions
-------

Actions can be triggered from the window menu, from the toolbar, or by using a keyboard
shortcut.

Settings
^^^^^^^^

The settings action allows you to configure this software. Triggering the action will
open the settings dialogue.

Reload
^^^^^^

Sometimes the database will be updated (for example, by the user or another program).
The table will not be updated automatically. You can trigger the reload action to update
the table.

Download
^^^^^^^^

The download action will download scans based on the table selection. If a scan is
selected, only that scan will be downloaded. If a project is selected, all scans of that
project will be downloaded.

If the scan has not already been downloaded, a new directory will be created. If data
already exists, the proces will download the missing data skipping the existing data.

Only the raw data and the metadata will be downloaded.

Upload
^^^^^^

The upload action will upload scans based on the table selection. If a scan is selected,
only that scan will be uploaded. If a project is selected, all scans of that project will
be uploaded.

If the scan has not already been uploaded, a new directory will be created on the
server. If data already exists, the process will upload the missing data skipping the
existing data.

Only the raw data and the metadata will be uploaded (meaning reconstruction data will
not be uploaded).

Open
^^^^

The open action opens a directory corresponding to the current selection (for example,
a project or scan). The action will open the local directory and wil raise an exception
if the local directory does not exist (for example, if it has not been downloaded).

To open a directory:

1. Select a project or scan in the table
2. Click the Open button in the toolbar or file menu, or double click the selection

Validate scan
^^^^^^^^^^^^^

It is important to validate scan data after saving it. This is to make sure that the
data was not corrupted and is identical to the original data.

This program will check the raw data and metadata directory. It will not check other
directories such as the processed data directory. This is because the raw data and
metadata directory are the only directories that are copied to the archive and are
expected to be identical to the original data. The processed data directory is not
saved to the archive and is expected to be different from the original data.

Click validate to validate the scan data. This process is slow.

If the data is invalid, you will see a message saying that the data is invalid.

How does validation work?
"""""""""""""""""""""""""

There are two stages to validation.

1. A shallow check: this checks the file metadata. If they are the same same, the check
   passes.

2. A deep check: this checks the file contents. This is done by comparing the hash of
   the file contents, using the SHA3-348 algorithm.

The deep check is only done if the shallow check passes. This is to save time.

These validation checks are picky. For this reason, users should not modify the data in
the raw data and metadata directories. If you do, the validation will fail. If you
wish to modify the raw data (for example, to process it), you should copy the data to
(for example) a processed data directory.

Full screen
^^^^^^^^^^^

The full screen action will toggle full screen mode.

Documentation
^^^^^^^^^^^^^

The documentation action will open the documentation in a web browser. You are reading
the documentation right now.

About
^^^^^

The about action will show the about dialogue.