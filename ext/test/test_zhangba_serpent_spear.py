from core.src.game_control import GameControl
from core.src.event import EventList
from core.src.action_stack import ActionStack
import core.src.card as card
import core.src.ret_code as ret_code
from ext.src.players_control import PlayersControl
from ext.test.fake_player import Player

from test_common import *
import test_data

pc = PlayersControl()
gc = GameControl(EventList(), test_data.CardPool(test_data.gen_cards([
    test_data.CardInfo('duel', 1, card.SPADE),
    test_data.CardInfo('zhangba serpent spear', 2, card.SPADE),
    test_data.CardInfo('slash', 3, card.DIAMOND),
    test_data.CardInfo('dodge', 4, card.DIAMOND),

    test_data.CardInfo('slash', 5, card.CLUB),
    test_data.CardInfo('sabotage', 6, card.HEART),
    test_data.CardInfo('dodge', 7, card.DIAMOND),
    test_data.CardInfo('slash', 8, card.DIAMOND),

    test_data.CardInfo('duel', 9, card.SPADE),
    test_data.CardInfo('zhangba serpent spear', 10, card.HEART),
])), pc, ActionStack())
players = [Player(91, 4), Player(1729, 4)]
map(lambda p: pc.add_player(p), players)
gc.start()

last_event_id = len(gc.get_events(players[0].token, 0)) # until getting cards

assert_eq({
    'code': ret_code.OK,
    'action': 'use',
    'card': {
        0: {
            'require': ['fix target'],
            'target count': 1,
            'targets': [1],
        },
        1: { 'require': ['implicit target'] },
        2: {
            'require': ['fix target'],
            'target count': 1,
            'targets': [1],
        },
        3: { 'require': ['forbid'] },
        8: {
            'require': ['fix target'],
            'target count': 1,
            'targets': [1],
        },
        9: { 'require': ['implicit target'] },
    },
    'abort': 'allow',
    'players': [players[0].player_id],
}, gc.hint(players[0].token))
assert_eq({
    'code': ret_code.OK,
    'action': 'use',
    'players': [players[0].player_id],
}, gc.hint(players[1].token))

result = gc.player_act({
    'token': players[0].token,
    'action': 'card',
    'use': [1],
})
assert_eq(ret_code.OK, result['code'])
p0_events = gc.get_events(players[0].token, last_event_id)
assert_eq(1, len(p0_events))
if True: # just indent for a nice appearance
    event = p0_events[0]
    assert_eq(players[0].player_id, event['player'])
    assert_eq('zhangba serpent spear', event['equip']['name'])
    assert_eq(2, event['equip']['rank'])
    assert_eq(card.SPADE, event['equip']['suit'])
    assert_eq(1, event['equip']['id'])
p1_events = gc.get_events(players[1].token, last_event_id)
assert_eq(1, len(p1_events))
if True: # just indent for a nice appearance
    event = p1_events[0]
    assert_eq(players[0].player_id, event['player'])
    assert_eq('zhangba serpent spear', event['equip']['name'])
    assert_eq(2, event['equip']['rank'])
    assert_eq(card.SPADE, event['equip']['suit'])
last_event_id += 1

# cards:
# name                  | rank (id = rank - 1) | suit

# duel                  | 1                    | SPADE   <- use this
# zhangba serpent spear | 2                    | SPADE   -- equipped
# slash                 | 3                    | DIAMOND
# dodge                 | 4                    | DIAMOND
# duel                  | 9                    | SPADE
# zhangba serpent spear | 10                   | HEART

# slash                 | 5                    | CLUB
# sabotage              | 6                    | HEART
# dodge                 | 7                    | DIAMOND
# slash                 | 8                    | DIAMOND
result = gc.player_act({
                          'token': players[0].token,
                          'action': 'duel',
                          'targets': [players[1].player_id],
                          'use': [0],
                      })
assert_eq(ret_code.OK, result['code'])

assert_eq({
    'code': ret_code.OK,
    'action': 'discard',
    'players': [players[1].player_id],
}, gc.hint(players[0].token))
assert_eq({
    'code': ret_code.OK,
    'action': 'discard',
    'methods': {
        'slash': {
            'require': ['fix card count'],
            'card count': 1,
            'cards': [4, 7],
        },
    },
    'abort': 'allow',
    'players': [players[1].player_id],
}, gc.hint(players[1].token))

