# 10 — Test matrix and evidence naming

| Area | Local synthetic | Hosted Linux | Windows | Real authorized |
| --- | --- | --- | --- | --- |
| Fable static/runtime + record | upstream baseline only | upstream historical | upstream historical | targeted opt-in |
| Astra observation/spec | upstream baseline only | upstream 940/2 historical | latest Windows mixed failures | none |
| REA adapter | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN |
| CSV parser/schema preview | NOT_RUN | NOT_RUN | NOT_RUN | sanitized user CSV |
| Generated app API + SQLite | NOT_RUN | NOT_RUN | NOT_RUN | only disposable approved copy |
| Browser list/filter/detail | NOT_RUN | NOT_RUN | NOT_RUN | 1 real owner-approved site |
| 3 domain examples | NOT_RUN | NOT_RUN | NOT_RUN | sample only |
| Windows packaging UX | NOT_RUN | n/a | NOT_RUN | user acceptance |

Evidence report format: test command; UTC+KST date; commit SHA; OS, Python/Node/Chromium versions; test case count pass/fail/skip; stderr or diagnosis; artifact redaction result; scope disclaimer.
No assertions from upstream snapshots count toward a new REA integration PASS. Do not reclassify 2 skipped tests as passing. Keep Windows failure 96 fail/108 error known issue until classified.
