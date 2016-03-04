# AppleSupportDownloadInfoProvider

## Description
Provides links to downloads posted to the Apple support knowledge bases.

## Input Variables
- **LOCALE:**
    - **required:** False
    - **description:** The ISO-639 language code and the ISO-3166 country code e.g. en\_US = English, American es\_ES = Español, Spain
- **ARTICLE\_NUMBER:**
    - **required:** True
    - **description:** The KB article number without the leading 'DL' e.g. http://support.apple.com/kb/dl907 ARTICLE\_NUMBER = 907

## Output Variables
- **url:**
    - **description:** The full url for the file you want to download.
- **version:**
    - **description:** The version of the support download

# MunkiGitCommitter

## Description
Allows AutoPkg to commit changes to a munki repository that is tracked by a git repository.

## Input Variables
- **GIT\_COMMIT\_MESSAGE:**
    - **required:** False
    - **description:** Any additional message you want attached to the commit.
- **MUNKI\_REPO:**
    - **required:** True
    - **description:** Path to a mounted Munki repo.
- **munki\_importer\_summary\_result:**
    - **required:** False
    - **description:** Stuff goes here

### Example use:
```
$ autopkg run GoogleChrome.munki.recipe --post com.github.n8felton.shared/MunkiGitCommitter
```
This will add and commit the pkginfo to your git repository with the message format:
```
[AutoPkg] Adding %NAME% version %VERSION%
```