# cards:
# name                  | rank (id = rank - 1) | suit

# zhangba serpent spear | 2                    | SPADE   -- equipped
# slash                 | 3                    | DIAMOND
# dodge                 | 4                    | DIAMOND
# duel                  | 9                    | SPADE
# zhangba serpent spear | 10                   | HEART

# slash                 | 5                    | CLUB    <- play this
# sabotage              | 6                    | HEART
# dodge                 | 7                    | DIAMOND
# slash                 | 8                    | DIAMOND
result = gc.player_act({
                          'token': players[1].token,
                          'method': 'slash',
                          'discard': [4],
                      })
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
                          'token': players[0].token,
                          'method': 'zhangba serpent spear',
                          'discard': [2],
                      })
assert_eq({
              'code': ret_code.BAD_REQUEST,
              'reason': ret_code.BR_WRONG_ARG % 'wrong cards',
          }, result)

result = gc.player_act({
                          'token': players[0].token,
                          'method': 'zhangba serpent spear',
                          'discard': [0, 3],
                      })
assert_eq({
              'code': ret_code.BAD_REQUEST,
              'reason': ret_code.BR_WRONG_ARG % 'not own this card',
          }, result)

result = gc.player_act({
                          'token': players[0].token,
                          'method': 'zhangba serpent spear',
                          'discard': [1, 2],
                      })
assert_eq({
              'code': ret_code.BAD_REQUEST,
              'reason': ret_code.BR_WRONG_ARG % 'wrong region',
          }, result)

assert_eq({
    'code': ret_code.OK,
    'action': 'discard',
    'methods': {
        'slash': {
            'require': ['fix card count'],
            'card count': 1,
            'cards': [2],
        },
        'zhangba serpent spear': {
            'require': ['fix card count'],
            'card count': 2,
            'cards': [2, 3, 8, 9],
        },
    },
    'abort': 'allow',
    'players': [players[0].player_id],
}, gc.hint(players[0].token))
assert_eq({
    'code': ret_code.OK,
    'action': 'discard',
    'players': [players[0].player_id],
}, gc.hint(players[1].token))

last_event_id = len(gc.get_events(players[0].token, 0)) # about to use the spear
# cards:
# name                  | rank (id = rank - 1) | suit

# zhangba serpent spear | 2                    | SPADE   -- equipped
# slash                 | 3                    | DIAMOND
# dodge                 | 4                    | DIAMOND <- play this
# duel                  | 9                    | SPADE   <-  and this
# zhangba serpent spear | 10                   | HEART

# sabotage              | 6                    | HEART
# dodge                 | 7                    | DIAMOND
# slash                 | 8                    | DIAMOND
result = gc.player_act({
                          'token': players[0].token,
                          'method': 'zhangba serpent spear',
                          'discard': [3, 8],
                      })
assert_eq(ret_code.OK, result['code'])
p0_events = gc.get_events(players[0].token, last_event_id)
assert_eq(1, len(p0_events))
if True: # just indent for a nice appearance
    event = p0_events[0]
    assert_eq(players[0].player_id, event['player'])
    assert_eq(2, len(event['play']))

    assert_eq('dodge', event['play'][0]['name'])
    assert_eq(4, event['play'][0]['rank'])
    assert_eq(card.DIAMOND, event['play'][0]['suit'])
    assert_eq(3, event['play'][0]['id'])

    assert_eq('duel', event['play'][1]['name'])
    assert_eq(9, event['play'][1]['rank'])
    assert_eq(card.SPADE, event['play'][1]['suit'])
    assert_eq(8, event['play'][1]['id'])
p1_events = gc.get_events(players[1].token, last_event_id)
assert_eq(1, len(p1_events))
if True: # just indent for a nice appearance
    event = p1_events[0]
    assert_eq(players[0].player_id, event['player'])
    assert_eq(2, len(event['play']))

    assert_eq('dodge', event['play'][0]['name'])
    assert_eq(4, event['play'][0]['rank'])
    assert_eq(card.DIAMOND, event['play'][0]['suit'])

    assert_eq('duel', event['play'][1]['name'])
    assert_eq(9, event['play'][1]['rank'])
    assert_eq(card.SPADE, event['play'][1]['suit'])
last_event_id += 1

result = gc.player_act({
                          'token': players[1].token,
                          'method': 'zhangba serpent spear',
                          'discard': [6, 7],
                      })
