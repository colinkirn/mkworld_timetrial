"""
Author: Cam Kirn
Assign each track a number to display in the proper order
"""

from enum import IntEnum

class Courses(IntEnum):
    Mario_Bros_Circuit = 1
    Crown_City = 2
    Whistlestop_Summit = 3
    DK_Spaceport = 4
    Desert_Hills = 5
    Shy_Guy_Bazaar = 6
    Wario_Stadium = 7
    Airship_Fortress = 8
    DK_Pass = 9
    Starview_Peak = 10
    Sky_High_Sundae = 11
    Wario_Shipyard = 12
    Koopa_Troopa_Beach = 13
    Faraway_Oasis = 14
    Peach_Stadium = 15
    Peach_Beach = 16
    Salty_Salty_Speedway = 17
    Dino_Dino_Jungle = 18
    Great_Block_Ruins = 19
    Cheep_Cheep_Falls = 20
    Dandelion_Depths = 21
    Boo_Cinema = 22
    Dry_Bones_Burnout = 23
    Moo_Moo_Meadows = 24
    Choco_Mountain = 25
    Toads_Factory = 26
    Bowsers_Castle = 27
    Acorn_Heights = 28
    Mario_Circuit = 29
    Rainbow_Road = 30

def format_course_names(course_var: str) -> str:
    """
    Author: Cam Kirn
    Convert enum member's name to proper formatting for user
    """
    if course_var == "Mario_Bros_Circuit":
        course_name = "Mario Bros. Circuit"
    elif course_var == "Sky_High_Sundae":
        course_name = "Sky-High Sundae"
    elif course_var == "Great_Block_Ruins":
        course_name = "Great ? Block Ruins"
    elif course_var == "Toads_Factory":
        course_name = "Toad's Factory"
    elif course_var == "Bowsers_Castle":
        course_name = "Bowser's Castle"
    else:
        course_name = course_var.replace('_', ' ')
    return course_name