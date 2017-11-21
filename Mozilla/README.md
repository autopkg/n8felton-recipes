The FirefoxDeveloperEdition recipes in this repo have been deprecated and the autopkg/recipes `Mozilla/Firefox.munki.recipe` should be used instead. You can see [autopkg/recipes#218](https://github.com/autopkg/recipes/pull/218) for more info.

The steps to use those recipes would be as follows:

```
autopkg repo-add recipes
autopkg make-override Firefox.munki.recipe -n FirefoxDeveloperEdition.munki.recipe
```
From there you will want to edit the override and change `RELEASE` to `devedition-latest` as well as updating the `NAME` and `display_name` within the pkginfo.

If you're trying to run the recipe as a one-off you can accomplish the same by doing `autopkg run Firefox.munki --key=RELEASE=devedition-latest --key=NAME=FirefoxDeveloperEdition`. However, you'd still need to update the `display_name` in Munki after it imports.