assert_eq({
              'code': ret_code.BAD_REQUEST,
              'reason': ret_code.BR_WRONG_ARG % 'no such method',
          }, result)

# cards:
# name                  | rank (id = rank - 1) | suit

# zhangba serpent spear | 2                    | SPADE   -- equipped
# slash                 | 3                    | DIAMOND
# zhangba serpent spear | 10                   | HEART

# sabotage              | 6                    | HEART
# dodge                 | 7                    | DIAMOND
# slash                 | 8                    | DIAMOND <- play this
result = gc.player_act({
                          'token': players[1].token,
                          'method': 'slash',
                          'discard': [7],
                      })
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
                          'token': players[0].token,
                          'method': 'slash',
                          'discard': [2, 9],
                      })
assert_eq({
              'code': ret_code.BAD_REQUEST,
              'reason': ret_code.BR_WRONG_ARG % 'wrong cards',
          }, result)

# cards:
# name                  | rank (id = rank - 1) | suit

# zhangba serpent spear | 2                    | SPADE   -- equipped
# slash                 | 3                    | DIAMOND <- play this
# zhangba serpent spear | 10                   | HEART

# sabotage              | 6                    | HEART
# dodge                 | 7                    | DIAMOND
result = gc.player_act({
                          'token': players[0].token,
                          'method': 'slash',
                          'discard': [2],
                      })
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
                          'token': players[1].token,
                          'method': 'abort',
                          'discard': [],
                      })
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
                          'token': players[0].token,
                          'action': 'card',
                          'use': [1],
                      })
assert_eq({
              'code': ret_code.BAD_REQUEST,
              'reason': ret_code.BR_WRONG_ARG % 'wrong region',
          }, result)

result = gc.player_act({
                          'token': players[0].token,
                          'action': 'card',
                          'use': [],
                      })
assert_eq({
              'code': ret_code.BAD_REQUEST,
              'reason': ret_code.BR_WRONG_ARG % 'wrong cards',
          }, result)

last_event_id = len(gc.get_events(players[0].token, 0)) # until now

# cards:
# name                  | rank (id = rank - 1) | suit

# zhangba serpent spear | 2                    | SPADE   -- lost
# zhangba serpent spear | 10                   | HEART   <- equip this

# sabotage              | 6                    | HEART
# dodge                 | 7                    | DIAMOND
result = gc.player_act({
                          'token': players[0].token,
                          'action': 'card',
                          'use': [9],
                      })
assert_eq(ret_code.OK, result['code'])

p0_events = gc.get_events(players[0].token, last_event_id)
assert_eq(2, len(p0_events))
if True: # just indent for a nice appearance
    event = p0_events[0]
    assert_eq(players[0].player_id, event['player'])
    assert_eq('weapon', event['region'])
    assert_eq('zhangba serpent spear', event['unequip']['name'])
    assert_eq(2, event['unequip']['rank'])
    assert_eq(card.SPADE, event['unequip']['suit'])

    event = p0_events[1]
    assert_eq(players[0].player_id, event['player'])
    assert_eq('zhangba serpent spear', event['equip']['name'])
    assert_eq(10, event['equip']['rank'])
    assert_eq(card.HEART, event['equip']['suit'])
    assert_eq(9, event['equip']['id'])
p1_events = gc.get_events(players[1].token, last_event_id)
assert_eq(2, len(p1_events))
if True: # just indent for a nice appearance
    assert_eq(p0_events[0], p1_events[0])

    event = p1_events[1]
    assert_eq(players[0].player_id, event['player'])
    assert_eq('zhangba serpent spear', event['equip']['name'])
    assert_eq(10, event['equip']['rank'])
    assert_eq(card.HEART, event['equip']['suit'])
last_event_id += 1

# try discarding an equipped item by sabotage
pc = PlayersControl()
gc = GameControl(EventList(), test_data.CardPool(test_data.gen_cards([
            test_data.CardInfo('duel', 1, card.SPADE),
            test_data.CardInfo('zhangba serpent spear', 2, card.SPADE),
            test_data.CardInfo('slash', 3, card.DIAMOND),
            test_data.CardInfo('dodge', 4, card.DIAMOND),

            test_data.CardInfo('slash', 5, card.CLUB),
            test_data.CardInfo('sabotage', 6, card.HEART),
            test_data.CardInfo('sabotage', 7, card.DIAMOND),
            test_data.CardInfo('slash', 8, card.DIAMOND),

            test_data.CardInfo('duel', 9, card.SPADE),
            test_data.CardInfo('zhangba serpent spear', 10, card.HEART),

            test_data.CardInfo('duel', 11, card.DIAMOND),
            test_data.CardInfo('duel', 12, card.HEART),
     ])), pc, ActionStack())
