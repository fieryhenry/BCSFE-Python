# Battle Cats Save File Editor

A python save editor for the mobile game The Battle Cats that requires a rooted device/emulator.

It is sort of based on my [C# save editor](https://github.com/fieryhenry/Battle-Cats-Save-File-Editor) but it works in a completely different way and should be more reliable since it works in a similar way to how the game actually parses the save data. But the downside is that if there is one error/bug in the parser code, you can't edit anything and the program crashes.

Join the [discord server](https://discord.gg/DvmMgvn5ZB) if you want to suggest new features, report bugs or get help on how to use the editor (not a substitute for the latest tutorial video).

If you want to support me then consider gifting me some ko-fi here: https://ko-fi.com/fieryhenry

## Thanks to:

Lethal's editor for giving me inspiration to start the
project and it helped me work out how to patch the save data and edit
cf/xp: https://www.reddit.com/r/BattleCatsCheats/comments/djehhn/editoren/

Beeven and csehydrogen's open source code, which helped me figure out how to patch save data: [GitHub - beeven/battlecats](https://github.com/beeven/battlecats), [GitHub - csehydrogen/BattleCatsHacker](https://github.com/csehydrogen/BattleCatsHacker)

## How to use:

At the moment you will need either a rooted device or a rooted android emulator. I recommed LDPlayer, Nox, or MEmu. Bluestacks is also an option but is more difficult to root as it doesn't have a built in option. If you are using an emulator you can transfer your save data from your main device to it using the in-game transfer menu and then transfer back to your device after editing your save.

1. Install python (If you haven't already) https://www.python.org/downloads/

2. Enter the command: `python -m pip install -U battle-cats-save-editor` into cmd or another terminal to install the editor. If that doesn't work then use `py` instead of `python` in the command

3. Connect your rooted device to your pc or start up your emulator

4. Then enter the command: `python -m BCSFE_Python` to run the editor. If that doesn't work then use `py` instead of `python` in the command

5. Choose the option to `Get the save data from the game automatically using adb` and enter the game version that you are using.

6. If you get the `No device with an adb connection can be found, please connect one and try again.` error message then you haven't setup your adb correctly, so you may need to go into the settings in your emulator (If using one) and make sure adb is enabled.

7. If you get a parsing error, or nothing seems to happen then please join the [discord server]((https://discord.gg/DvmMgvn5ZB)) and report it to me directly or in #bug-reports

8. Then edit what you want. You can either enter the numbers asigned to each feature, or a word to search for a feature e.g entering catfood will run the Cat Food feature and entering cats will show you all the features that have cats in their name.

9. Your edits won't be saved automatically so you'll need to go into the `Save Management` option and choose one of the first 3 options. A shortcut for re-launching the game is to enter `(r` into the the editor.

If you want a video to follow instead then watch the tutorial video [here]() (WIP)

### How to fix "This save data is currently acitve elsewhere"

I don't really know how this error occurs because I've gotten it even with an untouched account after repeatedly `Save Data to Server` and then `Cancel Save Data Transfer` but anyway here's how to fix it:

1. Rename your current save to something like `SAVE_DATA_main` to keep track easily

2. Open the editor, select any save and then run the feature in `Save Management` to `Clear save data`

3. Open the game, select a langauge and accept all of the agreements.

4. Open the editor and get the save data using adb

5. Close the editor

6. Rename the new save data to `SAVE_DATA_new` to keep track easily

7. Open the editor and select the `SAVE_DATA_main` save file.

8. Go into the `Inquiry Code / Token` menu and run the feature to `Fix elsewhere error / Unban account` 

9. Select `SAVE_DATA_new`

10. Then go into `Save Management` and pick one of the first 3 options

11. Open the game and you should be able to play (You may need to press `Play` a few times)

12. I recommed you remove all cat food, rare tickets, platinum tickets, and legend tickets from your save file to avoid getting banned. Although it might not make a difference.

### How to unban an account

You can get banned for editing in any amount of cat food, rare tickets, platinum tickets  (not platinum shards), or legend tickets.

The way you fix it is the same method as the elsewhere fix, so just follow that.

To avoid getting banned in the future instead of hacking in cat food, just edit everything in that you can buy with cat food, e.g battle items, catamins, xp, leadership for energy, etc and just hack in the cats/upgrades you want instead of editing in rare tickets, platinum tickets or legend tickets.

### Why can't I upload save data to the game servers?

Since 10.4 the transfer system has been secured better, so it is much more difficult to do anything. The difference between downloading and uploading save data is that there is a signature (Nyanko-Signature) that is generated. (There are other things too such as authorization but you can get that by doing other different requests to the servers anyway). So until I know how that signature is generated root is still required.