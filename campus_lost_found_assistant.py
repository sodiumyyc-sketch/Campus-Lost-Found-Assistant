import json
import os
from datetime import datetime


DATA_FILE = "lost_found_data.json"


class Item:
    """
    This class represents one lost or found item.
    Each item stores information such as name, category, location, date, and description.
    """

    def __init__(self, item_id, item_type, name, category, location, date, description, returned=False):
        self.item_id = item_id
        self.item_type = item_type
        self.name = name
        self.category = category
        self.location = location
        self.date = date
        self.description = description
        self.returned = returned

    def to_dict(self):
        """
        Convert an Item object into a dictionary so it can be saved into a JSON file.
        """
        return {
            "item_id": self.item_id,
            "item_type": self.item_type,
            "name": self.name,
            "category": self.category,
            "location": self.location,
            "date": self.date,
            "description": self.description,
            "returned": self.returned
        }

    @staticmethod
    def from_dict(data):
        """
        Convert a dictionary loaded from the JSON file back into an Item object.
        """
        return Item(
            data["item_id"],
            data["item_type"],
            data["name"],
            data["category"],
            data["location"],
            data["date"],
            data["description"],
            data["returned"]
        )


class LostFoundSystem:
    """
    This class controls the whole lost and found system.
    It stores item records, saves data, loads data, and manages menu functions.
    """

    def __init__(self):
        self.items = []
        self.load_data()

    def load_data(self):
        """
        Load item data from a JSON file.
        If the file does not exist, the program starts with an empty list.
        """
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    self.items = [Item.from_dict(item_data) for item_data in data]
            except json.JSONDecodeError:
                print("Warning: Data file is damaged. Starting with empty data.")
                self.items = []
        else:
            self.items = []

    def save_data(self):
        """
        Save all item records into a JSON file.
        """
        data = [item.to_dict() for item in self.items]

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def get_next_id(self):
        """
        Generate the next item ID.
        """
        if len(self.items) == 0:
            return 1

        highest_id = max(item.item_id for item in self.items)
        return highest_id + 1

    def validate_date(self, date_text):
        """
        Check whether the date format is valid.
        The required format is YYYY-MM-DD.
        """
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def get_item_input(self, item_type):
        """
        Ask the user to enter item details.
        This function is used for both lost items and found items.
        """
        print()
        print(f"--- Report a {item_type} item ---")

        name = input("Item name: ").strip()
        category = input("Category, for example Electronics, Card, Keys, Clothes: ").strip()
        location = input("Location, for example Library, Cafeteria, Classroom: ").strip()

        while True:
            date = input("Date, format YYYY-MM-DD: ").strip()

            if self.validate_date(date):
                break
            else:
                print("Invalid date format. Please enter the date like 2026-05-24.")

        description = input("Short description: ").strip()

        if name == "":
            name = "Unknown item"

        if category == "":
            category = "Unknown category"

        if location == "":
            location = "Unknown location"

        if description == "":
            description = "No description provided"

        new_item = Item(
            self.get_next_id(),
            item_type,
            name,
            category,
            location,
            date,
            description
        )

        self.items.append(new_item)
        self.save_data()

        print()
        print(f"{item_type.capitalize()} item has been added successfully.")
        print(f"Item ID: {new_item.item_id}")

    def report_lost_item(self):
        """
        Add a lost item record.
        """
        self.get_item_input("lost")

    def report_found_item(self):
        """
        Add a found item record.
        """
        self.get_item_input("found")

    def view_items(self, item_type):
        """
        Display all lost or found items that have not been returned.
        """
        print()
        print(f"--- {item_type.capitalize()} Items ---")

        filtered_items = [
            item for item in self.items
            if item.item_type == item_type and not item.returned
        ]

        if len(filtered_items) == 0:
            print(f"No active {item_type} items found.")
            return

        for item in filtered_items:
            self.display_item(item)

    def display_item(self, item):
        """
        Display one item in a clear format.
        """
        print()
        print(f"ID: {item.item_id}")
        print(f"Type: {item.item_type.capitalize()}")
        print(f"Name: {item.name}")
        print(f"Category: {item.category}")
        print(f"Location: {item.location}")
        print(f"Date: {item.date}")
        print(f"Description: {item.description}")
        print(f"Returned: {'Yes' if item.returned else 'No'}")

    def calculate_match_score(self, lost_item, found_item):
        """
        Calculate a match score between one lost item and one found item.
        A higher score means the two items are more likely to match.
        """
        score = 0

        if lost_item.category.lower() == found_item.category.lower():
            score += 3

        if lost_item.location.lower() == found_item.location.lower():
            score += 3

        if lost_item.date == found_item.date:
            score += 2

        lost_words = set((lost_item.name + " " + lost_item.description).lower().split())
        found_words = set((found_item.name + " " + found_item.description).lower().split())

        common_words = lost_words.intersection(found_words)
        score += len(common_words)

        return score

    def search_possible_matches(self):
        """
        Search possible matches between lost items and found items.
        """
        print()
        print("--- Possible Matches ---")

        lost_items = [
            item for item in self.items
            if item.item_type == "lost" and not item.returned
        ]

        found_items = [
            item for item in self.items
            if item.item_type == "found" and not item.returned
        ]

        if len(lost_items) == 0 or len(found_items) == 0:
            print("There are not enough lost and found records to compare.")
            return

        matches_found = False

        for lost_item in lost_items:
            for found_item in found_items:
                score = self.calculate_match_score(lost_item, found_item)

                if score >= 4:
                    matches_found = True

                    print()
                    print("Possible match found!")
                    print(f"Match score: {score}")
                    print()
                    print("Lost item:")
                    self.display_item(lost_item)
                    print()
                    print("Found item:")
                    self.display_item(found_item)
                    print("-" * 40)

        if not matches_found:
            print("No strong possible matches found.")

    def mark_item_as_returned(self):
        """
        Mark an item as returned by using its item ID.
        """
        print()
        print("--- Mark Item as Returned ---")

        try:
            item_id = int(input("Enter the item ID to mark as returned: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        for item in self.items:
            if item.item_id == item_id:
                if item.returned:
                    print("This item is already marked as returned.")
                else:
                    item.returned = True
                    self.save_data()
                    print("Item has been marked as returned successfully.")
                return

        print("Item ID not found.")

    def view_returned_items(self):
        """
        Display all returned items.
        """
        print()
        print("--- Returned Items ---")

        returned_items = [item for item in self.items if item.returned]

        if len(returned_items) == 0:
            print("No returned items yet.")
            return

        for item in returned_items:
            self.display_item(item)

    def show_menu(self):
        """
        Display the main menu.
        """
        print()
        print("=" * 45)
        print("Campus Lost & Found Assistant")
        print("=" * 45)
        print("1. Report a lost item")
        print("2. Report a found item")
        print("3. View lost items")
        print("4. View found items")
        print("5. Search possible matches")
        print("6. Mark an item as returned")
        print("7. View returned items")
        print("8. Save and exit")

    def run(self):
        """
        Run the main program loop.
        """
        while True:
            self.show_menu()
            choice = input("Choose an option from 1 to 8: ").strip()

            if choice == "1":
                self.report_lost_item()
            elif choice == "2":
                self.report_found_item()
            elif choice == "3":
                self.view_items("lost")
            elif choice == "4":
                self.view_items("found")
            elif choice == "5":
                self.search_possible_matches()
            elif choice == "6":
                self.mark_item_as_returned()
            elif choice == "7":
                self.view_returned_items()
            elif choice == "8":
                self.save_data()
                print("Data saved. Thank you for using Campus Lost & Found Assistant.")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 8.")


def main():
    """
    Start the program.
    """
    app = LostFoundSystem()
    app.run()


if __name__ == "__main__":
    main()