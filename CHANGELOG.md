# Changelog

## [3.0.1] - 2025-08-04

### Fixed

- Installing the editor on certain platforms due to a dependency issue

## [3.0.0] - 2025-08-04

This is a full re-write of the editor, so many things were added, changed and fixed, and I didn't
really document the changes that well, so here's a summary:

### Added

- Game Data for es, it, de, th, fr locales and a way to change what repo to use for game data

- Better color and localization support

- Better adb usage

- Waydroid support

- More config options

- Lucky tickets

- Treasure Chests

- Support for new talent orbs

- Ultra Form Support

- Better save backups

_ More support for older game versions

- Labyrinth medals

- Many more things

### Changed

- Improved the wording on a few features

- Cats will be auto-unlocked by default when upgrading / true forming, etc

- Many more things

## [2.7.2.3] - 2023-06-19

### Fixed

- New version of colored crashing the editor by forcing the editor to use the
old version (new colored version renamed stuff and also raises an exception when
not using a specific set of colors)

- Max value for equip slots being too high, for some reason ponos has allocated
space for 18 equip slots but has only allocated space for 17 slot names

## [2.7.2.2] - 2023-06-08

### Fixed

- The editor crashing when editing meow medals or event stages

## [2.7.2.1] - 2023-05-28

### Fixed

- The editor crashing if user info not found

## [2.7.2] - 2023-05-28

### Added

- Ultra Talent Support

- 12.2.0 cannon support

### Changed

- Improved item tracking and user info tracking so your inquiry code shouldn't
change as much

### Fixed

- Issues with the max values for some multi items

- Disable maxes config option not being checked

- Gold pass not being able to be removed

## [2.7.1] - 2023-03-22

### Added

- A feature to convert save versions e.g en to jp - might give issues and only
works if both apps are the same version

### Changed

- Base material names are no longer hardcoded and so jp base material names exist
now

- New cats no longer cause the cat capsule machine still thinking the cat is new

- Talent orbs editing works better now + aku orbs

### Fixed

- Things like treasures and gold pass id crashing the editor when entering too
large of a number

- Jp 12.2.0 save parsing

- The first mission not showing up in mission clearing

- Gatya seed not being able to set above the 32 signed int limit

- Outbreaks crashing

## [2.7.0] - 2023-01-08

### Added

- Features to clear legend quest, behemoth culling stages, and collab gauntlets

- Feature to get scheme item rewards (e.g go go pogo cat mission rewards)

- More support for rooted android devices (pull and push directly to root
folder + re-run game)

- The ability to remove talents

- The ability to select / download a new save without having to restart the editor

### Changed

- Catseye editing will now use the game data for names - means i don't need to
update the whole editor to put another catseye type in

- When uploading the managed items, a save key is added (idk if this changes
anything / reduces bans but newer game versions do this)

- The editor will never ask if you want to exit, to exit enter the option to exit
or do `ctrl+c`

- Renamed feature `Create a new account` to `Generate a new inquiry code and token`
to better reflect what it does

### Fixed

- Cat name selection for jp

- Evolve cats and upgrade cats crashing if game data is outdated

- Main story crashing and chapter names being offset sometimes

- Dojo score not being able to be edited if you haven't been to the dojo yet

- Max value for some items being an unsigned int even though the game reads
signed ints

- Outbreak clearing not setting all stages

- Jp timed score rewards being parsed and serialized incorrectly leading to
incorrect timed scores being edited in

### Removed

- The `pick` module due to issues with python 3.11

## [2.6.0] - 2022-10-24

### Added

- Editor support for android. Using termux you can now run and install the editor

- On crash, the editor will ask if you want to save your changes and upload
managed item changes to the servers

- A way to remove meow medals

- A feature to play the CotC 3 filibuster stage again

- A way to remove outbreaks

- A feature to unlock the aku realm

### Changed

- When upgrading cats, if you upgrade past the normal max for that cat then the
level cap of the cat will also increase / decrease to match. (E.g if you upgrade
a cat to level 35 using the editor, then use a catseye in game then it will
unlock level 36 instead of level 31)

- How selecting stages to clear works. Instead of selecting stage ids you enter
a stage to complete the progress to (e.g entering 5 clears the first 5 stages,
and entering 48 clears them all and then if you then enter 5 again it will clear
the level progress for the levels 6-48)

### Fixed

- Crash if using an older game version and getting cats by rarity / gatya id

- Talents crashing

- CotC 2 and 3 appearing in the outbreaks feature when they don't have outbreaks

- The editor crashing if you don't have an internet connection

## [2.5.0] - 2022-10-14

### Added

- A feature to fix time related issues (HGT, no energy recovery, etc)

### Changed

- Features that fix things (fix time related issues, fix gamatoto crashing the
game, fix equip menu not unlocked, etc) have been moved / copied to their own
category called `Fixes`

