# Localization

Small tutorial on how to localize the editor into a different language.

## Disclaimer

Please do not use machine or AI translated text, they will likely make mistakes, especially since
there is specific terminology unique to The Battle Cats and the save editor, and if you do not
know the language you will not be able to correct them. There are also many other ethical and legal
issues when using AI that I would like to avoid.

Thank you for understanding

## How To

0. If you want to submit a pull request later you should fork the editor (make sure to fork the codeberg repo: <https://codeberg.org/fieryhenry/BCSFE-Python>)

1. Install the editor from source by following [these instructions](https://codeberg.org/fieryhenry/BCSFE-Python#install-from-source)
  (make sure to change the git clone url to be your fork if you have one)

2. Inside the `src/bcsfe/files/locales/` folder you will find the pre-existing locales, copy the
  one named `en` and rename it to the code of the language you are translating to

3. Create a file called `metadata.json` inside the folder and edit it to contain the following info:

```json
{
  "authors": ["author-1", "author2", "cool-person3"],
  "name": "Name of language (english name of language)"
}
```

For example the one for Vietnamese looks like this:

```json
{
  "authors": ["HungJoesifer"],
  "name": "Tiếng Việt (Vietnamese)"
}
````

4. Edit each of the .properties file, translating each value, try to keep the colors the same as
the original text. Anything in `{..}` should stay exactly how it is. Anything in `{{..}}` references
another key and so can be changed if you want. For more details see [here](https://codeberg.org/fieryhenry/ExampleEditorLocale/).

5. Once you think you have finished, open the editor and edit the config value `Language` and
select your language from the list

6. Restart the editor and check that it works, you should also see the details you specified
in the `metadata.json` file in the opening text

7. Enable the config option to display missing locale keys then restart the editor

8. If everything is correct you shouldn't see any missing keys (extra keys are fine).

9. Once done, push your changes to your fork if you have one and feel free to submit a pull request
to the codeberg repo. Alternatively you can just zip your locale folder and send it to me or in
the #localization channel on discord. (or [matrix](https://matrix.to/#/@fieryhenry:matrix.fyhenry.uk>))
