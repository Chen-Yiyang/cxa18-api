import math

def retweet_influence(retweets):
    """
    The more retweets, the less the result (i.e. the multiplier/ratio) will be
    rationale: the more influence a tweet has (in terms of retweets), the more cautious readers should be while handling it
    the ratio is [0.8, 1.0]
    """
    ratio = 0.2 * math.exp(-0.001*retweets) + 0.8

    return ratio
