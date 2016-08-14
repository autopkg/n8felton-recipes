##MinitabExpressMU.munki

This recipe is for Minitab Express used with a Multi-User (MU) license.

To use this recipe you will either need to populate `MT_LICENSE_SERVER` in one of two ways:
  1. Create an override by running `autopkg make-override MinitabExpressMU.munki` and populate `MT_LICENSE_SERVER` in the override
  2. Pass it as a key when running the recipe, i.e., `autopkg run MinitabExpressMU.munki --key "MT_LICENSE_SERVER=27000@license.example.com"`
