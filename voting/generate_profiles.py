'''
    File: profile_optimized.py
    Author: Eric Pacuit (epacuit@umd.edu)
    Date: December 7, 2020
    
    Functions to generate profile
    
    Most of the functions interface with the preflib tools
    
    Main Functions
    --------------
    prob_models: dictionary with functions to create profiles for various probability models
    generate_profile: generates a profile
    
'''


from .preflibtools.generate_profiles  import *
from .profiles import Profile
import numpy as np # for the SPATIAL model

#############
# wrapper functions to interface with preflib tools for generating profiles
#############

def create_rankings_mallows(num_voters, cmap, phi, ref=None):
    '''create a profile using a mallows model with dispersion param phi
    ref is the reference ranking.
    
    wrapper function to call the preflib function gen_mallows
    '''
    if ref == None:
        ref, refc = gen_impartial_culture_strict(1, cmap)
        
    _rmaps, rcounts = gen_mallows(num_voters, cmap, [1.0], [phi], ref)
    
    # fix candidate names so that they range from 0 to num_cands-1 
    # the preflib gen_mallows function returns candidate maps where candidates
    # are named 1...num_cands
    
    rmaps = [{cname - 1: rank for cname,rank in _r.items()} for _r in _rmaps]
    return  rmaps, rcounts

def create_rankings_mallows_two_rankings(num_voters, cmap, phi, ref=None):
    '''create a profile using a Mallows model with dispersion param phi
    ref is two linear orders that are reverses of each other 
    
    wrapper function to call the preflib function gen_mallows with 2 reference rankings
    
    '''
    
    if ref == None:
        ref, refc = gen_impartial_culture_strict(1, cmap)
    ref1 = ref[0]
    
    # reverse the ref1 ranking
    _rankings = [sorted(list(r.items()), key=lambda _r: _r[1]) for r in ref]
    _ranking= [[_cr[0] for _cr in _crs] for _crs in _rankings] [0]
    _ranking.reverse()
    ref2 = {c:cidx+1 for cidx,c in enumerate(_ranking)}

    _rmaps, rcount = gen_mallows(num_voters, cmap, [0.5, 0.5], [phi, phi], [ref1, ref2])
    
    # fix candidate names so that they range from 0 to num_cands-1 
    # the preflib gen_mallows function returns candidate maps where candidates
    # are named 1...num_cands
    
    rmaps = [{cname - 1: rank for cname,rank in _r.items()} for _r in _rmaps]
    return rmaps, rcount

def create_rankings_urn(num_voters, cmap, replace):
    """create a list of rankings using the urn model
    
    wrapper function to call the preflib function gen_urn_strict
    """

    return gen_urn_strict(num_voters, replace, cmap)        

def create_rankings_single_peaked(num_voters, cmap, param):
    """create a single-peaked list of rankings
    
    wrapper function to call the preflib function gen_single_peaked_impartial_culture_strict
    """
    
    return gen_single_peaked_impartial_culture_strict(num_voters, cmap)

def get_ranking(candidates):
    '''get a ranking (using impartial culture) from a list of candidates'''
    refm, refc = gen_impartial_culture_strict(1, {c:c for c in candidates})
    return rmap_to_linear_rankings(refm)[0]

def rmap_to_linear_rankings(rmaps): 
    '''convert rmaps from preflib to a list of tuples
    
    The function assumes that rmaps represents linear orderings of the candidates
    and that the names of the candidates are 1,2,...num_cands
    
    rmaps: dict
        dictionary provided by preflib profile generation functions
    '''
    
    _rankings = [sorted(list(r.items()), key=lambda _r: _r[1]) for r in rmaps]
    return [tuple([_cr[0] for _cr in _crs]) for _crs in _rankings] 


###########
# generate profile using the spatial model
##########


