# Changelog

## [2.0.1] - 2022-07-04

#### Fixed

- Upgrade cats and unlock event stages not working properly when editing all at once

## [2.0.0] - 2022-07-04

#### Added

- The ability to upload your save data to the ponos servers and get transfer and confirmation codes. (The editor's root requirement is now gone). Although, you'll still need root access if you get banned / elsewhere popup. I haven't tested the feature too much so it could lead to bans

- An option to go back in the feature menu

- An automatic updater, if there is a new update, it will ask if you want to update and if you say yes then it'll try to update automatically

- A way to select `all` talent orbs to edit all at once

- A new tutorial video that shows you how to use the transfer system stuff and unban an account [here](https://www.youtube.com/watch?v=Kr6VaLTXOSY)

#### Changed

- The fix elsewhere / unban feature, it no longer needs another account. You can still use the old one, now named `Old Fix elsewhere error / Unban account (needs 2 save files)` if you want

- A bunch of the source code. You should now be able to import BCSFE_Python in another python file and access the parser, serialiser, etc. Due to the rewrite, some stuff may be broken. This, and testing, is where the majority of the time went to

- The order of few options, to make the server stuff closer to the top as that's what most people will be selecting now that no root is needed

#### Fixed

- Some adb issues

- More save parsing issues

- Edit dojo score crashing if you haven't been to the dojo yet

- Adding adb to path issue

- Ototo cat cannon not setting the correct value when editing all at once

- Individual treasures feature giving you 49/48 treasures

## [1.8.0.1] - 2022-05-24

#### Removed

- Import from a random module that got imported automatically by vscode

## [1.8.0] - 2022-05-24

#### Added

- New behemoth stones to get catfruit feature
- The ability to fix gamatoto from crashing the game

#### Fixed

- Some adb issues thanks to [!j0](https://github.com/j0912345)
- More save parsing issues

## [1.7.1] - 2022-05-20

#### Fixed

- Save parsing issue with en 11.5

## [1.7.0] - 2022-05-20

#### Added

- The ability to clear catnip challenges / missions
- The ability to complete cat cannons to certain stages (e.g foundation, style, cannon)
- The ability to set the Catclaw dojo score (only `Hall of Initiates` atm - don't know if ranked stuff can be save edited)
- The ability to remove the `Clear "{stage_name}" for a chance to get the Special unit {cat_name}` stage clear rewards when entering Legend Stages
- The ability to set the `maxed upgrades --> rare tickets` conversion thing to allow for unbannable rare tickets to be generated. Run the `trade progress` feature, enter the number of rare tickets you want, go into game and press the `Use All` button in cat storage and then press `Trade for Ticket` . There appears to be nothing in your storage because there is an unobtainable blue upgrade / special skill between `power` and `range` and the editor adds that to your storage to allow you to use the `trade` thing, although any other blue upgrade also works, as long as it is max level.               

#### Fixed

- More save parsing issues

## [1.6.2] - 2022-05-03

#### Fixed

- Upgrade cats and upgrade blue upgrades crashing the editor

## [1.6.1] - 2022-05-03

#### Fixed

- Gauntlets from crashing the editor

## [1.6.0] - 2022-05-03

#### Added

- The ability to edit specific treasures for each stage

- The ability to edit groups of treasures (e.g energy drink, aqua crystal)

#### Fixed

- More save parsing issues
- Event stages crashing when selecting `all` for the stage ids

## [1.5.0] - 2022-04-28

#### Added

- When exporting to json, the current editor version will be included and so if json data from a different editor version is being imported a warning message will show.

- Option to edit specific stages in a main story chapter

- Option to remove enemy guide entries

#### Fixed

- More save parsing issues

- Meow medals not writing properly

- The enemy ids in `unlock/remove enemy guide entries` not being the same as the ones on the wiki

## [1.4.8] - 2022-04-23

#### Fixed

- More save parsing issues
- Event stages, uncanny, gauntlets not unlocking the next subchapter
- Outbreaks crashing the editor after being edited

## [1.4.7] - 2022-04-22

#### Changed

- It seems like the adb included in the editor doesn't work, and so I've removed it, you now need to have adb in your Path environment variable. Tutorial in the help videos's description

## [1.4.6] - 2022-04-22

#### Changed

- When the editor detects a new version, it will display where to see the changelog

#### Fixed

- A small issue relating to meow medals

- Some more parsing errors

## [1.4.5] - 2022-04-22

#### Changed

- `adb.exe` is now included in the project, so you should be able to auto-pull and push saves without adding it to your `PATH`

#### Fixed

- Catfruit crashing

## [1.4.4] - 2022-04-21

#### Fixed

- Some saves getting an error when parsing

## [1.4.2 & 1.4.3] - 2022-04-21

#### Fixed

- It should correctly auto-install required packages

## [1.4.1] - 2022-04-21

#### Fixed

- It should auto-install required packages

## [1.4.0] - 2022-04-21

#### Added

- Ability to unlock enemy guide

- Ability to clear cat guide rewards

#### Changed

- Made clear tutorial also beat Korea

## [1.3.0] - 2022-04-21

#### Added

- Ability to add, upgrade cats, and true form cats in a certain rarity category.
