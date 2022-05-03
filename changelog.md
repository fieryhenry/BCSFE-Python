# Changelog

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

- A small issue releating to meow medals

- Some more parsing errors

## [1.4.5] - 2022-04-22

#### Changed

- `adb.exe` is now included in the project, so you sould be able to auto-pull and push saves without adding it to your `PATH`

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