def voter_utility(v_pos, c_pos, beta):
    '''Based on the Rabinowitz and Macdonald (1989) mixed model
    described in Section 3, pp. 745 - 747 of 
    "Voting behavior under the directional spatial model of electoral competition" by S. Merrill III 
    
    beta = 1 is the proximity model
    beta = 0 is the directional model
    '''
    return 2 * np.dot(v_pos, c_pos) - beta*(np.linalg.norm(v_pos)**2 + np.linalg.norm(c_pos)**2)

def create_prof_spatial_model(num_voters, cmap, params):
    num_dim = params[0] # the first component of the parameter is the number of dimensions
    beta = params[1] # used to define the mixed model: beta = 1 is proximity model (i.e., Euclidean distance)
    num_cands = len(cmap.keys())  
    mean = [0] * num_dim # mean is 0 for each dimension
    cov = np.diag([1]*num_dim)  # diagonal covariance
    
    # sample candidate/voter positions using a multivariate normal distribution
    cand_positions = np.random.multivariate_normal(np.array(mean), cov, num_cands)
    voter_positions = np.random.multivariate_normal(np.array(mean), cov, num_voters)
    
    # generate the rankings and counts for each ranking
    ranking_counts = dict()
    for v,v_pos in enumerate(voter_positions):
        v_utils = {voter_utility(v_pos,c_pos,beta): c for c,c_pos in enumerate(cand_positions)}
        ranking = tuple([v_utils[_u] for _u in sorted(v_utils.keys(),reverse=True)])
        if ranking in ranking_counts.keys():
            ranking_counts[ranking] += 1
        else:
            ranking_counts.update({ranking:1})
    
    # list of tuples where first component is a ranking and the second is the count
    prof_counts = ranking_counts.items()
    
    return [rc[0] for rc in prof_counts], [rc[1] for rc in prof_counts]


##########
# functions to generate profiles
##########

# dictionary of all the avialble probability models with default parameters
prob_models = {
    "IC": {"func": create_rankings_urn, "param": 0}, # IC model is Mallows with phi=1.0
    "IAC": {"func": create_rankings_urn, "param": 1}, # IAC model is urn with alpha=1
    "MALLOWS": {"func": create_rankings_mallows, "param": 0.8}, 
    "MALLOWS_2REF": {"func": create_rankings_mallows_two_rankings, "param": 0.8}, 
    "URN": {"func": create_rankings_urn, "param": 10},
    "SinglePeaked": {"func": create_rankings_single_peaked, "param": None},
    "SPATIAL": {"func": create_prof_spatial_model, "param": (3, 1.0)},

}
 

def generate_profile(num_cands, num_voters, probmod="IC", probmod_param=None):
    '''generate a profile with num_cands candidates and num_voters voters using 
    the probmod probabilistic model (with parameter probmod_param)
    
    Parameters
    ----------
    num_cands: int 
        number of candidates
    num_voters: int
        number of voters
    probmod: str
        name of the probability model to use, default is IC (impartial culture)
        other options are IAC (impartial anonymous culture), URN (urn model with default alpha=10),
        MALLOWS (Mallows with default phi=0.8), MALLOWS_2REF (Mallows with two reference rankings that 
        are reverses of each other and default phi=0.8), SinglePeaked (single peaked profile), and 
        SPATIAL (default is the proximity model with 2 dimensions)
    probmod_param: number
        alternative parameter for the different models (e.g., different dispersion parameter for Mallows)
    '''
    # candidates names must be 0,..., num_cands - 1
    cmap = {cn:cn for cn in range(num_cands)}
    create_rankings = prob_models[probmod]["func"]
    probmod_p = prob_models[probmod]["param"] if  probmod_param is None else probmod_param 
    
    # use preflib tools to generate the rankings
    rmaps, rmapscounts = create_rankings(num_voters, cmap, probmod_p) 
    
    # the SPATIAL model creates a list of tuples, but the preflib functions creates a list of dictionaries
    rankings = rmap_to_linear_rankings(rmaps) if probmod != "SPATIAL" else rmaps 
    return Profile(rankings, num_cands, rcounts=rmapscounts)
