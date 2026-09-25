# Fan Bing Research

**Study public work. Track change. Test transferable lessons.**

An independent, source-grounded research repository about Fan Bing (XDash), the author of the Chinese book *增长黑客*. Part of **People Research**: one person, one repository, one shared method.

This is not an official project, an archive of copyrighted full texts, a personality clone, or an endorsement by the subject. Identity evidence is documented in the [subject card](docs/SUBJECT.md).

The Chinese-language seed collection contains source records, dated events, work entries, eight case studies, five working hypotheses, counterevidence, and proposed experiments. Sources distinguish article reading from index inspection, partial reading, and podcast shownotes. Self-reports are not treated as independent confirmation. Read the [overview](research/OVERVIEW.md) and [coverage gaps](research/GAPS.md).

The initial release was assembled with AI assistance and still requires human review. Its review date is 2026-09-25, not a guarantee of complete or live coverage. Hypotheses describe observed public material, not a person's hidden motives or internal mental state.

## Local tools

Python 3.11+, standard library only:

```bash
python scripts/research.py validate
python scripts/research.py search "newsletter"
python scripts/research.py build --check
python -m unittest discover -s tests -v
```

Edit the normalized JSON data and original research notes, then run `build`. The included [Agent Skill](skills/person-research/SKILL.md) describes a portable workflow; browsing and file access must be provided by its host.

Original code and notes are MIT-licensed. Third-party sources retain their own rights; see [NOTICE](NOTICE.md). See the [Chinese README](README.md) for all reading paths and the [series guide](docs/SERIES.md) for reuse.
