# Prerequisites for using soundDB

<!-- MarkdownTOC autolink=true depth=2 bracket=round -->

- [Logistics and Installation](#logistics-and-installation)
    - [First Step: Windows Command Prompt](#first-step-windows-command-prompt)
    - [Installing Python](#installing-python)
    - [Using Python](#using-python)
- [Learning Python](#learning-python)
    - [Base Python language](#base-python-language)
    - [The Python Scientific Computing Stack](#the-python-scientific-computing-stack)
- [Other topics](#other-topics)
    - [Virtual Environments](#virtual-environments)
    - [Text Editor](#text-editor)

<!-- /MarkdownTOC -->


# Logistics and Installation

Note: these guides mostly cover the particulars of using Python on Windows. If you're using macOS or linux, Google can lead you to good tutorials for using the Terminal and installing Python, since there are far more resources and fewer nuances.

## First Step: Windows Command Prompt

All your interaction with Python will, at some point, require using the Windows Command Prompt. If you're unfamiliar with the Command Prompt, read [this tutorial](http://www.cs.princeton.edu/courses/archive/spr05/cos126/cmd-prompt.html) (skip the "Some Useful Commands" section; we're not using Java).

You only really need to know the very basics: changing directories (`cd`) and listing their contents (`dir`).

To run Command Prompt, press Start and search for "Command Prompt" or "cmd". I recommend making a shortcut too, since you'll use it often (right-click the icon while it's open and click "Pin this program to taskbar").

Tips:

- Copying and pasting in Command Prompt is particularly unintuitive.
    - To copy, select text with the mouse and press `Enter`.
    - To paste, right-click and the text will be inserted wherever your blinking cursor is.
- You can type the beginning of a file or folder name and press Tab to auto-complete
- The up and down arrows cycle through previous commands

## Installing Python

There are many ways to install a Python. The complexity has less to do with installing the Python interpreter itself, and more with installing and managing all the packages (libraries) that comprise the Python ecosystem. For Windows users, this is especially difficult, since the standard Python package manager ([pip](https://pip.pypa.io/en/stable/)) is hampered by Microsoft's lack of inclusion of C++ compiler. Either installing a compiler or finding the right pre-compiled versions of the libraries you need is a pain.

In my opinion, [Anaconda](https://docs.continuum.io/anaconda/) is by far the best way around these problems. Anaconda is a platform-agnostic Python distribution which includes its own package manager, with which you can download and install hundreds of the most popular scientific computing packages which have been pre-compiled for Windows by the Anaconda team.

The typical Anaconda installation pre-installes hundreds of popular packages for you. I prefer to keep things minimal and use [Miniconda](http://conda.pydata.org/miniconda.html), which pre-installs nothing except Python and the package manager tool, reducing bloat (400MB vs 3GB of stuff you probably won't use). By only installing what you need as you go, it's also easier to know what libraries your code actually requires.

1. Download the Python 3.5 64-bit Windows installer from <http://conda.pydata.org/miniconda.html>
2. Run the installer and follow the instructions. If unsure about any setting, simply accept the defaults as they all can be changed later.
3. When finished, open Command Prompt.
4. Type `conda --version` and hit Enter. If you see a version number, and not error messages, the installation worked.
5. Type `python` and hit Enter. You should see something like this:

    ```
    Python 3.5.1 |Continuum Analytics, Inc.| (default, Dec  7 2015, 15:00:12) [MSC v.1900 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>> 
    ```

    You are now in the Python interpreter! Try using Python as an overpowered calculator by typing in some math expressions.

    To exit the Python interpreter, press `Ctrl`+`Z`, then Enter.

### Installing necessary packages

As a start, I recommend installing these packages, which form the base of the Python scientific computing stack:

- [NumPy](http://www.numpy.org/) - Base N-dimensional array package
- [Pandas](http://pandas.pydata.org/) - Data structures & analysis
- [SciPy](https://www.scipy.org/scipylib/index.html) - Mathematical algorithms built on NumPy
- [Matplotlib](http://matplotlib.org/) - Comprehensive 2D Plotting
- [Jupyter](http://jupyter.org/) - Interactive data science environment, like MATLAB

To do so, open Command Prompt and run this command (remember you can paste into Command Prompt by right-clicking):

```
conda install pandas=0.18.1 numpy scipy matplotlib jupyter numexpr bottleneck
```

*(`numexpr` and `bottleneck` are recommended dependencies of pandas that improve performance. Pandas is explicitly restricted to v0.18.1 because the newest version is incompatible with soundDB for now; see issue #5)*

Did you get an error about `[SSL: CERTIFICATE_VERIFY_FAILED]`? Are you on the NPS network? Read on.

#### Sidebar: The Government is Decrypting Your Secure Internet Connection

In September 2016, DOI IT implemented "SSL Visibility" for secure Internet traffic on its network. "SSL Visibility" is a pleasant term for a man-in-the-middle attack: your connection passes through a device on the DOI network, which decrypts your secure traffic, scans it (for "malware and malicious links"), and re-encrypts it before sending it to its real destination. You can read an explanation of [how this works](http://www.zdnet.com/article/how-the-nsa-and-your-boss-can-intercept-and-break-ssl/), and the [security vulnerabilities it introduces](https://insights.sei.cmu.edu/cert/2015/03/the-risks-of-ssl-inspection.html).

Encryption uses "certificates", which verify a server is actually who it says it is. DOI has automatically installed a certificate on NPS computers so that they believe connections passing through this decrypting device are genuine. However, conda uses its own list of certificates. When it tries to connect, it doesn't recognize the certificate it gets as valid, and concludes that the server it reached is not who it says it is&mdash;which, in fact, is correct.

To make this work:

1. Download the DOI Root Certificate [from Google Drive](https://drive.google.com/file/d/0B551gy_Kqih1Y202VlFubnJPcFU/view). If that doesn't work, use [the DOI official link](http://blockpage.doi.gov/images/DOIRootCA.crt) instead&mdash;but know that this link is, ironically, insecure and theoretically opens a moderate security risk if anyone cared to exploit it.
2. Move the certificate file to your home folder. (You can put it elsewhere, but you'll need to adjust the commands you copy from this document accordingly.) Your home folder is `C:\Users\<your_username>`; click your full name in the top-right of the Start menu to open it.
3. Run this command in Command Prompt:

    ```
    conda config --set ssl_verify "%USERPROFILE%\DOIRootCA.cer"
    ```

4. Try the prior `conda install` command again. (Press the up arrow in Command Prompt to rerun previous commands.)

### Installing soundDB

soundDB and iyore are both pure-Python packages&mdash;no code needs to be compiled to install them. The standard package manager `pip` can handle that perfectly well on Windows, and it was simpler to distribute these packages through `pip`.

To install soundDB from my custom package index on GitHub with `pip`, run this command:

```
pip install --extra-index-url https://gjoseph92.github.io/soundDB/packages/ --extra-index-url https://nationalparkservice.github.io/iyore/packages/ soundDB
```

If you are on the NPS network and had certificate issues with conda, this will fail too. Assuming you already [downloaded the DOI Root Certificate](#sidebar-the-government-is-decrypting-your-secure-internet-connection) and put it in your home folder, here's the workaround:

- Any time you use `pip`, add the `--cert="%USERPROFILE%\DOIRootCA.cer"` flag.
- Assuming the certificate file is in your home folder and named `DOIRootCA.cer`, the command to install soundDB becomes:

    ```
    pip install --cert="%USERPROFILE%\DOIRootCA.cer" --extra-index-url https://gjoseph92.github.io/soundDB/packages/ --extra-index-url https://nationalparkservice.github.io/iyore/packages/ soundDB
    ```


#### Testing the Installation

To test that everything worked, open a Python interpreter (type `python` and press Enter). Type `import soundDB` and press Enter. Nothing might happen for a few seconds, then the command will finish and a new input line will appear, beginning with `>>>`. If there are no error messages, the installation worked. Exit the interpreter with `Ctrl`+`Z`.

## Using Python

As you've seen, to run the Python interpreter, you just run the `python` command in the Command Prompt. This is the interactive session: you type in a command and Python runs it and prints the result, which is handy for learning and exploring.

Python scripts are text files ending in `.py`, which really just contain a sequence of commands for that interpreter to execute. To run a Python script, `cd` to the folder containing it in the Command Prompt, then run `python <script_name.py>`.

### Using Jupyter Notebook

The interactive Python interpreter is helpful, but particularly for exploring data, it's nice to have an environment more like MATLAB or RStudio, where you can edit and rerun code you've written, create graphics, and write nicely-formatted notes and explanation along with your code.

[Jupyter](http://jupyter.org/) does this. It's a bit like Mathematica or MATLAB&mdash;except that it runs in a web browser. You can try it online here: <https://try.jupyter.org/>.

When using Jupyter, you create "notebook" files (`.ipynb`). These store your code, but they also store any output it produces (including graphics). This means you can share your notebooks (or put them on GitHub) and others can see your code and its results without rerunning it, or even needing the data. You can also export them as HTML files to share with people who don't have Python.

To run Jupyter Notebook, open the Command Prompt, `cd` into the directory in which you want to save your notebooks, and run `jupyter notebook`. After a couple seconds, a new page will open in your web browser. Create a new Python notebook and start writing. (If Internet Explorer opens instead of Chrome, you might want to make Chrome your default browser by opening the [Chrome settings page](chrome://settings) and scrolling to the bottom.)

Jupyter is easily learned through Googling and experimentation. A few things to know to get started, though:

- You enter code in cells. To run a cell, hit `Shift`-`Enter`.
- Press Tab to auto-complete variable names. Even better, if you have an object stored as, say, `metrics`, if you type `metrics.` and hit Tab, you'll see a list of all the attributes of the `metrics` object.
- Press `Shift`-`Tab` for documentation. The more times in a row you press it, the more documentation you get.

Great documentation for Jupyter notebooks can be found [here](http://nbviewer.jupyter.org/github/ipython/ipython/blob/3.x/examples/Notebook/Index.ipynb). (Jupyter used to be called IPython; this documentation is still accurate.)

Using Jupyter isn't necessary, but it can be a nicer environment for experimenting and learning, especially when working with pandas.

# Learning Python

Unlike R or MATLAB, Python is not a language designed specifically for statistics or scientific computing. It's a general-purpose high-level programming language used for everything from running web servers to controlling robots to building neural networks to geoprocessing to cleaning data. Due to its thoughtful design and extensibility, though, a mature ecosystem of packages has emerged that provide tools and data structures which have made it extremely popular for scientific computing.

All this means that "learning Python" is an oversimplification. To use soundDB, you first have to learn the syntax, data structures, and style of the core Python programming language. Then you'll need to be proficient with the scientific computing tools which sit on top of the base language. Then you can learn soundDB, which relies on those tools.

soundDB itself is actually rather simple. Sort of like how using driving directions with Google Maps is simple, but you need to know how to drive a car.

That could seem discouraging, but take it another way: because Python is so general-purpose, it's an extremely valuable investment of your time to learn. As you become proficient with Python, you may find yourself using it for tasks which have nothing to do with soundDB and NVSPL files.

## Base Python language

If you are just beginning to program, Python is one of the best places to start.

- [Learn Python the Hard Way](https://learnpythonthehardway.org/book/) is an intimidatingly-named but very popular resource for learning both the basics of programming and the Python language.
- The [Think Python](http://greenteapress.com/thinkpython/thinkpython.pdf) textbook is a great option, both for beginners and those cowboy codeslingers who want to finally put in the time to learn to think like computer scientists.

So you think you can program?

- Try [Crash into Python](https://stephensugden.com/crash_into_python/), which may end up feeling exactly like that.
- Get familiar with the syntax at <https://learnxinyminutes.com/docs/python3/>.
- Best option? Read the [Python tutorial](https://docs.python.org/3/tutorial/index.html) and skim through parts you already understand.

### Topics to Understand

However you want to learn, I'd suggest that you feel comfortable with (almost) all of these topics before moving on to NumPy, pandas, and the other scientific computing tools for Python. Topics in *italics* are helpful, but not as necessary. Googling any of these as `python <topic>` should get you all the answers you need. (FYI, being a computer scientist just means Googling things until you figure them out.)

- Basics
    - Assigning variables
    - `print()`
    - Comparisons (`==`, `<`, `>`, `<=`, `>=`, `is`, `is not`)
    - Boolean logic (`x and y`, `y or not z`)
    - `if`, `elif`, and `else`
    - Built-in `help()`
- Python data structures
    - `list`
    - `tuple`
    - `dict`
    - `set`
    - strings
- List slicing syntax
- Iteration (`for` loops)
    - Through lists
    - Through dicts (using `.keys()`, `.values()`, and `.items()`)
    - Iterators: `range`, `enumerate`, `zip`
    - *`map`*
- List and dictionary comprehensions
- *Reading and writing files*

- Functions
  - *Thinking about function contracts and invariants (how you'd learn functions in a CS101 class)*
  - Arguments
  - Returning values
  - *Recursion*
  - Keyword arguments
  - *Lambdas*
  - *Writing documentation strings*
  - *Unpacking multiple returned values*

- Importing modules

- *Classes*
  - *What is a class? What's an instance of a class? Why use classes?*
  - *What is `self`?*
  - *Magic methods*


## The Python Scientific Computing Stack

Time for the fun parts:

### NumPy

NumPy is the core package of the Python scientific computing stack. Knowing its basics will greatly help you understand the more powerful tools that use it, but you probably won't interact with NumPy much compared to pandas. So don't worry too much about the particulars.

To start: [What is NumPy](http://docs.scipy.org/doc/numpy/user/whatisnumpy.html)?

Once you know, read [NumPy basics](http://docs.scipy.org/doc/numpy/user/basics.html) up to byte-swapping.

Helpful references: [NumPy routines](http://docs.scipy.org/doc/numpy/reference/routines.html) - especially array creation, array manipulation, indexing, and mathematical functions.

### pandas

Think of pandas as a combination of Excel and NumPy.

If you like, get an overview at [Greg Reda's introduction](http://gregreda.com/2013/10/26/intro-to-pandas-data-structures/).

Then dive into the official documentation. Start with [Intro to Data Structures](http://pandas.pydata.org/pandas-docs/stable/dsintro.html), then [Essential Basic Functionality](http://pandas.pydata.org/pandas-docs/stable/basics.html), then [Indexing and Selecting Data](http://pandas.pydata.org/pandas-docs/stable/indexing.html). If you can still read, then keep going.

Once you feel you understand pandas pretty well, read Tom Augspurger's [Modern Pandas series](https://tomaugspurger.github.io/modern-1.html) to learn how to use pandas *well*.

### Visualization

There are a number of options for plotting in Python. In my opinion, there's still no one really good tool&mdash;in any language.

[matplotlib](http://matplotlib.org/) is the most popular and powerful plotting library, and serves as the base for some of the others. But the syntax and styling can be a pain. It's modeled after MATLAB's plotting, which might make you feel comfortable, or disgusted, or both.

Tip: to use matplotlib nicely in Jupyter, add this line after importing it:

```
%matplotlib inline
```

(That's a "magic" command that makes your plots render into the browser.)

After playing with matplotlib a bit, read [Tom Augspurger's article about visualization](https://tomaugspurger.github.io/modern-6-visualization.html) and consider learning [seaborn](http://seaborn.pydata.org/) too.

I'm personally very excited about [Vega](https://vega.github.io/vega/) (compiled with [Vincent](https://vincent.readthedocs.io/en/latest/index.html) in Python) and [Vega-lite](https://vega.github.io/vega-lite/) (with [Altair](https://altair-viz.github.io/) in Python), but have yet to use them. There's a good chance these could become the best way to succinctly and comprehensibly produce almost any visualization.

# Other topics

## Virtual Environments

<http://conda.pydata.org/docs/using/envs.html>

## Text Editor

You could write and edit Python scripts in Notepad if you want. But a nice text editor with syntax highlighting, autocomplete, and other features makes things much easier and pleasant.

I highly recommend [Sublime Text](https://www.sublimetext.com/). Some people like Notepad++, but Sublime Text features like multiple selections and the incredible autocomplete hugely speed up writing longer programs.

On some machines (Dell Latitude notebooks?), the very useful Sublime key shortcuts (`ctrl`-``alt``-`up`, `ctrl`-`alt`-`down`) will split the cursor onto the next line, and have the bonus feature of flipping the entire display upside-down, which some users have found undesirable. To resolve this, Right-click on the Desktop, go to Graphic Properties, click Options, turn Enable Hot Keys off, and click Apply.