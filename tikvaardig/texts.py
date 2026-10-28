"""Sentences to type. Plain language, ordinary punctuation, no tongue-twisters."""

from __future__ import annotations

import random

NL = [
    "De trein naar Utrecht vertrekt vanmiddag een kwartier later dan gepland.",
    "Mijn buurvrouw bakt elke zondag brood en de hele straat ruikt ernaar.",
    "Vergeet niet de planten water te geven voordat je op vakantie gaat.",
    "Het regende zo hard dat de straten binnen een uur blank stonden.",
    "We hebben gisteren een nieuwe kast in elkaar gezet zonder de handleiding.",
    "De kat zit al de hele ochtend voor het raam naar de vogels te kijken.",
    "Kun je even kijken of de deur op slot zit voordat we weggaan?",
    "Na het eten liepen we nog een rondje door het park langs de vijver.",
    "De bakker op de hoek verkoopt de lekkerste appeltaart van de stad.",
    "Volgende week begint de cursus en ik heb mijn boeken nog niet gekocht.",
    "Het is vandaag precies een jaar geleden dat we hier zijn komen wonen.",
    "Zet de melk terug in de koelkast, anders is hij morgen zuur.",
    "De kinderen bouwden een hut van takken en oude dekens in de tuin.",
    "Op de markt kochten we verse aardbeien en een bos gele tulpen.",
    "Mijn telefoon was bijna leeg, dus ik heb hem snel even opgeladen.",
    "Er stond een lange rij voor de ijssalon omdat het zo warm was.",
    "De vergadering duurde langer dan verwacht, maar we zijn eruit gekomen.",
    "Hij fietst elke dag twintig kilometer naar zijn werk, weer of geen weer.",
    "Het nieuwe restaurant in de binnenstad heeft een terras aan het water.",
    "Ze leest het liefst in de trein, met een kop koffie binnen handbereik.",
    "Morgen worden de dozen bezorgd, dus we moeten plek maken in de gang.",
    "De hond rende zo hard over het strand dat zijn oren omhoog waaiden.",
    "In de bibliotheek is het altijd rustig, zelfs op een zaterdagmiddag.",
    "We hebben de hele avond gepraat en niet gemerkt hoe laat het was.",
    "De lamp in de keuken knippert al een week, ik moet een nieuwe kopen.",
    "Ik heb mijn sleutels gevonden in de zak van mijn andere jas.",
    "De eerste sneeuw van het jaar viel vannacht, de daken zijn wit.",
    "Bij de kassa vroeg de man of ik een tasje nodig had.",
    "De bus stopte net op tijd, anders had ik een halfuur moeten wachten.",
    "Vanavond eten we pannenkoeken omdat de kinderen dat zo graag willen.",
]

EN = [
    "The train to the city leaves fifteen minutes later than planned this afternoon.",
    "My neighbour bakes bread every Sunday and the whole street can smell it.",
    "Don't forget to water the plants before you go on holiday next week.",
    "It rained so hard that the streets were flooded within an hour.",
    "We put together a new bookcase yesterday without reading the instructions.",
    "The cat has been sitting at the window all morning watching the birds.",
    "Could you check whether the door is locked before we leave the house?",
    "After dinner we walked around the park and along the pond one more time.",
    "The bakery on the corner sells the best apple pie in the whole town.",
    "The course starts next week and I still haven't bought the books.",
    "It is exactly one year ago today that we moved into this house.",
    "Put the milk back in the fridge or it will be sour by tomorrow.",
    "The children built a den out of branches and old blankets in the garden.",
    "At the market we bought fresh strawberries and a bunch of yellow tulips.",
    "My phone was almost dead, so I charged it quickly before leaving.",
    "There was a long queue outside the ice cream shop because it was so warm.",
    "The meeting ran longer than expected, but we reached a decision in the end.",
    "He cycles twenty kilometres to work every day, whatever the weather.",
    "The new restaurant in the old town has a terrace right by the water.",
    "She prefers reading on the train, with a cup of coffee within reach.",
    "The boxes arrive tomorrow, so we need to clear some space in the hallway.",
    "The dog ran so fast along the beach that its ears flapped in the wind.",
    "The library is always quiet, even on a busy Saturday afternoon.",
    "We talked all evening and didn't notice how late it had become.",
    "The kitchen light has been flickering for a week; I need to buy a new one.",
    "I found my keys in the pocket of my other coat after searching everywhere.",
    "The first snow of the year fell last night and the roofs are white.",
    "At the checkout the cashier asked whether I needed a bag.",
    "The bus stopped just in time, otherwise I would have waited half an hour.",
    "Tonight we are having pancakes because the children asked for them.",
]

POOLS = {"nl": NL, "en": EN}


def make_text(lang: str = "en", min_chars: int = 400, rng: random.Random | None = None) -> str:
    """Join random sentences until there is enough, without immediate repeats."""
    rng = rng or random.Random()
    pool = list(POOLS.get(lang, EN))
    rng.shuffle(pool)
    out: list[str] = []
    i = 0
    while sum(len(s) + 1 for s in out) < min_chars:
        if i >= len(pool):
            rng.shuffle(pool)
            i = 0
            if out and pool[0] == out[-1]:
                pool.append(pool.pop(0))
        out.append(pool[i])
        i += 1
    return " ".join(out)


def single(lang: str = "en", rng: random.Random | None = None) -> str:
    rng = rng or random.Random()
    return rng.choice(POOLS.get(lang, EN))
