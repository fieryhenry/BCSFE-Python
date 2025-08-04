# Battle Cats Save File Editor

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/fieryhenry)

[![LiberaPay](https://liberapay.com/assets/widgets/donate.svg)](https://liberapay.com/fieryhenry)

BCSFE is a python command line save editor for The Battle Cats.

Join the [discord server](https://discord.gg/DvmMgvn5ZB) if you want to suggest
new features, report bugs or get help on how to use the editor (please read the
below tutorials first before asking for help).

## Thanks to

Lethal's editor for giving me inspiration to start the project and it helped me
work out how to patch the save data and edit cf/xp: <https://www.reddit.com/r/BattleCatsCheats/comments/djehhn/editoren/>

Beeven and csehydrogen's free and open source code, which helped me figure out how to
patch save data: [beeven/battlecats](https://github.com/beeven/battlecats), [csehydrogen/BattleCatsHacker](https://github.com/csehydrogen/BattleCatsHacker)

Anyone who has supported my on [Ko-Fi](https://ko-fi.com/fieryhenry) or [LiberaPay](https://liberapay.com/fieryhenry)

Everyone who's given me saves, which helped to test save loading/saving and to
test/develop new features

### Localization

- HungJoesifer for Vietnamese localization

### Themes

- HungJoesifer for the `discord` inspired theme

## Installation

Note the following tutorials are for the device you wish to run the editor on, not the device
that you have the game installed on.

For example just because you have the game on an android device, does not mean you have to run
the editor on it. It is easier to run the editor on a PC / laptop rather than on a mobile device.

### Windows / MacOS

1. Install Python 3.9 or later if you don't already have it: <https://www.python.org/downloads/>

2. Open a terminal such as PowerShell or Command Prompt

3. Run the following command:

```powershell
py -m pip install bcsfe
```

4. If you get an error saying that `py` is not a recongnised command, then try:

```powershell
python -m pip install bcsfe
```

or

```powershell
python3 -m pip install bcsfe
```

5. If you get an error saying `No module named pip`, then run:

```powershell
py -m ensurepip --upgrade
```

Again change `py` for `python` or `python3` if needed

5. To run the editor, as long as Python is in your PATH, you should be able to run:

```powershell
bcsfe
```

6. If Python is not in your path you'll need to run:

```powershell
py -m bcsfe
```

Again change `py` for `python` or `python3` if needed.

If you are using Windows and you are still struggling, try watching this video [here](https://youtu.be/ypmT39jqZrg).

### Linux

1. Install Python 3.9 or later using your system's package manager if you don't already have it

2. You might have to install pip seperately with a package called `python-pip` or something similar
or you can run the following command:

```sh
python3 -m ensurepip --upgrade
```

3. Depending on your distro you might not be able to install the editor directly using the system
pip and you might need to use pipx (python-pipx) or create a virtual environment manually.

4. Using pipx:

```sh
pipx install bcsfe
```

5. If `~/.local/bin/` is in your path you should be able to run the editor with the command:

```sh
bcsfe
```

6. You may also need to install `tk` with your system package manager to open the
file selection dialog. This package may be called `tk` or `python-tk` or `python3-tk`.

If anyone wants to put the editor on the AUR or another package repo, feel free, I'll be happy to
help if needed.

### Android

You need to install a terminal emulator to be able to install and run Python packages.

[Termux](https://termux.dev/en/) is a good option and is what this tutorial will use.

1. Download Termux, you can either get it from [F-Droid](https://f-droid.org/), or the APK directly
from [GitHub](https://github.com/termux/termux-app?tab=readme-ov-file#github). DO NOT use the
Google Play Store version, as it does not fully work.

I recommend using F-Droid since it can update Termux for you (and it's just a better alternative
than using the Google Play Store).

On F-Droid Termux is called `Termux Terminal emulator with packages`

2. Once Termux is installed, open it and run the following commands:

```sh
termux-setup-storage
termux-change-repo
pkg update
pkg upgrade
pkg install python python-pip
```

When it asks for a mirror, it doesn't really matter which one you pick, the default single mirror
works fine.

3. Install the editor with the following command:

```sh
pip install bcsfe
```

Or if that doesn't work try:

```sh
python -m pip install bcsfe
```

4. Run the editor with the following command:

```sh
bcsfe
```

Or if that doesn't work try:

```sh
python -m bcsfe
```

Note that the editor might give you warnings about tkinter not being installed, you can just
ignore those as tkinter will not work on mobile. This just means that instead of a graphical file
selection dialog, you just have to type the file path manually.

For example to save your save file to your downloads directory, the path might look something like
`/storage/emulated/0/Download/SAVE_DATA` or `/sdcard/Download/SAVE_DATA`


### iOS

I do not have an iOS device, so there is no text tutorial, but Viarules has made a video
tutorial [here](https://www.youtube.com/watch?v=xw-uOqQRYJ8). The video uses iSH which is
apparently quite slow, and other people recommend using a-Shell instead.


## Terms of Use

By using the editor you agree to the following:

If you are using the editor to run a paid service that profits off of the editor
(e.g a service to provide people with hacked accounts, or a paid discord bot to edit people's accounts,
etc) you must make it very clear that you are using this save editor.

This should be done by linking this GitHub page, and explicitly stating that the tool you are
using is available for free and that they don't need to use your service to hack their account.

This information needs to be visible and something the customer agrees to **before** any payment is made.

This also includes paid services which claim to teach people "How To Hack The Battle Cats". In those
cases, this still applies, so you still need to state and have the customer acknowledge the things
I said above.

Free services / derivative works (such as a third party discord bot or editor gui) are fine to use
the editor under the hood as long as you abide by the [License](#license). Basically if you are
distributing a program which uses the editor, you need to license your own program under the GPL
or a compatible license (basically make it open source / free software too).

These terms are designed to prevent scams and the exploitation of users.

Also if you **are** profiting from the editor, it would be greatly appreciated if you could
give back something and support me.

## Usage

Once you have installed and ran the editor, you can now begin to edit your save file!

1. In `The Battle Cats` enter the `Change Account / Device` menu in the `Settings` on the main menu.

2. Then enter the `Begin Data Transfer` menu.

3. Then click / tap `Save Data to Server`, this should give you a transfer code and a confirmation
code.

4. In the editor use the option called `Download save file using transfer and
confirmation code` by entering the number `1`

5. Enter your transfer code

6. Enter your confirmation code

7. Select the country code that you are using, `en`=english,
`kr`=korean, `jp`=japanese, `tw`=taiwanese.

Note that `en` also includes the `it`, `es`, `fr`, `th`, and `de` translations.

8. Edit what you want. Note that in most cases, if you want to exit the current
   input you can enter `q` and press enter to go back to the previous menu

9. In the editor, go into the `Save Management` category and select `Save changes and upload to
game servers (get transfer and confirmation codes)`. It may take some time, it
may also fail, if it does then try again.

10. This should give you a new transfer code and a new confirmation code.

11. Back in-game, tap the `Close Game` button, then tap `Cancel Data Transfer` (and also possibly
`Start Game From Beginning`)

12. Go back into the `Change Account / Device` menu and then go into the `Resume Data Transfer`
menu

13. Enter the new codes, and tap `Resume Transfer`

14. Then done! You should see your edits in-game.

15. Every time that you want to make an edit to your save, you will have to re-upload it to the
game servers in the editor and re-download it in-game, the saves aren't automatically linked together.

Apparently doing the Google Account / Apple Account link limits the number of data transfers you can
do within a certain time. So to be safe, I would avoid linking your account.

### Using a rooted device via adb

1. Add adb to your PATH environment variable, or edit the config to set ADB path editor config option
  to the full path of the adb executable. You can download adb from
  [platform-tools](https://developer.android.com/studio/releases/platform-tools)

1. Open the editor and select the option named `Pull save file from device
using adb` and enter your game version, or select the option named
`Select save file from file` and select a copy of your save data

1. Edit what you want

1. Go into save management and select an option to push save data to the game

1. Enter the game and you should see changes

### Using a rooted device directly

1. You need to be running the editor on the device itself, so you'll need to
follow the [Android tutorial](#android) to install the editor

1. You may have to run the editor with `sudo python -m bcsfe` or something, so you might have to
setup the termux root repo and run `pkg install sudo`

1. In the editor select the option named `Pull save file from root storage`

1. Edit what you want

1. Go into save management and select an option to push save data to the game

1. Enter the game and you should see changes


### How to unban your account

1. Select the option in `Account` to `Unban account` or
just upload the save data to the game servers again

1. It may take some time but after, you should be able to choose one of the
options in save management to push the save data to the game.

#### How to prevent a ban in the future

- Instead of editing in platinum tickets use the `Platinum Shards` feature

- Instead of editing in rare tickets use the `Normal Ticket Max Trade Progress
(allows for unbannable rare tickets)` feature

- Instead of hacking in cat food, just edit everything in that you can buy with
cat food, e.g battle items, catamins, xp, energy refills (leaderships), etc.
If you really want catfood then you can clear and unclear catnip missions with
the feature `Catnip Challenges / Missions` then entering 1 when asked.
You'll need to collect the catfood in-game after each clear though

- Instead of hacking in tickets, just hack in the cats/upgrades you want directly

### Install from source

If you want the latest features then you can install the editor from the github.

1. Download [Git](https://git-scm.com/downloads)

2. Run the following commands: (You may have to replace `py` with `python` or `python3`)

```sh
git clone https://github.com/fieryhenry/BCSFE-Python.git
cd BCSFE-Python
py -m pip install -e .
py -m bcsfe
```

Then if you want the latest changes you only need to run `git pull` in the downloaded
`BCSFE-Python` folder. (use `cd` to change the folder)

Alternatively you can use pip directly, although it won't auto-update with the latest
git commits.

```sh
py -m pip install git+https://github.com/fieryhenry/BCSFE-Python.git
py -m bcsfe
```

If you want to use the editor again all you need to do is run the `py -m bcsfe` command

## Documentation

- [Custom Editor Locales](https://github.com/fieryhenry/ExampleEditorLocale)
- [Custom Editor Themes](https://github.com/fieryhenry/ExampleEditorTheme)

I only have documentation for the locales and themes atm, but I will probably
add more documentation in the future.

## Contributing

If you want to contribute to the BCSFE, I recommend joining the [Discord Server](https://discord.gg/DvmMgvn5ZB) and starting a
discussion in #dev-chat, or create an issue in this repo, or a draft pull request.

If you need help with reverse engineering the save file, I have a basic starting guide here:
<https://codeberg.org/fieryhenry/bc_ree>.

## License

BCSFE is licensed under the GNU GPLv3 which can be read [here](https://www.gnu.org/licenses/gpl-3.0.en.html).