players = [Player(91, 4), Player(1729, 4)]
map(lambda p: pc.add_player(p), players)
gc.start()

result = gc.player_act({
                          'token': players[0].token,
                          'action': 'card',
                          'use': [1],
                      })
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
                          'token': players[0].token,
                          'action': 'abort',
                      })
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
                          'token': players[0].token,
                          'discard': [1],
                      })
assert_eq({
              'code': ret_code.BAD_REQUEST,
              'reason': ret_code.BR_WRONG_ARG % 'wrong region',
          }, result)

# cards:
# name                  | rank (id = rank - 1) | suit

# duel                  | 1                    | SPADE   <- discard this
# zhangba serpent spear | 2                    | SPADE   -- equipped
# slash                 | 3                    | DIAMOND
# dodge                 | 4                    | DIAMOND
# duel                  | 9                    | SPADE
# zhangba serpent spear | 10                   | HEART

# slash                 | 5                    | CLUB
# sabotage              | 6                    | HEART
# sabotage              | 7                    | DIAMOND
# slash                 | 8                    | DIAMOND
result = gc.player_act({
                          'token': players[0].token,
                          'discard': [0],
                      })
assert_eq(ret_code.OK, result['code'])

# cards:
# name                  | rank (id = rank - 1) | suit

# zhangba serpent spear | 2                    | SPADE   -- equipped
# slash                 | 3                    | DIAMOND
# dodge                 | 4                    | DIAMOND
# duel                  | 9                    | SPADE
# zhangba serpent spear | 10                   | HEART

# slash                 | 5                    | CLUB
# sabotage              | 6                    | HEART
# sabotage              | 7                    | DIAMOND
# slash                 | 8                    | DIAMOND
# duel                  | 11                   | DIAMOND <- draw this and use it
# duel                  | 12                   | HEART   <- draw this
result = gc.player_act({
                          'token': players[1].token,
                          'action': 'duel',
                          'targets': [players[0].player_id],
                          'use': [10],
                      })
assert_eq(ret_code.OK, result['code'])

# cards:
# name                  | rank (id = rank - 1) | suit

# zhangba serpent spear | 2                    | SPADE   -- equipped
# slash                 | 3                    | DIAMOND
# dodge                 | 4                    | DIAMOND <- play this
# zhangba serpent spear | 10                   | HEART   <-  and this

# slash                 | 5                    | CLUB
# sabotage              | 6                    | HEART
# sabotage              | 7                    | DIAMOND
# slash                 | 8                    | DIAMOND
# duel                  | 12                   | HEART
result = gc.player_act({
                          'token': players[0].token,
                          'method': 'zhangba serpent spear',
                          'discard': [3, 9],
                      })
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
                          'token': players[1].token,
                          'method': 'abort',
                          'discard': [],
                      })
assert_eq(ret_code.OK, result['code'])

# cards:
# name                  | rank (id = rank - 1) | suit

# zhangba serpent spear | 2                    | SPADE   -- equipped
# slash                 | 3                    | DIAMOND

# slash                 | 5                    | CLUB
# sabotage              | 6                    | HEART   <- use this
# sabotage              | 7                    | DIAMOND
# slash                 | 8                    | DIAMOND
# duel                  | 12                   | HEART
result = gc.player_act({
                          'token': players[1].token,
                          'action': 'sabotage',
                          'targets': [players[0].player_id],
                          'use': [5],
                      })
assert_eq(ret_code.OK, result['code'])

last_event_id = len(gc.get_events(players[0].token, 0)) # about to sabotage
result = gc.player_act({
                          'token': players[1].token,
                          'region': 'weapon',
                      })
assert_eq(ret_code.OK, result['code'])

