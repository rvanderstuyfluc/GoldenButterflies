import json
import sys
import random
from typing import List, Optional, Tuple
from enum import Enum


class EventStatus(Enum):
    UNKNOWN = "unknown"
    PASS = "pass"
    FAIL = "fail"
    PARTIAL_PASS = "partial_pass"


class Statistic:
    def __init__(self, name: str, value: int = 0, description: str = "", min_value: int = 0, max_value: int = 100):
        self.name = name
        self.value = value
        self.description = description
        self.min_value = min_value
        self.max_value = max_value

    def __str__(self):
        return f"{self.name}: {self.value}"

    def modify(self, amount: int):
        self.value = max(self.min_value, min(self.max_value, self.value + amount))


class Character:
    def __init__(self, name: str = "Bob", strength_value: int = 10, intelligence_value: int = 10, stamina_value: int = 10, agility_value: int = 10):
        self.name = name
        self.is_invisible = False
        self.strength = Statistic("Strength", value=strength_value, description="Strength is a measure of physical power.")
        self.intelligence = Statistic("Intelligence", value=intelligence_value, description="Intelligence is a measure of cognitive ability.")
        self.stamina = Statistic("Stamina", value = stamina_value, description="Stamina is a measure of endurance")
        self.agility = Statistic("Agility", value = agility_value, description="Agility is a measure of nimbleness")

    def __str__(self):
        return f"Character: {self.name}, Strength: {self.strength}, Intelligence: {self.intelligence}"

    def get_stats(self):
        return [self.strength, self.intelligence, self.stamina, self.agility]  # Extend this list if there are more stats
    
total_characters = [
    Character(name="Jonathan Davis", strength_value= 50, intelligence_value=50, stamina_value=10, agility_value=10),
    Character(name="Fred Durst", strength_value=50, intelligence_value=10, stamina_value=30, agility_value=30),
    Character(name="Solana SZA", strength_value=30, intelligence_value=40, stamina_value=20, agility_value=30),
    Character(name="Soobin Choi", strength_value=20, intelligence_value=20, stamina_value=45, agility_value=35),
    Character(name="Chappell Roan", strength_value=30, intelligence_value=30, stamina_value=30, agility_value=30),
    Character(name="Sabrina Carpenter", strength_value=40, intelligence_value=20, stamina_value=30, agility_value=30),
    Character(name="Beyoncé", strength_value=30, intelligence_value=30, stamina_value=30, agility_value=30),
    Character(name="Ariana Grande", strength_value=50, intelligence_value=30, stamina_value=20, agility_value=30),
    Character(name="Theo James", strength_value=30, intelligence_value=40, stamina_value=30, agility_value=30),
    Character(name="Anne Hathaway", strength_value=20, intelligence_value=20, stamina_value=30, agility_value=50)
]

class Event:
    def __init__(self, data: dict):
        self.primary_attribute = data['primary_attribute']
        self.secondary_attribute = data['secondary_attribute']
        self.prompt_text = data['prompt_text']
        self.pass_message = data['pass']['message']
        self.fail_message = data['fail']['message']
        self.partial_pass_message = data['partial_pass']['message']
        self.status = EventStatus.UNKNOWN

    def execute(self, party: List[Character], parser):
        print(self.prompt_text)
        character = parser.select_party_member(party)
        chosen_stat = parser.select_stat(character)
        self.resolve_choice(character, chosen_stat)

    def resolve_choice(self, character: Character, chosen_stat: Statistic):
        if chosen_stat.name == self.primary_attribute:
            self.status = EventStatus.PASS
            print(self.pass_message)
        elif chosen_stat.name == self.secondary_attribute:
            self.status = EventStatus.PARTIAL_PASS
            print(self.partial_pass_message)
        else:
            self.status = EventStatus.FAIL
            print(self.fail_message)

class Location:
    def __init__(self, events: List[Event]):
        self.events = events
        self.max_events = 3 

    def get_event(self) -> Event:
        return random.choice(self.events)

    def is_completed(self, completed_events: int) -> bool:
        return completed_events >= self.max_events
    
