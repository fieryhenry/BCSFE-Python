# Battle Cats Save File Editor

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/M4M53M4MN)

A python save editor for the mobile game The Battle Cats

Join the [discord server](https://discord.gg/DvmMgvn5ZB) if you want to suggest new features, report bugs or get help on how to use the editor (please read the below tutorials / watch the latest [tutorial video](https://www.youtube.com/watch?v=Kr6VaLTXOSY) first before asking for help).

## Thanks to

Lethal's editor for giving me inspiration to start the project and it helped me work out how to patch the save data and edit cf/xp: <https://www.reddit.com/r/BattleCatsCheats/comments/djehhn/editoren/>

Beeven and csehydrogen's open source code, which helped me figure out how to patch save data: [beeven/battlecats](https://github.com/beeven/battlecats), [csehydrogen/BattleCatsHacker](https://github.com/csehydrogen/BattleCatsHacker)

Everyone who's given me saves, which helped to test save parsing/serialising and to test/develop new features

## How to use

If you have a pc: watch a [Tutorial video](https://www.youtube.com/watch?v=Kr6VaLTXOSY), or scroll down for a text tutorial

If you only have an android device: read the [Android text tutorial](https://github.com/fieryhenry/BCSFE-Python#android-tutorial)

If you only have an ios device: watch the [IOS tutorial video](https://www.youtube.com/watch?v=xw-uOqQRYJ8) (Made by Viarules, NOTE: Some people have said that ish is really slow, and you should use a-shell instead)

## Main tutorial

You no longer need a rooted device nor a rooted android emulator.

Although if you want to get unbanned / fix the elsewhere error you will still need one. I recommend LDPlayer, Nox, or MEmu if needed. Bluestacks is also an option but is more difficult to root as it doesn't have a built in option.

---

1. Install python (You'll need version 3.9 and up) <https://www.python.org/downloads/>

2. Enter the command: `py -m pip install -U battle-cats-save-editor` into command prompt or another terminal to install the editor (**NOT the Windows Python app**). If that doesn't work then use `python3` or `python` instead of `py` in the command

3. Enter the command: `py -m BCSFE_Python` to run the editor. If that doesn't work then use `python3` or `python` instead of `py` in the command

4. Look below for the tutorial that you need, or watch [here](https://www.youtube.com/watch?v=Kr6VaLTXOSY) for a video

#### Using Transfer Codes

If you don't have a rooted device or an emulator setup then do this:

5. Go into the game and look in the top right of the screen and record / remember the game version

6. Go into the in-game transfer system in `Settings-> Data Transfer` and click `Begin Data Transfer`

7. In the editor use the option called `Download save data from the game using transfer and confirmation codes` (enter the corresponding number, not the name itself)

8. Enter the game version that you are using, `en`=english, `kr`=korean, `ja`=japanese, `tw`=taiwan.

9. Enter your transfer code

10. Enter your confirmation code

11. Enter the game version that you recorded earlier in step 5. If you entered everything in correctly it should work and you should be able to select a place to put the save

12. If you get a parsing error please join the [discord server](https://discord.gg/DvmMgvn5ZB) and report it in #bug-reports and / or dm me your save file (preferably <b>not</b> transfer codes)

13. Edit what you want

14. Go into the `Save Management` option and select `Save changes and upload to game servers (get transfer and confirmation codes)`. It may take some time

15. Enter those codes into the game's transfer system (click on `Resume Data Transfer`) (You may need to `Cancel Data Transfer` in-game before doing so)

16. If you press play you may get a `The current Save Data is in violation` message, if so press ok and try again and it should go away, if it doesn't look at the tutorial below

#### Using a rooted device

If you can't upload your save data using the in-game system because your are banned or the `This save data is currently active elsewhere` message appears, you will need direct access to the save data:

If you don't have a rooted device:

5. You will need to get one of the emulators listed earlier, I recommend LD Player because I know that it works with this method. If you change the default install location, make sure to keep a note of it for it later

   1. Enable `root permission` in the settings and under `ADB Debugging` select `Open local connection`. You will need to restart LD Player for the changes to work

   2. Open the editor and select the option named `Use adb to pull the save from a rooted device` and enter your game version

6. If you get the option to add adb to your path, select enter `y`.

7. The editor will look for adb in default install directories of common emulators and add it automatically

8. If it fails, then you will need to either

   1. Enter the path to your emulator's install directory, it might look like `C:\LDPlayer\LDPlayer4.0`

   2. Download adb with from [here](https://dl.google.com/android/repository/platform-tools-latest-windows.zip). Extract the zip and copy the folder path (not adb.exe itself) into the editor

9. Now rerun the editor and try the option again. If it still doesn't work you'll need to manually do it, using the tutorial below.

10. If you get a parsing issue please join the [discord server](https://discord.gg/DvmMgvn5ZB) and report it in #bug-reports and / or dm me your save file (preferably not transfer codes)

11. Edit what you want

12. Go into save management and select an option to push save data to the game

13. Enter the game and you should see changes

### Put adb in path

To use the options in the editor to get and push your save data to the game, you will need to have adb in your path system environment variable. The editor will try to do this automatically, but it may not work. So do this if it doesn't (If you're not using windows look up how to do this):

1. If you are using an emulator: Go to your emulator's install directory, if you're
   using LDPlayer it will most likely be in `C:/LDPlayer/LDPlayer4.0`.
   Then find `adb` in that folder (other emulators might have it in the `bin` directory)

2. If you aren't using an emulator [Download the Android SDK Platform Tools ZIP file for Windows](https://dl.google.com/android/repository/platform-tools-latest-windows.zip), and unzip it.

3. Copy the path to the folder that you are in (not adb.exe itself)

4. Then open the windows start menu and search: `edit the system environment variables` and press enter.

5. Then click on the `Environment Variables` button.

6. Then in the `System variables` box find the variable named `Path`, then
   click on the `edit` button.

7. Then click `New` and paste the path into it.

8. Click `Ok` then `Ok` again then `Ok` again.

9. Relaunch powershell and maybe restart your whole pc, and try the command
   again.

If this method is too difficult, just use a root file explorer instead
    and manually get the files that you want. The path that you will need is: `/data/data/jp.co.ponos.battlecatsen/files/SAVE_DATA`

### How to fix "This save data is currently active elsewhere" or "The current Save Data is in violation"

1. You will need to get access to save data so you will need a rooted device / emulator, so look at the first part of the `Using a rooted device` tutorial.

2. Select the option in `Inquiry Code / Token` to `Fix elsewhere error / Unban account`

3. It may take some time but after, you should be able to choose one of the options in save management to push the save data to the game.

4. If you press play you may get a `The current Save Data is in violation` message, if so press ok and try again and it should go away, if it doesn't then either you've done something wrong or the process didn't work. You may need to follow the tutorial in the second part of the old help video [here](https://www.youtube.com/watch?v=xBnGR1A3A-U) (3:40) and use the `Old Fix elsewhere error / Unban account (needs 2 save files)` feature instead

### How to unban an account

You can get banned for editing in any amount of cat food, rare tickets, platinum tickets or legend tickets.

The way you fix it is the same method as the elsewhere fix, so just follow that.

##### How to prevent a ban in the future

- Instead of editing in platinum tickets use the `Platinum Shards` feature

- Instead of editing in rare tickets use the `Normal Ticket Max Trade Progress (allows for unbannable rare tickets)` feature

- Instead of hacking in cat food, just edit everything in that you can buy with cat food, e.g battle items, catamins, xp, energy refills (leaderships), etc. If you really want catfood then you can clear and unclear catnip missions with the feature `Catnip Challenges / Missions` then entering 1 when asked. You'll need to collect the catfood in-game after each clear though

- Instead of hacking in tickets, just hack in the cats/upgrades you want directly

## Android Tutorial

If you don't have a pc to install and run the editor you can use Termux.

1. Download [F-Droid](https://f-droid.org/F-Droid.apk) - You can download the Termux apk directly but then it won't automatically update

2. Install F-Droid

3. Open it and wait for it to finish `Updating repositories`

4. Tap the green search button in the bottom right and search for `Termux`

5. Tap `Termux Terminal emulator with packages`

6. Tap `INSTALL` and then `OPEN` once installed

7. Once opened enter the command `pkg install python`

8. If that doesn't work then read this: <https://stackoverflow.com/a/71097459>

9. Then run `python -m pip install -U battle-cats-save-editor`

10. If that doesn't work then run `pkg upgrade` and try again

11. Then run `python -m BCSFE_Python`

12. You can then use the editor like normal (If asked to enter the path to a save file, then just enter `SAVE_DATA`)

### Install from source

If you want the latest features and don't mind bugs then you can install the editor from the github.

1. Download [Git](https://git-scm.com/downloads)

2. Run the following commands: (You may have to replace `py` with `python` or `python3`)

```batch
git clone https://github.com/fieryhenry/BCSFE-Python.git
py -m pip install -e BCSFE-Python/
py -m BCSFE_Python
```

If you want to use the editor again all you need to do is run the `py -m BCSFE_Python` command

Then if you want the latest changes you only need to run `git pull` in the downloaded `BCSFE-Python` folder. (use `cd` to change the folder)
