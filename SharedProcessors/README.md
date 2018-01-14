# AppleSupportDownloadInfoProvider

## Description
Provides links to downloads posted to the Apple support knowledge bases.

## Input Variables
- **LOCALE:**
    - **required:** False
    - **description:** The ISO-639 language code and the ISO-3166 country code e.g. en\_US = English, American es\_ES = Español, Spain
- **ARTICLE\_NUMBER:**
    - **required:** True
    - **description:** The KB article number without the leading 'DL' e.g. https://support.apple.com/kb/dl907 ARTICLE\_NUMBER = 907

## Output Variables
- **url:**
    - **description:** The full url for the file you want to download.
- **version:**
    - **description:** The version of the support download

# HPSoftwareInfoProvider

## Description
Determines the ESSENTIAL-REQUIRED software necessary for a given product\_number. Returns the URL, version and description of the software.

## Input Variables
- **lang\_code:**
    - **default:** en
    - **required:** False
    - **description:** ISO 639-1 code for preferred language
- **os:**
    - **default:** Mac OS X 10.11
    - **required:** False
    - **description:** The OS you want to search for
- **product\_number:**
    - **required:** True
    - **description:** HP Product Number of device that requires software. Typically 6 alphanumeric characters, e.g. E6B70A
- **country\_code:**
    - **default:** us
    - **required:** False
    - **description:** ISO 3166-1 alpha-2 code for preferred country

## Output Variables
- **url:**
    - **description:** The full url for the software.
- **version:**
    - **description:** The version of the software.
- **description:**
    - **description:** A description of the software.

# MD5Checksum

## Description
Calculate a message-digest fingerprint (checksum) for a file

## Input Variables
- **pathname:**
    - **required:** True
    - **description:** Path of the file to calculate MD5 checksum on.
- **md5checksum:**
    - **required:** False
    - **description:** A MD5 checksum to verify pathname.

## Output Variables
- **md5checksum:**
    - **description:** MD5 checksum calculated from pathname.

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

## Output Variables

# PkgInfoVersioner

## Description
Finds a package given it's package ID and modifies the PackageInfo version, resulting in the receipt database containing the modified version information.

## Input Variables
- **unpacked\_path:**
    - **required:** True
    - **description:** The path where the package containing the PKGID you want to change the version of is extracted to. Should match destination\_path of FlatPkgUnpacker processor.
- **PKGID:**
    - **required:** True
    - **description:** The package id of the pkg-ref you want to changethe version of.
- **VERSION:**
    - **required:** True
    - **description:** The version you want to set the PKGID to

## Output Variables

# RemoteFilenameFinder

## Description
Finds the proper file name for a download.

## Input Variables
- **url:**
    - **required:** True
    - **description:** The URL to retrieve the remote filename for.
- **CURL\_PATH:**
    - **default:** /usr/bin/curl
    - **required:** False
    - **description:** Path to curl binary. Defaults to /usr/bin/curl.

## Output Variables
- **filename:**
    - **description:** The retrieved remote filename.

# RubyGemInfoProvider

## Description
Provides information about the latest version of a given Ruby gem

## Input Variables
- **gem\_name:**
    - **required:** True
    - **description:** The name of the ruby gem you want the information for.

## Output Variables
- **gem\_description:**
    - **description:** Short description of the gem.
- **gem\_version:**
    - **description:** The latest version of the gem.

# SourceForgeBestReleaseURLProvider

## Description
Provides URLs to the "Best Release" of a project on SourceForge. The "Best Release" is set by the project maintainer, and while one would think that should always be the "latest stable" release, that is not always the case. Always verify output.

## Input Variables
- **SOURCEFORGE\_PROJECT\_NAME:**
    - **required:** True
    - **description:** A SourceForge project's "URL Name" e.g. `https://sourceforge.net/projects/burn-osx` would use "URL Name" `burn-osx`

## Output Variables
- **url:**
    - **description:** The full url for the file you want to download.
- **md5checksum:**
    - **description:** The MD5 checksum of the file, provided by the API.
