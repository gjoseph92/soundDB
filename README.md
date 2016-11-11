# soundDB

A library for the NPS Natural Sounds & Night Skies Division to make going from data-somewhere-on-disk to data-ready-for-processing as painless as possible.

----------------------------------

## Demo

## First, the problem

These are the annoyances soundDB hopes to solve:

1. We have lots of natural sounds data (NVSPL files, audio, etc.), stored in lots of different places. Though the contents of the files is usually consistent, the way they're *organized* in all those different places often isn't. Code that reads all the NVSPL files for one park may not work for another, because they keep their NVSPL in a different place.
2. Many people have written functions for parsing the data. Many times. If we share one set of good parsing functions, we won't have to write them again.

Ask your doctor: if your data is always well-organized and you like rewriting code, soundDB may not be right for you.

## The system

soundDB solves problem 1 using the library [`iyore`](https://github.com/nationalparkservice/iyore). You should first read about iyore, since it's critical for using soundDB effectively. But here's the gist:

Your datasets may be organized in many different ways. But if you can tell the computer *how* each one is organized, then pulling out just the files you want is a snap.

