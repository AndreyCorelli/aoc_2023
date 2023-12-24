from itertools import groupby
from typing import List


class Card:
    LABEL_ORDER = reversed("A K Q J T 9 8 7 6 5 4 3 2".split())
    LABEL_TO_ORDER = {l: i for i, l in enumerate(LABEL_ORDER)}

    def __init__(self, label):
        self.label = label
        self.strength = Card.LABEL_TO_ORDER[label]

    def __lt__(self, other):
        return self.strength < other.strength

    def __eq__(self, other):
        return self.label == other.label

    def __str__(self):
        return self.label

    def __repr__(self):
        return self.label


class Hand:
    def __init__(self, cards_str, bid):
        self.cards = [Card(label) for label in cards_str]
        self.bid = bid
        self.rank = self.calculate_rank()

    def __str__(self):
        return "".join([c.label for c in self.cards]) + " " + str(self.bid) + " " + str(self.rank)

    def __repr__(self):
        return self.__str__()

    def calculate_rank(self):
        seqs = self.longest_sequences()
        rate = self._calculate_combination_rank(seqs)

        card_rank, mult = 0, 1
        for card in reversed(self.cards):
            card_rank += mult * card.strength
            mult *= 14

        return rate * 7529536 + card_rank

    def _calculate_combination_rank(self, seqs: List[str]) -> int:
        longest = len(seqs[0])
        if longest == 5:
            return 10
        if longest == 4:
            return 9
        if longest == 3 and len(seqs[1]) == 2:
            return 8
        if longest == 3:
            return 7
        if len(seqs[0]) == 2 and len(seqs[1]) == 2:
            return 6
        if len(seqs[0]) == 2:
            return 5
        return 0

    def __lt__(self, other):
        return self.rank < other.rank

    def longest_sequences(self) -> List[str]:
        sequences = []
        sorted_cards = sorted(self.cards, key=lambda card: card.label)
        for label, group in groupby(sorted_cards, key=lambda card: card.label):
            group_list = list(group)
            sequences.append(''.join(card.label for card in group_list))
        sequences.sort(key=len, reverse=True)
        return sequences


class Game:
    def __init__(self, file_path):
        self.hands = []
        with open(file_path, 'r') as file:
            for line in file:
                cards_str, bid = line.strip().split()
                self.hands.append(Hand(cards_str, int(bid)))
        self._sort_hands()
        self.bid = self._calc_total_bid()


    def _sort_hands(self):
        self.hands.sort()

    def _calc_total_bid(self) -> int:
        total, ml = 0, 1
        for hand in self.hands:
            total += ml * hand.bid
            ml += 1
        return total


if __name__ == "__main__":
    game = Game('/Users/andreisitaev/Downloads/input_d7_1.txt')
    for hand in game.hands:
        print([card.label for card in hand.cards], hand.bid)
    print(f"Total bid: {game.bid}")
