import random


DIFFICULTIES = {
    "easy":   (1, 50,  10),
    "medium": (1, 100,  7),
    "hard":   (1, 200,  5),
}


def get_difficulty():
    while True:
        choice = input("Choose difficulty (easy / medium / hard): ").strip().lower()
        if choice in DIFFICULTIES:
            return choice
        print("Please enter 'easy', 'medium', or 'hard'.")


def play_round(difficulty):
    low, high, max_attempts = DIFFICULTIES[difficulty]
    secret = random.randint(low, high)
    attempts_used = 0

    print(f"\nI'm thinking of a number between {low} and {high}. You have {max_attempts} attempts.")

    while attempts_used < max_attempts:
        remaining = max_attempts - attempts_used
        raw = input(f"Attempts remaining: {remaining}. Your guess: ").strip()

        try:
            guess = int(raw)
        except ValueError:
            print("That's not a valid number. Try again.")
            continue

        attempts_used += 1

        if guess < secret:
            print("Too low!")
        elif guess > secret:
            print("Too high!")
        else:
            print(f"Correct! You guessed it in {attempts_used} attempt(s).")
            return True

    print(f"Out of attempts! The secret number was {secret}.")
    return False


def show_summary(name, played, won):
    win_rate = (won / played * 100) if played > 0 else 0
    print(f"\nThanks for playing, {name}!")
    print(f"Rounds played: {played}")
    print(f"Rounds won:    {won}")
    print(f"Win rate:      {win_rate:.0f}%")


def main():
    name = input("Enter your name: ").strip()
    print(f"\nWelcome, {name}! Let's play the Number Guessing Game.")

    rounds_played = 0
    rounds_won = 0

    while True:
        difficulty = get_difficulty()
        won = play_round(difficulty)
        rounds_played += 1
        if won:
            rounds_won += 1

        while True:
            again = input("\nPlay again? (y/n): ").strip().lower()
            if again in ("y", "yes"):
                break
            elif again in ("n", "no"):
                show_summary(name, rounds_played, rounds_won)
                return
            else:
                print("Please enter 'y' or 'n'.")


if __name__ == "__main__":
    main()
