# Scripting Documentation

## Introduction

The BCSFE scripting system is a system that allows you to create your own
scripts to automate editing your save file without programming a python script
or by manually making changes using the cli.

The script files are written in yaml.

## Scripting

### Schema

Each file must have a schema-version key: `schema-version: 0` at the top of the
file. This is used to ensure that the file is compatible with the current
version of the scripting system.

### Package

The package key (e.g `package: bcsfe`) is used to specify the tool that the
script is for. This is used to ensure that the script is compatible with the
tool that you are using. At the moment, only bcsfe is supported but I might
expand this in the future.

### Input

Instead of hardcoding values into the script, you can use the "!input" value to
take input from the user. E.g:

```yaml
- actions:
    - edits:
        - catfood:
            amount: "!input"
            add: true
```

### Actions

The actions key is used to specify the actions that you want to perform on the
save file. It is a list of dictionaries. Available actions are:

#### Load Save

The `load-save` action is used to load a save file. This action must be before
any editing actions. There are many methods of loading a save file:

##### Adb Pull

This can be used to load a save file from a rooted android device. It takes a
country code and an optional device id. If the device id is not specified, it
will use the first device that it finds. E.g:

```yaml
- actions:
    - load-save:
        method: adb-pull
        cc: "en"
        device: "emulator-5554"
```

#### Print

The `print` action is used to print a message to the console. It takes a message
key which is the message to print. (You can use the `{ }` syntax to insert a
variable or function call into the message.) E.g:

```yaml
- actions:
    - print: "finished loading save {get_iq()}"
```

#### Edits

The `edits` action contains a list of edit actions. These are the actions that
actually edit the save file. There are many types of edit action:

##### Basic Items

These include `catfood` and `xp`. They take an amount key which is the amount to
be added or set. This adding or setting can be controlled with the `add` key
which is a boolean. If it is true, the amount will be added to the current
amount. If it is false, the amount will be set to the amount specified. E.g:

If the add key is not specified, it will default to false.

```yaml
- actions:
    - edits:
        - catfood:
            amount: 100
            add: true
        - xp:
            amount: "!input"
```

### Saving the Save File

The `save-save` action is used to save the save file. When saving the save file
you can specify a `managed-items` key:

#### Managed Items

The `managed-items` key is optional and is used to specify whether tracked items
should be uploaded the game servers. This reduces ban risk when editing in
catfood, rare tickets, platinum tickets and legend tickets. It is a dictionary
which contains the following keys:

- `upload`: A boolean which specifies whether the items should be uploaded.
- `print`: Whether to print the status of the upload to the console.
- `allow-iq-change`: If the upload fails, whether to allow the inquiry code to
  be changed. If this is false, the script will fail if the upload fails.

If the `managed-items` key is not specified, it will default to not uploading

#### Methods

There are many methods of saving a save file:

##### Adb Push

This can be used to save a save file to a rooted android device. It takes a
country code and an optional device id. If the device id is not specified, it
will use the first device that it finds. You can also specifiy to rerun the game
after saving. E.g:

```yaml
- actions:
    - save-save:
        method: adb-push
        cc: "jp"
        device: "emulator-5554"
        rerun: true
        managed-items:
            upload: true
            print: true
            allow-iq-change: true
```
