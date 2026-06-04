# Localization

Small tutorial on how to localize the editor into a different language.

## Disclaimer

Please do not use machine or AI translated text, they will likely make mistakes, especially since
there is specific terminology unique to The Battle Cats and the save editor, and if you do not
know the language you will not be able to correct them. There are also many other ethical and legal
issues when using AI that I would like to avoid.

Thank you for understanding

## How To

1. Open the editor

2. Run the Edit config feature

3. Select the option to change language

4. Select the option to create a new locale

5. Enter the required data

6. Keep a record of the path it gives you e.g:

>>> Successfully created new locale at **/home/henry/.local/share/bcsfe/locales/de**

7. Open that folder in file explorer or something.

8. Edit metadata again if you want

9. Edit each of the .properties file, translating each value, try to keep the colors the same as
the original text. Anything in `{..}` should stay exactly how it is. Anything in `{{..}}` references
another key and so can be changed if you want. For more details see [here](https://codeberg.org/fieryhenry/ExampleEditorLocale/).

10. Once done restart the editor and check that it works, you should also see the details you specified
in the `metadata.json` file in the opening text

11. Enable the config option to display missing locale keys then restart the editor

12. If everything is correct you shouldn't see any missing keys (extra keys are fine).

13. Once done, you can either copy the files to `src/files/locales/<locale>` in a fork of the editor and submit a pull request
to the codeberg repo. Alternatively you can just zip your locale folder and send it to me or in
the #localization channel on discord. (or [matrix](https://matrix.to/#/@fieryhenry:matrix.battlecatsmodding.org))

14. Note that if you make changes to anything in `src/files/`, you will need to run the editor with
the `--force-migrate` flag to copy them to the correct folder