### Fixed

- Having a very high playtime not allowing you to transfer

- Having corrupted cat unlock flags messing up user rank calculation and not
letting you transfer

- Cat shrine not appearing when editing it

- Selecting cats from name not letting you select cats

- Transfer error messages not appearing in some cases

## [2.4.0] - 2022-10-05

### Added

- An option in save management to save the save data without opening the file
selection dialog

- Option to edit where the config file is located

- A way to enter an officer id or generate a random one when getting the gold
pass. Entering -1 for the officer id will remove the gold pass

### Changed

- Platinum shards max amounts now takes into account your current platinum ticket
amount to make sure you can't go over 9 tickets

- Made catshrine appear when using the edit catshrine level feature and the level
up dialogs are now skipped

- When pulling using adb the editor will automatically detect currently installed
game versions and let you select one to pull. If only 1 game version is installed
it will just default to that one.

### Fixed

- Selecting cats based on name crashing if entering a cat id too large

- Upgrade cats / special skills crashing the editor if setting the base level to
0 or a level to be larger than 65535

- Being unable to download a save / pull saves if your default country code is
longer than 2 characters. The editor will just ask you to manually enter it

- Treasure groups chapter selection ids being off by 1

## [2.3.0] - 2022-09-14

### Added

- Feature to add enigma stages

- Feature to edit Gamatoto shrine xp / level

- Replaced some unknown values in the save stats + updated parsing for 11.3.0
and up

### Changed

- Get gold pass will now give the paid version instead of the free trial and
each subsequent use of the feature will increase the total renewal times by 1
and wipe the daily catfood stamp count

### Fixed

- File not found error if item_tracker.json is not present

## [2.2.2] - 2022-09-04

### Added

- A new config option to select options with the arrow keys or j and k to select
some options. `EDITOR` -> `USE_ARROW_KEYS_FOR_FEATURE_SELECT`

### Fixed

- Default save path being empty, causing the editor to not be able to pull saves
unless changed

## [2.2.1] - 2022-09-04

### Fixed

- Editor sometimes crashing when saving a file when the file dialog

## [2.2.0] - 2022-09-03

### Added

- Option when selecting cats to only get obtainable cats (Only the cats that
show up in the cat guide)

- Option to select cats by name when selecting cats

### Changed

- Config file will now be located in the app data folder / home folder

- Character drop, evolve cats and talents will now be able to use the normal cat
selecting menu

- You can now select all chapters at once when editing treasure groups

### Fixed

- Wrong chapter being shown when selecting levels

- Editor crashing when entering the name of a category when selecting a feature

## [2.1.1] - 2022-08-17

### Changed

- Split up some features into subcategories e.g Treasures / Levels -> Treasures
-> Treasure groups. Or Items -> Tickets -> Normal Tickets

### Fixed

- Gamatoto helpers

## [2.1.0] - 2022-08-16

### Added

- The ability to unlock the equip menu

- The ability to upload catfood and other bannable item changes to the ponos
servers - this is done automatically whenever your save data is saved /
uploaded. This should in theory prevent bans from catfood and other items,
but it seems a bit unreliable so I've kept the warning in the editor

