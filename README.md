# Measuring Violations of Positive Involvement in Voting

This is the code used for the paper "Measuring Violations of Positive Involvement in Voting" by Wes Holliday and Eric Pacuit


## Where to start

tl;dr: An overview of Profiles and voting methods is found in 01-Profiles.ipynb and 02-VotingMethods.ipynb.   See 03-PI_instances.ipynb for the code to generate figures from the paper.

1. 01-Profiles.ipynb: Contains an overview of how to create profiles (implemented in voting/profiles.py) and generate profiles with different numbers of candidates/voters (implemented in voting/generate_profiles.py).   

A profile is created by initializing a Profile class object.  The needs a list of rankings (each ranking is a tuple of numbers), the number of candidates and a list giving the number of each ranking in the profile:

```python
from voting.profiles import Profile

rankings = [(0, 1, 2, 3), (2, 3, 1, 0), (3, 1, 2, 0), (1, 2, 0, 3), (1, 3, 2, 0)]
num_cands = 4
rcounts = [5, 3, 2, 4, 3]

prof = Profile(rankings, num_cands, rcounts=rcounts)
```

The function generate_profile is used to generate a profile for a given number of candidates and voters:  
```python
from voting.generate_profiles import generate_profile

# generate a profile using the Impartial Culture probability model
prof = generate_profile(3, 4) # prof is a Profile object with 3 candidate and 4 voters

# generate a profile using the Impartial Anonymous Culture probability model
prof = generate_profile(3, 4, probmod = "IAC") # prof is a Profile object with 3 candidate and 4 voters
```

3. Import and use voting methods (see voting/voting_methods.py for implementations and 02-VotingMethods.ipynb for an overview): 

```python
from voting.profiles import Profile
from voting.voting_methods import *

prof = Profile(rankings, num_cands, rcounts=rcounts)
print(f"The {borda.name} winners are {borda(prof)}")
```
4. See 03-Measuring_PI_violations.ipynb for the code to measure the vioaltions of positive invovlement.  

5. See 04-Visualizing_measures_PI_violations.ipynb for the code to generate the graphs from the paper.  

6. See 05-PI_instances.ipynb for instances of violations of positive involvement.  


## Dev Notes

* All of the code assumes that voters submit linear orders over the set of candidates. 
* In order to optimize some of the code for reasoning about profiles, it is assumed that in any profile the candidates are named by the initial segment of the non-negative integeters.  So, in a profile with 5 candidates, the candidate names are "0, 1, 2, 3, and 4".   Use the `cmap` varaible for different candidate names: `cmap` is a dictionary with keys 0, 1, ..., num_cands - 1 and values the "real" names of the candidates.  




## Other Files/Directories

1. voting/profiles.py: Implementation of the Profile class used to create and reason about profile (see 01-Profile.ipynb for an overview).

2. voting/voting_methods.py: Implemenations of the voting methods (see 02-VotingMethods.ipynb for an overview).

3. voting/generate_profiles.py: Implementation of  the funciton `generate_profile` to interface with the Preflib tools to generate profiles according to different probability models.   The code go generate profiles according to differnet probability models  is based on the [Preflib tools](https://github.com/PrefLib/PrefLib-Tools) used to genreate profiles according to different probability models. 

5. data/: Output of the simulations run on AWS to produce the figures in the paper. 

6. graphs_tark/: pdfs of the graphs from the paper.



## Requirements

All the code is written in Python 3. 

- The notebooks and most of the library is built around a full SciPy stack: [MatPlotLib](https://matplotlib.org/), [Numpy](https://numpy.org/), [Pandas](https://pandas.pydata.org/)
- [numba](http://numba.pydata.org/) 
- [networkx](https://networkx.org/)
- [tabulate](https://github.com/astanin/python-tabulate)
- [seaborn](https://seaborn.pydata.org/)  
- [multiprocess](https://pypi.org/project/multiprocess/) (only needed if running the simulations in  03-PI_instances.ipynb) 
- [tqdm.notebook](https://github.com/tqdm/tqdm)