p0_events = gc.get_events(players[0].token, last_event_id)
assert_eq(1, len(p0_events))
if True: # just indent for a nice appearance
    event = p0_events[0]
    assert_eq(players[0].player_id, event['player'])
    assert_eq('weapon', event['region'])
    assert_eq('zhangba serpent spear', event['unequip']['name'])
    assert_eq(2, event['unequip']['rank'])
    assert_eq(card.SPADE, event['unequip']['suit'])
p1_events = gc.get_events(players[1].token, last_event_id)
assert_eq(p0_events, p1_events)

# cards:
# name                  | rank (id = rank - 1) | suit

# slash                 | 3                    | DIAMOND

# slash                 | 5                    | CLUB
# sabotage              | 7                    | DIAMOND
# slash                 | 8                    | DIAMOND
# duel                  | 12                   | HEART   <- use this
result = gc.player_act({
                          'token': players[1].token,
                          'action': 'duel',
                          'targets': [players[0].player_id],
                          'use': [11],
                      })
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
                          'token': players[0].token,
                          'method': 'zhangba serpent spear',
                          'discard': [],
                      })
assert_eq({
              'code': ret_code.BAD_REQUEST,
              'reason': ret_code.BR_WRONG_ARG % 'no such method',
          }, result)

result = gc.player_act({
                          'token': players[0].token,
                          'method': 'slash',
                          'discard': [2],
                      })
assert_eq(ret_code.OK, result['code'])

# extend slash range and slash

pc = PlayersControl()
gc = GameControl(EventList(), test_data.CardPool(test_data.gen_cards([
    test_data.CardInfo('slash', 1, card.SPADE),
    test_data.CardInfo('zhangba serpent spear', 12, card.SPADE),
    test_data.CardInfo('dodge', 3, card.DIAMOND),
    test_data.CardInfo('dodge', 4, card.SPADE),

    test_data.CardInfo('dodge', 5, card.HEART),
    test_data.CardInfo('dodge', 6, card.HEART),
    test_data.CardInfo('dodge', 7, card.DIAMOND),
    test_data.CardInfo('dodge', 8, card.DIAMOND),

    test_data.CardInfo('dodge', 9, card.HEART),
    test_data.CardInfo('dodge', 10, card.HEART),
    test_data.CardInfo('dodge', 11, card.DIAMOND),
    test_data.CardInfo('dodge', 12, card.DIAMOND),

    test_data.CardInfo('dodge', 13, card.HEART),
    test_data.CardInfo('dodge', 1, card.HEART),
    test_data.CardInfo('dodge', 2, card.DIAMOND),
    test_data.CardInfo('dodge', 3, card.DIAMOND),

    test_data.CardInfo('dodge', 4, card.HEART),
    test_data.CardInfo('dodge', 5, card.HEART),
])), pc, ActionStack())
players = [Player(2, 4), Player(19, 4), Player(91, 4), Player(1729, 4)]
map(lambda p: pc.add_player(p), players)
gc.start()

assert_eq({
    'code': ret_code.OK,
    'action': 'use',
    'card': {
        0: {
            'require': ['fix target'],
            'target count': 1,
            'targets': [1, 3],
        },
        1: { 'require': ['implicit target'] },
        2: { 'require': ['forbid'] },
        3: { 'require': ['forbid'] },
        16: { 'require': ['forbid'] },
        17: { 'require': ['forbid'] },
    },
    'abort': 'allow',
    'players': [players[0].player_id],
}, gc.hint(players[0].token))

result = gc.player_act({
    'token': players[0].token,
    'action': 'card',
    'targets': [players[2].player_id],
    'use': [0],
})
assert_eq({
    'code': ret_code.BAD_REQUEST,
    'reason': ret_code.BR_WRONG_ARG % 'out of range',
}, result)

result = gc.player_act({
    'token': players[0].token,
    'action': 'card',
    'use': [1],
})
assert_eq(ret_code.OK, result['code'])

assert_eq({
    'code': ret_code.OK,
    'action': 'use',
    'card': {
        0: {
            'require': ['fix target'],
            'target count': 1,
            'targets': [1, 2, 3],
        },
        2: { 'require': ['forbid'] },
        3: { 'require': ['forbid'] },
        16: { 'require': ['forbid'] },
        17: { 'require': ['forbid'] },
    },
    'methods': {
        'zhangba serpent spear': {
            'require': ['fix card count', 'fix target'],
            'cards': [0, 2, 3, 16, 17],
            'card count': 2,
            'targets': [1, 2, 3],
            'target count': 1,
        },
    },
    'abort': 'allow',
    'players': [players[0].player_id],
}, gc.hint(players[0].token))