- A feature to claim all user rank rewards (Doesn't give any items)

- A way to select specific gacha banner cats - you need to go to the wiki for
the banner you want, and look at the name of the image e.g royal fest = 602

- The ability to get the gold pass

- A feature to create a new account - new iq and token

- A way to clear specific aku stages

- Some configuration options , e.g options to remove max limits, automatically
save changes after each edit, etc, the path to the config file is shown at the
top of the editor

### Changed

- You can now exit, catfood, rare, plat, and legend tickets after the warning is
shown

- The editor will now display "Press enter to exit" when exiting

- Whenever your inquiry code changes, the editor will upload your catfood and
other bannable item amounts to the servers - this should prevent bans

- When entering a transfer code, the editor will check for a hex number and when
entering a confirmation code it will check for a dec number. This should prevent
people confusing 0 for O

- Game data will now be downloaded from [here](https://github.com/fieryhenry/BCData)
when needed so that if I want to update the data in the editor, I don't have to
do a new release

### Fixed

- Select cats based on rarity being off by 1
- Evolve cats setting some cats to the first form

## [2.0.2] - 2022-07-08

### Fixed

- Jp not being able to upload save data

## [2.0.1] - 2022-07-04

### Fixed

- Upgrade cats and unlock event stages not working properly when editing all at once

## [2.0.0] - 2022-07-04

### Added

- The ability to upload your save data to the ponos servers and get transfer
and confirmation codes. (The editor's root requirement is now gone). Although,
you'll still need root access if you get banned / elsewhere popup. I haven't
tested the feature too much so it could lead to bans

- An option to go back in the feature menu

- An automatic updater, if there is a new update, it will ask if you want to
update and if you say yes then it'll try to update automatically

- A way to select `all` talent orbs to edit all at once

- A new tutorial video that shows you how to use the transfer system stuff and
unban an account [here](https://www.youtube.com/watch?v=Kr6VaLTXOSY)

### Changed

- The fix elsewhere / unban feature, it no longer needs another account.
You can still use the old one, now named `Old Fix elsewhere error / Unban
account (needs 2 save files)` if you want

- A bunch of the source code. You should now be able to import BCSFE_Python in
another python file and access the parser, serialiser, etc. Due to the rewrite,
some stuff may be broken. This, and testing, is where the majority of the time
went to

- The order of few options, to make the server stuff closer to the top as that's
what most people will be selecting now that no root is needed

### Fixed

- Some adb issues

- More save parsing issues

- Edit dojo score crashing if you haven't been to the dojo yet

- Adding adb to path issue

- Ototo cat cannon not setting the correct value when editing all at once

- Individual treasures feature giving you 49/48 treasures

## [1.8.0.1] - 2022-05-24

### Removed

- Import from a random module that got imported automatically by vscode

## [1.8.0] - 2022-05-24

### Added

- New behemoth stones to get catfruit feature
- The ability to fix gamatoto from crashing the game

### Fixed

- Some adb issues thanks to [!j0](https://github.com/j0912345)
- More save parsing issues

## [1.7.1] - 2022-05-20

### Fixed

- Save parsing issue with en 11.5

## [1.7.0] - 2022-05-20

### Added

- The ability to clear catnip challenges / missions
- The ability to complete cat cannons to certain stages (e.g foundation, style, cannon)
- The ability to set the Catclaw dojo score (only `Hall of Initiates` atm -
don't know if ranked stuff can be save edited)
- The ability to remove the `Clear "{stage_name}" for a chance to get the
Special unit {cat_name}` stage clear rewards when entering Legend Stages
- The ability to set the `maxed upgrades --> rare tickets` conversion thing to
allow for unbannable rare tickets to be generated. Run the `trade progress`
feature, enter the number of rare tickets you want, go into game and press
the `Use All` button in cat storage and then press `Trade for Ticket` .
There appears to be nothing in your storage because there is an unobtainable blue
upgrade / special skill between `power` and `range` and the editor adds that to
your storage to allow you to use the `trade` thing, although any other blue
upgrade also works, as long as it is max level.

### Fixed

- More save parsing issues

## [1.6.2] - 2022-05-03

### Fixed

- Upgrade cats and upgrade blue upgrades crashing the editor

## [1.6.1] - 2022-05-03

### Fixed

- Gauntlets from crashing the editor

## [1.6.0] - 2022-05-03

### Added

- The ability to edit specific treasures for each stage

- The ability to edit groups of treasures (e.g energy drink, aqua crystal)

### Fixed

- More save parsing issues
- Event stages crashing when selecting `all` for the stage ids

## [1.5.0] - 2022-04-28

### Added

- When exporting to json, the current editor version will be included and so if
json data from a different editor version is being imported a warning
message will show.

- Option to edit specific stages in a main story chapter

- Option to remove enemy guide entries

### Fixed

- More save parsing issues

- Meow medals not writing properly

- The enemy ids in `unlock/remove enemy guide entries` not being the same as the
ones on the wiki

## [1.4.8] - 2022-04-23

### Fixed

- More save parsing issues
- Event stages, uncanny, gauntlets not unlocking the next subchapter
- Outbreaks crashing the editor after being edited

## [1.4.7] - 2022-04-22

### Changed

- It seems like the adb included in the editor doesn't work, and so I've removed
it, you now need to have adb in your Path environment variable. Tutorial
in the help videos's description

## [1.4.6] - 2022-04-22

### Changed

- When the editor detects a new version, it will display where to see the changelog

### Fixed

- A small issue relating to meow medals

- Some more parsing errors

## [1.4.5] - 2022-04-22

### Changed

- `adb.exe` is now included in the project, so you should be able to auto-pull
and push saves without adding it to your `PATH`

### Fixed

- Catfruit crashing

## [1.4.4] - 2022-04-21

### Fixed

- Some saves getting an error when parsing

## [1.4.2 & 1.4.3] - 2022-04-21

### Fixed

- It should correctly auto-install required packages

## [1.4.1] - 2022-04-21

### Fixed

- It should auto-install required packages

## [1.4.0] - 2022-04-21

### Added

- Ability to unlock enemy guide

- Ability to clear cat guide rewards

### Changed

- Made clear tutorial also beat Korea

## [1.3.0] - 2022-04-21

### Added

- Ability to add, upgrade cats, and true form cats in a certain rarity category.
