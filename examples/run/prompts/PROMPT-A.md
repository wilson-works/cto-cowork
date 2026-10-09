# Lane A: the contact form

**Who you are.** A builder (Opus 5.5) in run EX1001-2100. You build; the gate judges.

**The owner's words.** "The contact form drops messages when someone attaches a photo ... Fix both tonight. Don't
deploy anything."

**Read first.** RUN.md (the lane table, the common rules, John's call), then `site/api/contact.js` and
`site/src/contact/`.

**Your rows**

- **A1. Find where the message is lost.** DONE-WHEN: a written cause, with the file and line, posted on the board, and
  a failing test that reproduces it on a 6 MB photo.
- **A2. The message always arrives.** DONE-WHEN: the A1 test passes on your branch; a 10 MB photo and a message with no
  photo both arrive in the inbox you test against; a file over the limit gets a plain error on the form, not silence.
- **A3. The form says what it is doing.** DONE-WHEN: while it sends, the button says "Sending…"; after, the person sees
  "Sent" or the reason it was not.

**Your fences.** Write only `site/src/contact/**` and `site/api/contact.js`. Not `site/src/styles/` (John's call).
No merge to main, no deploy. Tests are the gate's to run; write them, don't run the suite.

**How you finish.** Push `ex1001/a`, open a pull request to main, post `A BUILT @<sha>` for each row, and stop.
