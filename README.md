# Headmon

This public repository hosts the Headmon website, privacy policy, support
information, and public issue tracker.

Headmon is a private, local-only headache and migraine diary for Android and
iOS. The application source and development history are not hosted in this
repository.

## Support

- Website: https://headmondiary.com/
- In action: https://headmondiary.com/in-action/
- About: https://headmondiary.com/about/
- Support: https://headmondiary.com/support/
- Privacy policy: https://headmondiary.com/privacy/
- Informational use and medical notice: https://headmondiary.com/medical-notice/
- Support email for non-sensitive questions: headmon@proton.me
- Public bug reports and feature requests: use this repository's Issues tab.
- Security reports: follow [SECURITY.md](SECURITY.md) and email only invented,
  non-sensitive reproduction details rather than opening a public issue.

Never attach or email a Headmon JSON, CSV or PDF export, medical document,
private photo, exact location, or other health information. Use invented
example data. If a report cannot be made without personal information, do not
submit it.

## Repository scope

The contents are limited to public website and support material. The static
`/bv` backup workbench is a compiled artifact built from the public
[Headmon Backup Viewer source](https://github.com/HeadmonDiary/headmon-backup-viewer).
Its exact corresponding source revision, build command, license, and artifact
hashes are recorded in [`site/bv/SOURCE.txt`](site/bv/SOURCE.txt). The workbench
processes a selected backup in tab memory, does not upload it, does not persist
it in browser storage, and removes the draft database used by earlier preview
versions when it loads.

The backup viewer is licensed under GPL-3.0. No open-source license is granted
for the remaining Headmon-authored website or application material. Bundled
third-party components retain the terms listed in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). This repository is not the
Headmon mobile application source distribution.