result = gc.player_act({
    'token': players[0].token,
    'action': 'card',
    'targets': [players[2].player_id],
    'use': [0],
})
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
    'token': players[2].token,
    'method': 'dodge',
    'discard': [8],
})
assert_eq(ret_code.OK, result['code'])

assert_eq({
    'code': ret_code.OK,
    'action': 'use',
    'card': {
        2: { 'require': ['forbid'] },
        3: { 'require': ['forbid'] },
        16: { 'require': ['forbid'] },
        17: { 'require': ['forbid'] },
    },
    'abort': 'allow',
    'players': [players[0].player_id],
}, gc.hint(players[0].token))

result = gc.player_act({
    'token': players[0].token,
    'action': 'zhangba serpent spear',
    'targets': [players[1].player_id],
    'use': [16, 17],
})
assert_eq({
    'code': ret_code.BAD_REQUEST,
    'reason': ret_code.BR_INCORRECT_INTERFACE,
}, result)

# forbid slash after spear

pc = PlayersControl()
gc = GameControl(EventList(), test_data.CardPool(test_data.gen_cards([
    test_data.CardInfo('slash', 1, card.SPADE),
    test_data.CardInfo('zhangba serpent spear', 12, card.SPADE),
    test_data.CardInfo('dodge', 3, card.DIAMOND),
    test_data.CardInfo('dodge', 4, card.HEART),

    test_data.CardInfo('dodge', 5, card.HEART),
    test_data.CardInfo('dodge', 6, card.HEART),
    test_data.CardInfo('dodge', 7, card.DIAMOND),
    test_data.CardInfo('dodge', 8, card.DIAMOND),

    test_data.CardInfo('dodge', 9, card.HEART),
    test_data.CardInfo('dodge', 10, card.HEART),
])), pc, ActionStack())
players = [Player(2, 4), Player(19, 4)]
map(lambda p: pc.add_player(p), players)
gc.start()

result = gc.player_act({
    'token': players[0].token,
    'action': 'card',
    'use': [1],
})
assert_eq(ret_code.OK, result['code'])

assert_eq({
    'code': ret_code.OK,
    'action': 'use',
    'card': {
        0: {
            'require': ['fix target'],
            'target count': 1,
            'targets': [1],
        },
        2: { 'require': ['forbid'] },
        3: { 'require': ['forbid'] },
        8: { 'require': ['forbid'] },
        9: { 'require': ['forbid'] },
    },
    'methods': {
        'zhangba serpent spear': {
            'require': ['fix card count', 'fix target'],
            'cards': [0, 2, 3, 8, 9],
            'card count': 2,
            'targets': [1],
            'target count': 1,
        },
    },
    'abort': 'allow',
    'players': [players[0].player_id],
}, gc.hint(players[0].token))

last_event_id = len(gc.get_events(players[0].token, 0)) # until equip spear

result = gc.player_act({
    'token': players[0].token,
    'action': 'zhangba serpent spear',
    'targets': [players[1].player_id],
    'use': [2, 3],
})
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
    'token': players[1].token,
    'method': 'dodge',
    'discard': [4],
})
assert_eq(ret_code.OK, result['code'])

p0_events = gc.get_events(players[0].token, last_event_id)
assert_eq(3, len(p0_events))
if True: # just indent for a nice appearance
    event = p0_events[0]
    assert_eq(players[0].player_id, event['user'])
    assert_eq(1, len(event['targets']))
    assert_eq(players[1].player_id, event['targets'][0])
    assert_eq('slash', event['action'])
    assert_eq(2, len(event['use']))
    c = event['use'][0]
    assert_eq('dodge', c['name'])
    assert_eq(3, c['rank'])
    assert_eq(card.DIAMOND, c['suit'])
    assert_eq(2, c['id'])
    c = event['use'][1]
    assert_eq('dodge', c['name'])
    assert_eq(4, c['rank'])
    assert_eq(card.HEART, c['suit'])
    assert_eq(3, c['id'])
    event = p0_events[1]
    assert_eq('Invocation', event['type'])
    assert_eq(players[0].player_id, event['player'])
    assert_eq('zhangba serpent spear', event['invoke'])
    event = p0_events[2]
    assert_eq(players[1].player_id, event['player'])
    assert_eq(1, len(event['play']))
    assert_eq('dodge', event['play'][0]['name'])
    assert_eq(5, event['play'][0]['rank'])
    assert_eq(card.HEART, event['play'][0]['suit'])
