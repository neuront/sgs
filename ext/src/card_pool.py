import random

import core.src.card as card
import ext.src.equipment.equip as equip

class CardPool:
    @staticmethod
    def create():
        cards = all_cards()
        random.shuffle(cards)
        return CardPool(cards)

    def __init__(self, cards):
        self.discarded = []
        self.cards = cards
        self.id_to_card = { c.card_id: c for c in cards }
        self.player_id_to_owning_cards = dict()

    def _recycle(self, game_control, card):
        if equip.is_equipment_region(card.region):
            card.owner_or_nil.unequip(game_control, card.region)
        self.player_id_to_owning_cards[card.owner_or_nil.player_id].remove(card)
        card.reset()

    def cards_from_top(self, cnt):
        if len(self.cards) < cnt:
            random.shuffle(self.discarded)
            self.cards.extend(self.discarded)
            self.discarded = []
        return self.cards[:cnt]

    def deal(self, player, cnt):
        self.check_player_recorded(player)
        result = self.cards_from_top(cnt)
        self.cards = self.cards[cnt:]
        for c in result: c.set_owner(player)
        for c in result: c.set_region('onhand')
        self.player_id_to_owning_cards[player.player_id].extend(result)
        return result

    def discard(self, game_control, cards):
        for c in cards: self._recycle(game_control, c)
        self.discarded.extend(cards)

    def cards_by_ids(self, cards_ids):
        return map(lambda card_id: self.id_to_card[card_id], cards_ids)

    def player_has_cards(self, player):
        return len(filter(lambda c: c.available(),
                          self.player_id_to_owning_cards[player.player_id])) > 0

    @staticmethod
    def _cards_at(region):
        if region == 'all':
            return lambda c: True
        if region in ['onhand'] + equip.ls_equipment_regions():
            return lambda c: c.region == region
        if region == 'equipment':
            return lambda c: equip.is_equipment_region(c.region)
        return lambda c: False

    def player_cards_at(self, player, region):
        return filter(lambda c: c.available() and CardPool._cards_at(region)(c),
                      self.player_id_to_owning_cards[player.player_id])

    def player_has_cards_at(self, player, region):
        return self.player_cards_count_at(player, region) > 0

    def player_cards_count_at(self, player, region):
        return len(self.player_cards_at(player, region))

    def random_pick_cards(self, player, count):
        cards = filter(lambda c: c.region == 'onhand',
                       self.player_id_to_owning_cards[player.player_id])
        random.shuffle(cards)
        return cards[:count]

    def cards_transfer(self, target, cards):
        for c in cards:
            self.player_id_to_owning_cards[c.owner_or_nil.player_id].remove(c)
            c.set_region('onhand')
            c.set_owner(target)
            c.restore()
        self.player_id_to_owning_cards[target.player_id].extend(cards)

    def recycle_cards_of_player(self, gc, player):
        cards = self.player_id_to_owning_cards[player.player_id]
        for c in cards:
            c.set_region('cardpool')
            c.set_owner(None)
            c.restore()
        self.discarded.extend(cards)

    def check_player_recorded(self, player):
        if not player.player_id in self.player_id_to_owning_cards:
            self.player_id_to_owning_cards[player.player_id] = []

