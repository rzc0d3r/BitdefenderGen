# MBCI (Menu-based Сonsole Interface)

### If you start the project without specifying arguments it will start in MBCI mode. In this mode you can interact with the startup settings

---

## The first thing that greets you is the Main Menu, which currently has 3 items:

![](../img/main_menu.png)

1. **Settings** - this is under the startup settings menu
2. **Do it, damn it!** - launches the program 
3. **Exit** - obviously closes the program

> To select the desired item, enter its number from the list after and press Enter.

> The default setting is ```--chrome --email-api developermail``` so that when you start the program you can immediately select **Do it, damn it!** and you will generate your Bitdefener account through the chrome browser

---

## Description of the Settings menu:

![](../img/default_settings_menu.png)

Here you are greeted by a menu consisting items (they're all from [CommandLineArguments.md](CommandLineArguments.md)):

* Arguments that have a signature **(selected: ___)** expect you to select from a list that opens when you select the corresponding item
* Arguments with a caption **(saved: ___)** expect you to enter data, the input field will be available when the corresponding item is selected (If you enter a **file path**, remove the **quotation marks!!!**)
* Arguments that have a signature **(disabled/enabled)** expect you to simply select them by pressing Enter. They will change their state when you reselect them.

* Obviously, **Back** is going to take you back to the past menu...

#### Menu Demonstration

![](../img/custom_settings_menu.png)

### After customization you should go back to the _Main Menu_ and click on _Do it, damn it!_
