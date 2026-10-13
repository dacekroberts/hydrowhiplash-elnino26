# Prompt to paste

I have uploaded one flat folder. Read 00_MANIFEST.md and brief.md first, then tell me in a few lines what you will build and anything in the brief you cannot do.

Before building, tell me your current limits: film length, pixel size, frame rates, the number and size of code and data modules, the number of uploaded assets. If any file here breaks one, say which.

Build one film: 16:9, 1920 x 1080 px, 30 fps, 150 s at most, eight scenes at the starts and lengths in the brief's table.

Build the dark theme only for now. Order of work: first one theme module that reads tokens.json, written so a light set can be switched in later, and one pace constant for every cut and camera move. Then the map from map_shapes.json with its region labels. Then the scenes, each as its own module so one can be dropped or stretched later.

Take every number from numbers.json, tests.csv, seasons.csv or winters.csv. Do not type, estimate or re-round a figure. If a scene needs a number that is not in those files, stop and ask.

Keep every rule under 'Rules the film keeps'. Where a rule and a nicer picture disagree, the rule wins.

On-screen wording: use the brief's card lines exactly. Do not add a headline, a caption or an adjective of your own; if a scene seems to need more words, ask.

Use the typefaces in the folder. The ref_ pictures show how the site draws the same data: match their colours and marks, not their layout.

Credits: a scene that shows burned area or climate values carries its sources' short credit, and the closing card carries every notice in credits.md.

When the film is built, send back what the brief lists under 'What comes back'. I export the MP4s myself from the film's page.
