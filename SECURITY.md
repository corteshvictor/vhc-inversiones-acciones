# Security Policy

This project reads files that nobody in the chain controls. A user downloads an
XLSX from a screener or a PDF report and hands it to an AI agent, which parses it
and writes an HTML dashboard. Every one of those steps takes input from outside
and produces output that someone opens. That is why this file exists.

## Reporting a vulnerability

**Do not open a public issue.** A report filed in the open tells everyone about
the flaw before there is a fix.

Report it privately through
[GitHub Security Advisories](https://github.com/corteshvictor/vhc-inversiones-acciones/security/advisories/new),
which keeps the conversation between you and the maintainer until a fix ships.

That form exists only on public repositories. While this one is private the link
resolves to nothing, and anyone who can read this file already has repository
access: use whatever private channel granted you that access, and never a public
issue. `RELEASING.md` records enabling the form as a step of going public, so the
channel is live by the time anyone outside can read this.

Useful things to include, when you have them: what the flaw allows, the file or
input that triggers it, the version or commit you tested, and whether it is
already public elsewhere. A minimal reproducing file is worth more than a long
description.

Expect an acknowledgement within a few days. This is a single-maintainer project,
not a company with an on-call rotation, so please read silence as absence rather
than as dismissal, and feel free to send a reminder.

## Supported versions

The latest release is the one that receives fixes. Older tags stay published for
reference and are not patched.

## What this project defends against

These are the defenses in place. A report that defeats any of them is a
vulnerability, not a feature request.

**Malicious spreadsheets.** XML is parsed through `defusedxml`, which refuses the
entity expansion and external entity tricks that turn a small file into a denial
of service or a file read. Six ceilings bound what a single attachment can cost:
file size, entries inside the archive, uncompressed bytes in total and per
member, rows, and columns. A zip bomb hits them before it hits memory.

**Injected instructions.** An attachment is data, never a command. The skill
treats the contents of an XLSX, a PDF and any page it reads as untrusted
evidence, and ignores text that tries to redefine the task, impersonate the user
or alter the rules. When a file does carry such an attempt, saying so is the
first thing in the answer, above the analysis — a warning buried mid-report is a
warning nobody reads.

**Output that runs.** The dashboard is HTML built from names and labels that came
out of the attachment. Every one of those values is escaped before it reaches the
page, so a company named with a script tag stays text.

**A stale sector list.** Classification depends on a CSV of financials and
utilities. The tool refuses to run when it is missing rather than silently
skipping the exclusion, and warns once the list is more than 180 days old.

## What is out of scope

- **The judgement of the classification.** A company you believe is misclassified
  is a methodology discussion, not a vulnerability. Open an issue.
- **The data itself.** Figures come from InvestingPro. Their accuracy is theirs.
- **The AI platform.** Flaws in Claude, ChatGPT or Codex belong to their vendors.
- **`tools/merge_exports.py`.** The READMEs do teach it, so it is not an
  internal utility — but it neither inspects the archive beforehand nor applies
  the ceilings above, and it never touches the network. The `defusedxml` defense
  it does inherit, because `openpyxl` uses it. It reads exports the user
  downloaded from their own account, which is a different threat model from an
  attachment someone else sent, and the READMEs say so where they teach it. A
  hostile spreadsheet fed to it deliberately is out of scope; one handed to the
  skill is not.
- **Running the scripts on files you already distrust, outside the skill.** The
  ceilings assume an attachment of a plausible size. Point them at something
  arbitrary and you are on your own.

## What this project is not

It filters companies for study. It is not financial advice, no category is an
instruction to buy or sell, and nothing here is a price forecast. Acting on the
output is a decision that belongs to the person reading it.