p1_events = gc.get_events(players[1].token, last_event_id)
assert_eq(3, len(p1_events))
if True: # just indent for a nice appearance
    event = p1_events[0]
    assert_eq(players[0].player_id, event['user'])
    assert_eq(1, len(event['targets']))
    assert_eq(players[1].player_id, event['targets'][0])
    assert_eq('slash', event['action'])
    assert_eq(2, len(event['use']))
    c = event['use'][0]
    assert_eq('dodge', c['name'])
    assert_eq(3, c['rank'])
    assert_eq(card.DIAMOND, c['suit'])
    c = event['use'][1]
    assert_eq('dodge', c['name'])
    assert_eq(4, c['rank'])
    assert_eq(card.HEART, c['suit'])
    assert_eq(p0_events[1], p1_events[1])
    event = p1_events[2]
    assert_eq(players[1].player_id, event['player'])
    assert_eq(1, len(event['play']))
    assert_eq('dodge', event['play'][0]['name'])
    assert_eq(5, event['play'][0]['rank'])
    assert_eq(card.HEART, event['play'][0]['suit'])
    assert_eq(4, event['play'][0]['id'])

result = gc.player_act({
    'token': players[0].token,
    'action': 'zhangba serpent spear',
    'targets': [players[1].player_id],
    'use': [8, 9],
})
assert_eq({
    'code': ret_code.BAD_REQUEST,
    'reason': ret_code.BR_INCORRECT_INTERFACE,
}, result)

result = gc.player_act({
    'token': players[0].token,
    'action': 'card',
    'targets': [players[1].player_id],
    'use': [0],
})
assert_eq({
    'code': ret_code.BAD_REQUEST,
    'reason': ret_code.BR_INCORRECT_INTERFACE,
}, result)

# unequip

pc = PlayersControl()
gc = GameControl(EventList(), test_data.CardPool(test_data.gen_cards([
    test_data.CardInfo('slash', 1, card.SPADE),
    test_data.CardInfo('zhangba serpent spear', 12, card.SPADE),
    test_data.CardInfo('dodge', 3, card.DIAMOND),
    test_data.CardInfo('dodge', 4, card.HEART),

    test_data.CardInfo('+jueying', 5, card.SPADE),
    test_data.CardInfo('sabotage', 6, card.SPADE),
    test_data.CardInfo('dodge', 7, card.DIAMOND),
    test_data.CardInfo('dodge', 8, card.DIAMOND),

    test_data.CardInfo('dodge', 9, card.HEART),
    test_data.CardInfo('dodge', 10, card.HEART),

    test_data.CardInfo('dodge', 11, card.HEART),
    test_data.CardInfo('dodge', 12, card.HEART),

    test_data.CardInfo('dodge', 13, card.HEART),
    test_data.CardInfo('dodge', 1, card.HEART),
])), pc, ActionStack())
players = [Player(2, 8), Player(19, 8)]
map(lambda p: pc.add_player(p), players)
gc.start()

result = gc.player_act({
    'token': players[0].token,
    'action': 'card',
    'use': [1],
})
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
    'token': players[0].token,
    'action': 'abort',
})
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
    'token': players[1].token,
    'action': 'card',
    'use': [4],
})
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
    'token': players[1].token,
    'action': 'card',
    'use': [5],
    'targets': [players[0].player_id],
})
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
    'token': players[1].token,
    'region': 'weapon',
})
assert_eq(ret_code.OK, result['code'])

result = gc.player_act({
    'token': players[1].token,
    'action': 'abort',
})
assert_eq(ret_code.OK, result['code'])

assert_eq({
    'code': ret_code.OK,
    'action': 'use',
    'card': {
        0: { 'require': ['forbid'] },
        2: { 'require': ['forbid'] },
        3: { 'require': ['forbid'] },
        8: { 'require': ['forbid'] },
        9: { 'require': ['forbid'] },
        12: { 'require': ['forbid'] },
        13: { 'require': ['forbid'] },
    },
    'abort': 'allow',
    'players': [players[0].player_id],
}, gc.hint(players[0].token))