class Game:
    def __init__(self, parser, characters: List[Character], locations: List[Location], chosen_party, opposing_team):
        self.is_invisible = None
        self.parser = parser
        self.total_characters = total_characters
        self.party = self.parser.party
        self.locations = locations
        self.continue_playing = True
        self.round_count = 0  # Track the number of rounds
        self.max_rounds = 10  # Set a limit for the game
        self.chosen_part = chosen_party
        self.opposing_team = opposing_team
        self.completed_events = 0  # Track how many events have been completed in the current location
        self.current_location = locations[0]  # Start with the first location


    def add_character_to_party(self):
        chosen_character = self.parser.make_your_party(self.total_characters)
        self.party.append(chosen_character)  # Add the selected character to the party
        print(f"{chosen_character.name} has been added to your party!")

    def display_party(self):
        print("\nYour current party members:")
        for member in self.party:
            print(f"{member.name} - Strength: {member.strength.value}, Intelligence: {member.intelligence.value}, Stamina: {member.stamina.value}, Agility: {member.agility.value}")

        print("Game Over.")

    def start(self):
        while self.continue_playing and self.round_count < self.max_rounds:
            location = random.choice(self.locations)
            event = location.get_event()

            event.execute(self.party, self.parser)
            # If the number of completed events exceeds the threshold, move to the next location
            if location.is_completed(self.completed_events):
                self.move_to_new_location()

            if self.round_count == 6:
                self.trigger_special_event()

            self.check_game_over()

            self.round_count += 1  # Increment round count
            if self.is_invisible:
                self.deactivate_invisibility()
        print("Game Over.")

    def move_to_new_location(self):
        print("\nYou have completed the required number of events. Moving to a new location...\n")
        
        # Move to the next location
        next_location = self.locations[(self.locations.index(self.current_location) + 1) % len(self.locations)]
        self.current_location = next_location
        self.completed_events = 0  # Reset the event counter for the new location
        print(f"Now at a new location! ({self.current_location})")

    def check_game_over(self):
        if self.did_succeed():
            self.continue_playing = True

        # Add a chance for a special encounter
        if random.random() < 0.2:  # 20% chance for a surprise event
            self.trigger_special_event()

        return len(self.party) == 0
    def trigger_special_event(self):
        print("\n💥 A surprise event has occurred! 💥")


        # List of traps and power-ups
        surprise_events = [
            {"description": "You stepped on a hidden trap! Lose 10 stamina.", "effect": lambda player: player.stamina.modify(-10)},
            {"description": "You find a Speed Boost potion! Gain +10 agility.", "effect": lambda player: player.agility.modify(10)},
            {"description": "A spiked pit appears! Lose 5 agility escaping it.", "effect": lambda player: player.agility.modify(-5)},
            {"description": "You find a Strength Gauntlet! Gain +15 strength.", "effect": lambda player: player.strength.modify(15)},
            {"description": "A sudden rockslide hits you! Lose 10 stamina.", "effect": lambda player: player.stamina.modify(-10)},
            {"description": "You discover an Invisibility Cloak! Sneak past obstacles next round.", "effect": lambda player: self.activate_invisibility()},
            {"description": "A lightning strike charges you up! Gain +5 strength and +5 agility.", "effect": lambda player: (player.strength.modify(5), player.agility.modify(5))},
        ]

        # Pick a random event
        selected_event = random.choice(surprise_events)

        # Print the event description
        print(f"⚡ {selected_event['description']}")

        # Apply the effect to the entire party (or you could choose just one player)
        for player in self.party:
            selected_event['effect'](player)

    def did_succeed(self):
        if self.round_count == 7:
            return True

    def activate_invisibility(self):
        self.is_invisible = True
        for member in self.party:
            member.is_invisible = True

    def deactivate_invisibility(self):
        self.is_invisible = False
        for member in self.party:
            member.is_invisible = False

class UserInputParser:
    def __init__(self, max_party_size: int):
        self.party = []
        self.max_party_size = max_party_size

    def parse(self, prompt: str) -> str:
        return input(prompt)

    def make_your_party(self, total_characters: List[Character]) -> Tuple[List[Character], List[Character]]:
        unchosen_characters = total_characters.copy()
        while len(self.party) < self.max_party_size:
            print(f"\nYour party has {len(self.party)} members. You can add {self.max_party_size - len(self.party)} more.")
            print("Choose a character to add to your party:")
            for idx, character in enumerate(total_characters):
                print(f"{idx + 1}. {character.name}")
            while True:  # Loop to ensure valid input
                try:
                    choice = int(self.parse("Enter the number of the character to add to your party: ")) - 1
                    if 0 <= choice < len(total_characters):  # Check if choice is within valid range
                        break
                    else:
                        print(f"Invalid choice. Please enter a number between 1 and {len(total_characters)}.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
            #choice = int(self.parse("Enter the number of the character to add to your party: ")) - 1
            selected_character = total_characters[choice]
            if selected_character in self.party:
                print(f"{selected_character.name} is already in your party. Please choose a different character.")
            else:
                self.party.append(total_characters[choice])
                unchosen_characters.remove(selected_character)
                print(f"{selected_character.name} has been added to your party!")
        print("\nYour party is now full!")
        opposing_team = unchosen_characters
        print("\nOpposing team consists of:")
        for character in opposing_team:
            print(f"{character.name}")

        return self.party, opposing_team
        

    def select_party_member(self, party: List[Character]) -> Character:
        print("Choose a party member:")
        for idx, member in enumerate(party):
            print(f"{idx + 1}. {member.name}")
        choice = int(self.parse("Enter the number of the chosen party member: ")) - 1
        return party[choice]

    def select_stat(self, character: Character) -> Statistic:
        print(f"Choose a stat for {character.name}:")
        stats = character.get_stats()
        for idx, stat in enumerate(stats):
            print(f"{idx + 1}. {stat.name} ({stat.value})")
        choice = int(self.parse("Enter the number of the stat to use: ")) - 1
        return stats[choice]


def load_events_from_json(file_path: str) -> List[Event]:
    with open(file_path, 'r') as file:
        data = json.load(file)
    return [Event(event_data) for event_data in data]


def start_game():
    parser = UserInputParser(max_party_size=5)
    chosen_party, opposing_team = parser.make_your_party(total_characters)
    print(f"\nYou have chosen the following characters for your party:")
    for character in chosen_party:
        print(f"{character.name} - Strength: {character.strength.value}, Intelligence: {character.intelligence.value}, Stamina: {character.stamina.value}, Agility: {character.agility.value}")

    # Load events from the JSON file
    events = load_events_from_json('project_code/location_events/location_1.json')

    locations = [Location(events)]
    game = Game(parser, total_characters, locations, chosen_party, opposing_team)
    game.start()


if __name__ == '__main__':
    start_game()