def all_cards():
    class CardsGenerator:
        def __init__(self, suit):
            self.suit = suit
            self.rank = 0
            self.cards = []
            self.cid = 0

        def set_suit(self, suit):
            self.suit = suit
            return self

        def reset_rank(self):
            self.rank = 0
            return self

        def add_card(self, name):
            self.cards.append(card.Card(self.cid, name, self.rank, self.suit))
            self.rank += 1
            self.cid += 1
            return self

        def add_certain_card(self, name, rank, suit):
            self.cards.append(card.Card(self.cid, name, rank, suit))
            self.cid += 1
            return self

        def add_cards(self, names):
            for name in names: self.add_card(name)
            return self
    return CardsGenerator(card.SPADE
                          ).add_cards([
                                          '1',
                                          '2',
                                          'steal',
                                          'steal',
                                          '+jueying',
                                          '6',
                                          '7',
                                          'slash',
                                          'slash',
                                          'slash',
                                          'steal',
                                          'sabotage',
                                          '-dawan',
            ]).reset_rank().add_cards([
                                          'duel',
                                          '2',
                                          'sabotage',
                                          'sabotage',
                                          '5',
                                          '6',
                                          'slash',
                                          'slash',
                                          'slash',
                                          'slash',
                                          '11',
                                          'zhangba serpent spear',
                                          '13',
            ]).reset_rank().add_cards([
                                          '1',
                                          'rattan armor',
                                          '3',
                                          'thunder slash',
                                          'thunder slash',
                                          'thunder slash',
                                          'thunder slash',
                                          'thunder slash',
                                          '9',
                                          '10',
                                          '11',
                                          '12',
                                          '13',
            ]).set_suit(card.HEART
             ).reset_rank().add_cards([
                                          '1',
                                          'dodge',
                                          'peach',
                                          'peach',
                                          '-chitu',
                                          'peach',
                                          'peach',
                                          'peach',
                                          'peach',
                                          'slash',
                                          'slash',
                                          'peach',
                                          'dodge',
            ]).reset_rank().add_cards([
                                          '1',
                                          'dodge',
                                          '3',
                                          '4',
                                          '5',
                                          '6',
                                          '7',
                                          '8',
                                          '9',
                                          'slash',
                                          '11',
                                          'sabotage',
                                          '+zhuahuangfeidian',
            ]).reset_rank().add_cards([
                                          '1',
                                          'arson attack',
                                          'arson attack',
                                          'fire slash',
                                          'peach',
                                          'peach',
                                          'fire slash',
                                          'dodge',
                                          'dodge',
                                          'fire slash',
                                          'dodge',
                                          'dodge',
                                          '13',
            ]).set_suit(card.CLUB
             ).reset_rank().add_cards([
                                          'duel',
                                          'slash',
                                          'slash',
                                          'slash',
                                          'slash',
                                          'slash',
                                          'slash',
                                          'slash',
                                          'slash',
                                          'slash',
                                          'slash',
                                          '12',
                                          '13',
            ]).reset_rank().add_cards([
                                          '1',
                                          '2',
                                          'sabotage',
                                          'sabotage',
                                          '+dilu',
                                          '6',
                                          '7',
                                          'slash',
                                          'slash',
                                          'slash',
                                          'slash',
                                          '12',
                                          '13',
            ]).reset_rank().add_cards([
                                          '1',
                                          'rattan armor',
                                          '3',
                                          '4',
                                          'thunder slash',
                                          'thunder slash',
                                          'thunder slash',
                                          'thunder slash',
                                          '9',
                                          '10',
                                          '11',
                                          '12',
                                          '13',
            ]).set_suit(card.DIAMOND
             ).reset_rank().add_cards([
                                          'duel',
                                          'dodge',
                                          'steal',
                                          'steal',
                                          '5',
                                          'slash',
                                          'slash',
                                          'slash',
                                          'slash',
                                          'slash',
                                          'dodge',
                                          'peach',
                                          'slash',
            ]).reset_rank().add_cards([
                                          '1',
                                          'dodge',
                                          'dodge',
                                          'dodge',
                                          'dodge',
                                          'dodge',
                                          'dodge',
                                          'dodge',
                                          'dodge',
                                          'dodge',
                                          'dodge',
                                          '12',
                                          '-zixing',
            ]).reset_rank().add_cards([
                                          'vermilion feather fan',
                                          'peach',
                                          'peach',
                                          'fire slash',
                                          'fire slash',
                                          'dodge',
                                          'dodge',
                                          'dodge',
                                          '9',
                                          'dodge',
                                          'dodge',
                                          'arson attack',
                                          '+hualiu',
                                      ]).add_certain_card('2', 2, card.SPADE
                                       ).add_certain_card('Q', 12, card.HEART
                                       ).add_certain_card('2', 2, card.CLUB
                                       ).add_certain_card('Q', 12, card.DIAMOND
                                       ).cards
