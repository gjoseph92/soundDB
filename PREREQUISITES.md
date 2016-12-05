# Prerequisites for using soundDB

Here are some guidelines for getting started with soundDB, from installing Python to resources for learning the language.

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

*(`numexpr` and `bottleneck` are recommended dependencies of pandas that improve performance. Pandas is explicitly restricted to v0.18.1 because the newest version is incompatible for now; see issue #5)*