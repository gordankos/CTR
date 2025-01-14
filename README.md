# CTR
Calorie Tracking & Recipes

v0.0.0, January 2025

Pure Python calorie tracker and recipe desktop app, enabling definition
of complex recipes with automated calculation of meal net nutrition values,
compensated for mass change due to water evaporation / absorption after cooking. 
Allows for full control over all food product nutrition values, without
relying on any online database or approximations of cooked meal nutrition values.

A weekend project to replace an existing calorie tracking Excel workbook, and
finally introduce some enhanced user interface features that are not possible
in Excel without convoluted workarounds.

This app is designed for anyone who prepares their own meals, wants to maintain an
accurate record of their daily calorie intake, and prioritizes data input efficiency
and advanced functionality over the flexibility of commercially available smartphone apps.

Features include:
  - Intuitive PySide6 based GUI
  - Light / Dark / Fusion theme selection
  - User-friendly daily calorie input with searchable recipe and product dropdown menus
  - Product catalogue definition with searchable catalogue table and input fields with auto-completion
  - Recipe definition with searchable ingredient dropdown menus
  - Simple navigation between recipes and a searchable recipes list
  - Calculation of recipe net nutrition values, compensated for water evaporation / absorption after cooking
  - Separate recipe ingredient gross and net amount handling
  - Recipe ingredient amount definition relative to other ingredient amount or net amount
  - Automatic circular reference detection with a warning message in recipe ingredients
  - Overview of daily intake history for any calendar day
  - PyQtGraph daily intake visualization diagram showing total calories and calories per macronutrient
  - Daily nutrition intake targets definition and color-coded visualization
  - Daily nutrition intake entries unaffected by changes made to recipe or product catalogue unless updated manually
  - Automatic transfer of favorite (starred) servings in daily intake table to the next calendar day
  - Custom data savefiles containing the products catalogue, recipes and daily intake data
  - Product catalogue and recipes import / export functionality
  - Unsaved data detection on application quit and optional save before exiting

## Disclaimer

CTR app does not have any networking capabilities and operates entirely offline. All data entered into
the app remains stored locally on your PC and is not shared, uploaded, or transmitted over the internet.
Users are solely responsible for maintaining backups or transferring their data if needed.
While every effort has been made to ensure data security within the app, the developer assumes no responsibility
for data loss or unauthorized access resulting from misuse or third-party actions outside the app's control.

Developers will make every effort to ensure savefile compatibility with previous CTR releases,
preventing any updates from breaking compatibility with existing savefiles.

There are currently no plans to develop or implement any networking capabilities for this application.

## Windows registry access
Application saves minimal data to Windows registry under HKEY_CURRENT_USER\Software\GK\CTR for:
  - Open / Save / Directory file dialog sidebar URLs, enabling saving of user selected (favorite) local directories for quick access in the file dialogs

## Required Packages
  - PySide6
  - PyQtDarkTheme
  - PyQtGraph
