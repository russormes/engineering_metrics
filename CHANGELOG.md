# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- This CHANGELOG.md. Because I think it is a good idea. So there!
- The JiraIssue class is a subclass of the Python `dict` class. This means that we store attributes for programatic access along with entries to the dictionary. The second is primarily for issues to be used in pandas data structures as dictionaries and so exposes issue data in a useful format for data frames. This release adds some atrributes to the class, adds some values to the dictionary AND renames some existing dictionary keys, which may break some existing notebooks if not addressed. The list of changes are 
    - `assignee` is now an `dict` attribute on the class and the JiraIssue contains two new keys `assigneeName` and `assigneeEmail`
    - `cycle_time` and `lead_time` are now class attributes and the corresponding dicitonary keys are `cycleTime` and `leadTime`
    - `updated_at` is now a class attribute and the corresponding dicitonary key is `updatedAt`
    - `updated_at` is now a class attribute and the corresponding dicitonary key is `updatedAt`
    - the `issuelinks` key has changed to `issueLinks` to match the naming convention of underscore attributes and camel case keys.