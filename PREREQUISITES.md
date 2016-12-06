# Prerequisites for using soundDB

Here are some guidelines for getting started with soundDB, from [installing Python](#installing-python) to resources for [learning the language](#learning-python).

# Logistics and Installation

Note: these guides mostly cover the particulars of using Python on Windows. If you're using macOS or linux, Google can lead you to good tutorials for using the Terminal and installing Python, since there are far more resources and fewer nuances.

## First Step: Windows Command Prompt

All your interaction with Python will, at some point, require using the Windows Command Prompt. If you're unfamiliar with the Command Prompt, read [this tutorial](http://www.cs.princeton.edu/courses/archive/spr05/cos126/cmd-prompt.html) (skip the "Some Useful Commands" section; we're not using Java).

You only really need to know the very basics: changing directories (`cd`) and listing their contents (`dir`).

To run Command Prompt, press Start and search for "Command Prompt" or "cmd". I recommend making a shortcut too, since you'll use it often (right-click the icon while it's open and click "Pin this program to taskbar").

## Installing Python

There are many ways to install a Python. The complexity has less to do with installing the Python interpreter itself, and more with installing and managing all the packages (libraries) that comprise the Python ecosystem. For Windows users, this is especially difficult, since the standard Python package manager ([pip](https://pip.pypa.io/en/stable/)) is hampered by Microsoft's lack of inclusion of C++ compiler. Either installing a compiler or finding the right pre-compiled versions of the libraries you need is a pain.

In my opinion, [Anaconda](https://docs.continuum.io/anaconda/) is by far the best way around these problems. Anaconda is a platform-agnostic Python distribution which includes its own package manager, with which you can download and install hundreds of the most popular scientific computing packages which have been pre-compiled for Windows by the Anaconda team.

The typical Anaconda installation pre-installes hundreds of popular packages for you. I prefer to keep things minimal and use [Miniconda](http://conda.pydata.org/miniconda.html), which pre-installs nothing except Python and the package manager tool, reducing bloat (400MB vs 3GB of stuff you probably won't use). By only installing what you need as you go, it's also easier to know what libraries your code actually requires.

1. Download the Python 3.5 64-bit Windows installer from <http://conda.pydata.org/miniconda.html>
2. Run the installer and follow the instructions. If unsure about any setting, simply accept the defaults as they all can be changed later.
3. When finished, a new Command Prompt window will open. If not, run Command Prompt yourself.
4. Type `conda --version` and hit Enter. If you see a version number, and not error messages, the installation worked.
5. Type `python` and hit Enter. You should see something like this:

    ```
    Python 3.5.1 |Continuum Analytics, Inc.| (default, Dec  7 2015, 15:00:12) [MSC v.1900 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>> 
    ```

    You are now in the Python interpreter! Try using Python as an overpowered calculator by typing in some math expressions.

    To exit the Python interpreter, press `Ctrl`+`Z`, then Enter.

## Installing necessary packages

As a start, I recommend installing these packages, which form the base of the Python scientific computing stack:

- [NumPy](http://www.numpy.org/) - Base N-dimensional array package
- [Pandas](http://pandas.pydata.org/) - Data structures & analysis
- [SciPy](https://www.scipy.org/scipylib/index.html) - Mathematical algorithms built on NumPy
- [Matplotlib](http://matplotlib.org/) - Comprehensive 2D Plotting
- [Jupyter](http://jupyter.org/) - Interactive data science environment, like MATLAB

To do so, open Command Prompt and run this command:

```
conda install pandas=0.18.1 numpy scipy matplotlib jupyter numexpr bottleneck
```

*(`numexpr` and `bottleneck` are recommended dependencies of pandas that improve performance. Pandas is explicitly restricted to v0.18.1 because the newest version is incompatible with soundDB for now; see issue #5)*

## Installing soundDB

soundDB and iyore are both pure-Python packages&mdash;no code needs to be compiled to install them. The standard package manager `pip` can handle that perfectly well on Windows, and it was simpler to distribute these packages through `pip`.

Miniconda doesn't install `pip` by default, so first we'll do that. In a Command Prompt window, run:

```
conda install pip
```

Next, install soundDB from my custom package index on GitHub with `pip`:

```
pip install --extra-index-url https://gjoseph92.github.io/soundDB/packages/ --extra-index-url https://nationalparkservice.github.io/iyore/packages/ soundDB
```

To test that this worked, open a Python interpreter (type `python` and press Enter). Type `import soundDB` and press Enter. Nothing might happen for a few seconds, then the command will finish and a new input line will appear, beginning with `>>>`. If there are no error messages, the installation worked. Exit the interpreter with `Ctrl`+`Z`.

## Using Python

As you've seen, to run the Python interpreter, you just run the `python` command in the Command Prompt. This is the interactive session: you type in a command and Python runs it and prints the result, which is handy for learning and exploring.

Python scripts are text files ending in `.py`, which really just contain a sequence of commands for that interpreter to execute. To run a Python script, `cd` to the folder containing it in the Command Prompt, then run `python <script_name.py>`.

# Learning Python

Unlike R or MATLAB, Python is not a language designed specifically for statistics or scientific computing. It's a general-purpose high-level programming language used for everything from running web servers to controlling robots to building neural networks to geoprocessing to cleaning data. Due to its thoughtful design and extensibility, though, a mature ecosystem of packages has emerged that provide tools and data structures which have made it extremely popular for scientific computing.

All this means that "learning Python" is an oversimplification. To use soundDB, you first have to learn the syntax, data structures, and style of the core Python programming language. Then you'll need to be proficient with the scientific computing tools which sit on top of the base language. Then you can learn soundDB, which relies on those tools.

soundDB itself is actually rather simple. Sort of like how using driving directions with Google Maps is simple, but you need to know how to drive a car.

## Base Python language

Just learning to program? Try [Learn Python the Hard Way](https://learnpythonthehardway.org/book/), or the [Think Python](http://greenteapress.com/thinkpython/thinkpython.pdf) textbook. You will learn to program well, slowly.

Already a proficient programmer? Try [Crash into Python](https://stephensugden.com/crash_into_python/), which may end up feeling exactly like that. Or get familiar with the syntax at <https://learnxinyminutes.com/docs/python3/>. The best option might be the official [Python tutorial](https://docs.python.org/3/tutorial/index.html), and skim ahead through parts you already understand.

## The Python Scientific Computing Stack

### Jupyter

[Jupyter](http://jupyter.org/) is an interactive environment for Python (and a number of other languages, actually) that combines code and nicely formatted text in cells, a bit like Mathematica or MATLAB&mdash;except that it runs in a web browser. You can try it online here: <https://try.jupyter.org/>.

To run jupyter notebook, open the Command Prompt, `cd` into the directory in which you want to save your notebooks, and run `jupyter notebook`. After a couple seconds, a new page will open in your web browser. Create a new Python notebook.

Jupyter is easily learned through Googling and experimentation. To get started, you really just need to know that you run cells with `shift`-`enter` (like Mathematica).

Using Jupyter isn't necessary, but it can be a nicer environment for experimenting and learning, especially when working with pandas.

### NumPy

NumPy is the core package of the Python scientific computing stack. Knowing its basics will greatly help you understand the more powerful tools that use it, but you probably won't interact with NumPy much compared to pandas. So don't worry too much about the particulars.

To start: [What is NumPy](http://docs.scipy.org/doc/numpy/user/whatisnumpy.html)?

Once you know, read [NumPy basics](http://docs.scipy.org/doc/numpy/user/basics.html) up to byte-swapping.

Helpful references: [NumPy routines](http://docs.scipy.org/doc/numpy/reference/routines.html) - especially array creation, array manipulation, indexing, and mathematical functions.

### pandas

pandas is a little like Excel, but made out of NumPy.

If you like, get an overview at [Greg Reda's introduction](http://gregreda.com/2013/10/26/intro-to-pandas-data-structures/).

Then dive into the official documentation. Start with [Intro to Data Structures](http://pandas.pydata.org/pandas-docs/stable/dsintro.html), then [Essential Basic Functionality](http://pandas.pydata.org/pandas-docs/stable/basics.html), then [Indexing and Selecting Data](http://pandas.pydata.org/pandas-docs/stable/indexing.html). If you can still read, then keep going.

Once you feel you understand pandas pretty well, read Tom Augspurger's [Modern Pandas series](https://tomaugspurger.github.io/modern-1.html) to learn how to use pandas *well*.

# Other topics

### Virtual Environments

<http://conda.pydata.org/docs/using/envs.html>

### Text Editor

You could write and edit Python scripts in Notepad if you want. But a nice text editor with syntax highlighting, autocomplete, and other features makes things much easier and pleasant.

I highly recommend [Sublime Text](https://www.sublimetext.com/). Some people like Notepad++, but Sublime Text features like multiple selections and the incredible autocomplete hugely speed up writing longer programs.

On some machines (Dell Latitude notebooks?), the very useful Sublime key shortcuts (`ctrl`-``alt``-`up`, `ctrl`-`alt`-`down`) will split the cursor onto the next line, and have the bonus feature of flipping the entire display upside-down, which some users have found undesirable. To resolve this, Right-click on the Desktop, go to Graphic Properties, click Options, turn Enable Hot Keys off, and click Apply.