SIGN_LANGUAGE_GLOSSARY = {
    "hello": "Wave hand with palm facing outward",
    "thank you": "Touch chin with fingertips and move hand forward",
    "yes": "Make a fist and nod it up and down like a head nod",
    "no": "Tap thumb with first two fingers",
    "please": "Rub chest in circular motion with flat hand",
    "sorry": "Make a fist and rub it in a circular motion on chest",
    "help": "Thumbs up on flat palm, lift both hands up",
    "water": "W handshape taps chin",
    "eat": "Fingertips of flat hand tap mouth",
    "good": "Flat hand starts at chin and moves down to chest",
}


def lookup_sign(term: str) -> str:
    return SIGN_LANGUAGE_GLOSSARY.get(term.lower(), f"No sign found for '{term}'")


def get_all_signs() -> dict:
    return SIGN_LANGUAGE_GLOSSARY


FAQ = {
    "Where are the nearest restrooms?": "Restrooms are located at the north and south ends of the concourse, near Sections 101 and 210.",
    "Where can I find food stalls?": "Food stalls are on the lower concourse between Sections 104 and 108, and Sections 205 and 209.",
    "How do I exit the stadium?": "Use the nearest marked emergency exit. Main exits are at the west and east gates.",
    "Where can I get medical help?": "Medical stations are at Sections 112, 203, and near Gate C.",
    "Is there a prayer room?": "Yes, a multi-faith prayer room is located near Gate B on the lower level.",
    "Where is the lost and found?": "Lost and found is at the Guest Services desk near the main entrance.",
    "Is there free wifi in the stadium?": "Free wifi is available throughout the stadium. Connect to 'StadiumGuest'.",
    "Who can help with ticket issues?": "Visit the Ticket Help desk near Gate A or call the number on your ticket.",
    "Is the stadium wheelchair accessible?": "Yes, there are ramps, elevators, and dedicated seating areas. Ask staff for assistance.",
    "What time does the stadium open?": "The stadium opens two hours before kickoff. Check your ticket for exact gates.",
    "Are outside food and drinks allowed?": "No, outside food and drinks are not permitted except for baby formula or medical needs.",
    "Where can I buy merchandise?": "Official merchandise stores are on the upper and lower concourses near Sections 105 and 207.",
    "What should I do if I lose my child?": "Alert the nearest staff member or go to Guest Services near the main entrance immediately.",
    "How can I report a safety concern?": "Speak to any staff member or call the stadium hotline posted on your seat.",
}
