"""
Consensus filter between local ML model
and global NWP forecast.

ML is treated as a local expert.

NWP is treated as a global observer.
"""


NEIGHBOURS = {

    0: [1],

    1: [0, 2],

    2: [1, 3],

    3: [2],

    51: [53],

    53: [51, 55],

    55: [53],

    61: [63],

    63: [61, 65],

    65: [63]

}


def evaluate_weather_code(

        ml_code,
        nwp_code

):


    # exact agreement

    if ml_code == nwp_code:

        return ml_code


    # meteorologically close


    if nwp_code in NEIGHBOURS.get(

            ml_code,

            []

    ):

        return ml_code


    # disagreement


    return nwp_code
