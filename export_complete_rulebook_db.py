import fitz
import re
import json

PDF_PATH = '/Users/ethanelbard/Library/Mobile Documents/com~apple~CloudDocs/TTRPGs/Cosmere/Stormlight/SL001_Stormlight_Handbook_digital.pdf'
doc = fitz.open(PDF_PATH)

def clean_str(s):
    if not s: return ""
    s = s.replace('\xad', '')
    s = s.replace('’', "'").replace('‘', "'")
    s = s.replace('“', '"').replace('”', '"')
    s = s.replace('—', '—').replace('–', '-')
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def make_id(name):
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', name).strip().lower()
    return re.sub(r'[\s_]+', '-', clean)

def parse_focus_cost(text):
    m = re.search(r'spend (\d+) focus', text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    if 'spend 1 focus' in text.lower() or 'costs 1 focus' in text.lower():
        return 1
    return 0

def parse_investiture_cost(text):
    m = re.search(r'spend (\d+) investiture', text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    if 'spend 1 investiture' in text.lower() or 'spend 1 or more investiture' in text.lower():
        return 1
    return 0

def parse_activation(desc, prereq, tname):
    # Determine activation from rules text
    d = desc.lower()
    if 'when you acquire this talent' in d or 'your max' in d or 'gain +1' in d or 'increase your' in d or 'to resist your influence' in d or 'gain an advantage' in d and 'spend' not in d and 'as a reaction' not in d:
        return 'Passive'
    if 'as a reaction' in d or 'reaction' in d[:50]:
        return 'Reaction'
    if 'free action' in d:
        return 'Free Action'
    if '2 actions' in d or 'spend 2 actions' in d:
        return '2 Actions'
    if '3 actions' in d:
        return '3 Actions'
    if '1 action' in d or 'action' in d[:40] or 'make an attack' in d or 'make a test' in d:
        return 'Action'
    if 'spend' in d and 'focus' in d:
        return 'Special'
    if 'once per' in d or 'after you' in d or 'when you' in d:
        return 'Special'
    return 'Passive'

# HEROIC PATHS CONFIGURATION
HEROIC_PATHS = {
    'agent': {
        'name': 'Agent',
        'icon': '🗡️',
        'desc': 'Artists of duplicity and sabotage who unravel enemy plans with clever ruses and swift movements.',
        'starting_skill': 'Insight',
        'key_name': 'Opportunist (Agent Key)',
        'key_page': 79,
        'pages_desc': [82, 83, 84, 85],
        'pages_tree': [80, 81],
        'specialties': {
            'Investigator': {
                'desc': 'Uncovers clues, interrogates suspects, and solves mysteries.',
                'order': ['Watchful Eye', 'Get ’Em Talking', 'Quick Analysis', 'Baleful', 'Gather Evidence', 'Hardy', 'Sleuth’s Instincts', 'Close the Case'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Watchful Eye', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Get ’Em Talking', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Quick Analysis', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Baleful', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Gather Evidence', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Hardy', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Sleuth’s Instincts', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Close the Case', 'tier': 4}
                ]
            },
            'Spy': {
                'desc': 'Infiltrates enemy organizations with false identities and subtle takedowns.',
                'order': ['Sure Outcome', 'Plausible Excuse', 'Collected', 'Cover Story', 'Subtle Takedown', 'Mighty', 'Mercurial Facade', 'High Society Contacts'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Sure Outcome', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Plausible Excuse', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Collected', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Cover Story', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Subtle Takedown', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Mighty', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Mercurial Facade', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'High Society Contacts', 'tier': 4}
                ]
            },
            'Thief': {
                'desc': 'Masters of stealth, misdirection, pickpocketing, and urban agility.',
                'order': ['Risky Behavior', 'Cheap Shot', 'Double Down', 'Surefooted', 'Underworld Contacts', 'Shadow Step', 'Fast Talker', 'Trickster’s Hand'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Risky Behavior', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Cheap Shot', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Double Down', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Surefooted', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Underworld Contacts', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Shadow Step', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Fast Talker', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Trickster’s Hand', 'tier': 4}
                ]
            }
        }
    },
    'envoy': {
        'name': 'Envoy',
        'icon': '👑',
        'desc': 'Diplomats, religious leaders, and teachers who inspire allies and negotiate peace.',
        'starting_skill': 'Discipline',
        'key_name': 'Rousing Presence (Envoy Key)',
        'key_page': 87,
        'pages_desc': [90, 91, 92, 93],
        'pages_tree': [88, 89],
        'specialties': {
            'Diplomat': {
                'desc': 'Diffuses tensions, leverages etiquette, and cuts through deception.',
                'order': ['Steadfast Challenge', 'Collected', 'Withering Retort', 'Well Dressed', 'Calm Appeal', 'High Society Contacts', 'Peaceful Solution', 'Practiced Oratory'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Steadfast Challenge', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Collected', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Withering Retort', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Well Dressed', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Calm Appeal', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'High Society Contacts', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Peaceful Solution', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Practiced Oratory', 'tier': 4}
                ]
            },
            'Faithful': {
                'desc': 'Devoted adherents who galvanize crowds and offer sage spiritual counsel.',
                'order': ['Customary Garb', 'Galvanize', 'Devoted Presence', 'Composed', 'Stalwart Presence', 'Applied Motivation', 'Sage Counsel', 'Inspired Zeal'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Customary Garb', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Galvanize', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Devoted Presence', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Composed', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Stalwart Presence', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Applied Motivation', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Sage Counsel', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Inspired Zeal', 'tier': 4}
                ]
            },
            'Mentor': {
                'desc': 'Experienced teachers who guide pupils, instill confidence, and lead through demonstration.',
                'order': ['Sound Advice', 'Practical Demonstration', 'Lessons in Patience', 'Mighty', 'Instill Confidence', 'Guiding Oration', 'Foresight', 'Rallying Shout'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Sound Advice', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Practical Demonstration', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Lessons in Patience', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Mighty', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Instill Confidence', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Guiding Oration', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Foresight', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Rallying Shout', 'tier': 4}
                ]
            }
        }
    },
    'hunter': {
        'name': 'Hunter',
        'icon': '🏹',
        'desc': 'Wilderness trackers, deadly archers, and silent assassins.',
        'starting_skill': 'Perception',
        'key_name': 'Seek Quarry (Hunter Key)',
        'key_page': 95,
        'pages_desc': [98, 99, 100, 101],
        'pages_tree': [96, 97],
        'specialties': {
            'Archer': {
                'desc': 'Masters of ranged combat who pick off targets from vast distances.',
                'order': ['Tagging Shot', 'Combat Training', 'Sharp Eye', 'Steady Aim', 'Exploit Weakness', 'Hardy', 'Unrelenting Salvo', 'Backstep'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Tagging Shot', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Combat Training', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Sharp Eye', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Steady Aim', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Exploit Weakness', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Hardy', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Unrelenting Salvo', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Backstep', 'tier': 4}
                ]
            },
            'Assassin': {
                'desc': 'Lethal stalkers who strike from shadow with precision and fatal force.',
                'order': ['Startling Blow', 'Killing Edge', 'Fatal Thrust', 'Shadowing', 'Swift Strikes', 'Cold Eyes', 'Sidestep', 'Mighty'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Startling Blow', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Killing Edge', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Fatal Thrust', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Shadowing', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Swift Strikes', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Cold Eyes', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Sidestep', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Mighty', 'tier': 4}
                ]
            },
            'Tracker': {
                'desc': 'Expert guides and trappers who bond with beast companions.',
                'order': ['Hunter’s Edge', 'Animal Bond', 'Experienced Trapper', 'Pack Hunting', 'Deadly Trap', 'Protective Bond', 'Surefooted', 'Feral Connection'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Hunter’s Edge', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Animal Bond', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Experienced Trapper', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Pack Hunting', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Deadly Trap', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Protective Bond', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Surefooted', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Feral Connection', 'tier': 4}
                ]
            }
        }
    },
    'leader': {
        'name': 'Leader',
        'icon': '⚔️',
        'desc': 'Battlefield commanders, stalwart champions, and cunning politicos.',
        'starting_skill': 'Leadership',
        'key_name': 'Decisive Command (Leader Key)',
        'key_page': 103,
        'pages_desc': [106, 107, 108, 109],
        'pages_tree': [104, 105],
        'specialties': {
            'Champion': {
                'desc': 'Inspiring frontline warriors who draw enemy attention and shield their comrades.',
                'order': ['Valiant Intervention', 'Demonstrative Command', 'Hardy', 'Combat Coordination', 'Resolute Stand', 'Imposing Posture', 'Resilient Hero', 'Mighty'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Valiant Intervention', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Demonstrative Command', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Hardy', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Combat Coordination', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Resolute Stand', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Imposing Posture', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Resilient Hero', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Mighty', 'tier': 4}
                ]
            },
            'Officer': {
                'desc': 'Tactical commanders who maintain unit cohesion and direct synchronized maneuvers.',
                'order': ['Through the Fray', 'Composed', 'Customary Garb', 'Well Supplied', 'Confident Command', 'Authority', 'Relentless March', 'Synchronized Assault'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Through the Fray', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Composed', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Customary Garb', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Well Supplied', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Confident Command', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Authority', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Relentless March', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Synchronized Assault', 'tier': 4}
                ]
            },
            'Politico': {
                'desc': 'Machiavellian schemers who use rumormongering and cutthroat ploys.',
                'order': ['Cutthroat Tactics', 'Tactical Ploy', 'Rumormonger', 'Well Dressed', 'Baleful', 'Shrewd Command', 'Set at Odds', 'Grand Deception'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Cutthroat Tactics', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Tactical Ploy', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Rumormonger', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Well Dressed', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Baleful', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Shrewd Command', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Set at Odds', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Grand Deception', 'tier': 4}
                ]
            }
        }
    },
    'scholar': {
        'name': 'Scholar',
        'icon': '📖',
        'desc': 'Artifabrians who engineer technology, strategists who plan victories, and surgeons who mend wounds.',
        'starting_skill': 'Lore',
        'key_name': 'Erudition (Scholar Key)',
        'key_page': 112,
        'pages_desc': [112, 113, 116, 117],
        'pages_tree': [114, 115],
        'specialties': {
            'Artifabrian': {
                'desc': 'Inventors and jewelers who build, modify, and overcharge magical fabrials.',
                'order': ['Efficient Engineer', 'Prized Acquisition', 'Fine Handiwork', 'Inventive Design', 'Deep Study', 'Overcharge', 'Experimental Tinkering', 'Overwhelm With Detail'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Efficient Engineer', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Prized Acquisition', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Fine Handiwork', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Inventive Design', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Deep Study', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Overcharge', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Experimental Tinkering', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Overwhelm With Detail', 'tier': 4}
                ]
            },
            'Strategist': {
                'desc': 'Masterminds who predict outcomes, contingency-plan, and identify crucial turning points.',
                'order': ['Strategize', 'Mind and Body', 'Composed', 'Know Your Moment', 'Deep Contemplation', 'Contingency', 'Keen Insight', 'Turning Point'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Strategize', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Mind and Body', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Composed', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Know Your Moment', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Deep Contemplation', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Contingency', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Keen Insight', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Turning Point', 'tier': 4}
                ]
            },
            'Surgeon': {
                'desc': 'Physicians and medics who diagnose ailments, treat trauma, and revive the fallen.',
                'order': ['Field Medicine', 'Emotional Intelligence', 'Anatomical Insight', 'Collected', 'Swift Healer', 'Applied Medicine', 'Ongoing Care', 'Resuscitation'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Field Medicine', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Emotional Intelligence', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Anatomical Insight', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Collected', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Swift Healer', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Applied Medicine', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Ongoing Care', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Resuscitation', 'tier': 4}
                ]
            }
        }
    },
    'warrior': {
        'name': 'Warrior',
        'icon': '🛡️',
        'desc': 'Disciplined soldiers, master duelists, and elite Shardbearers.',
        'starting_skill': 'Athletics',
        'key_name': 'Vigilant Stance (Warrior Key)',
        'key_page': 119,
        'pages_desc': [122, 123, 124, 125, 126],
        'pages_tree': [120, 121],
        'specialties': {
            'Duelist': {
                'desc': 'Nimble fighters specializing in 1-on-1 martial forms, katas, and signature weapons.',
                'order': ['Practiced Kata', 'Flamestance', 'Ironstance', 'Signature Weapon', 'Surefooted', 'Feinting Strike', 'Vinestance', 'Wit’s End'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Practiced Kata', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Flamestance', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Ironstance', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Signature Weapon', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Surefooted', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Feinting Strike', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Vinestance', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Wit’s End', 'tier': 4}
                ]
            },
            'Shardbearer': {
                'desc': 'Warriors attuned to Shardblades and Shardplate, dealing cataclysmic strikes.',
                'order': ['Stonestance', 'Shard Training', 'Mighty', 'Windstance', 'Bloodstance', 'Shattering Blow', 'Meteoric Leap', 'Precise Parry'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Stonestance', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Shard Training', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Mighty', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Windstance', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Bloodstance', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Shattering Blow', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Meteoric Leap', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Precise Parry', 'tier': 4}
                ]
            },
            'Soldier': {
                'desc': 'Line infantry veterans trained in formations, defensive fortifications, and gritty endurance.',
                'order': ['Cautious Advance', 'Combat Training', 'Defensive Position', 'Hardy', 'Formation Drills', 'Swift Strikes', 'Wary', 'Devastating Blow'],
                'grid': [
                    {'col': 0, 'row': 0, 'name': 'Cautious Advance', 'tier': 1},
                    {'col': 1, 'row': 0, 'name': 'Combat Training', 'tier': 1},
                    {'col': 0, 'row': 1, 'name': 'Defensive Position', 'tier': 2},
                    {'col': 1, 'row': 1, 'name': 'Hardy', 'tier': 2},
                    {'col': 0, 'row': 2, 'name': 'Formation Drills', 'tier': 3},
                    {'col': 1, 'row': 2, 'name': 'Swift Strikes', 'tier': 3},
                    {'col': 0, 'row': 3, 'name': 'Wary', 'tier': 4},
                    {'col': 1, 'row': 3, 'name': 'Devastating Blow', 'tier': 4}
                ]
            }
        }
    }
}

# EXTRACT ALL HEROIC TALENT DESCRIPTIONS
def extract_all_heroic():
    db = {}
    for pkey, pcfg in HEROIC_PATHS.items():
        print(f"Parsing {pcfg['name']}...")
        
        # 1. Parse Key Talent
        ktxt = doc[pcfg['key_page'] - 1].get_text()
        kname = pcfg['key_name']
        idx = ktxt.find(kname)
        kdesc = ""
        if idx != -1:
            chunk = ktxt[idx:]
            lines = [l.strip() for l in chunk.split('\n') if l.strip()]
            desc_lines = []
            started = False
            for l in lines[1:]:
                if l.startswith('Activation:'):
                    started = True
                    continue
                elif started:
                    if any(w in l for w in ['Ethan El Bard', 'Chapter 4', 'Specialty', 'Key Talent', 'Starting Skill']):
                        break
                    desc_lines.append(l)
            kdesc = clean_str(' '.join(desc_lines))
        
        short_kname = kname.split('(')[0].strip()
        key_talent_obj = {
            'id': f"{pkey}-key",
            'name': short_kname,
            'fullName': kname,
            'isKey': True,
            'path': pcfg['name'],
            'specialty': 'Key Talent',
            'tier': 0,
            'prereq': 'None (Path Starting Talent)',
            'activation': 'Passive / Special',
            'focusCost': parse_focus_cost(kdesc),
            'investitureCost': 0,
            'shortDesc': clean_str(kdesc.split('.')[0] + '.') if '.' in kdesc else kdesc[:100],
            'description': kdesc
        }
        
        # 2. Parse Specialty Talents
        specialties_data = []
        
        for spec_name, spec_cfg in pcfg['specialties'].items():
            spec_talents = []
            for tgrid in spec_cfg['grid']:
                tname = tgrid['name']
                # Search for talent in description pages
                found_desc = ""
                found_prereq = "None"
                
                for pno in pcfg['pages_desc']:
                    txt = doc[pno - 1].get_text()
                    pattern = re.escape(tname) + r'\s*\n\s*Prerequisite:(.*?)\n\s*Activation:\s*(.*?)(?=\n[A-Z][A-Za-z ’\'-]{2,30}\n\s*Prerequisite:|\n[A-Z][A-Za-z ]+ Specialty|\n[A-Z][A-Za-z ]+ Talents|\nEthan El Bard|\Z)'
                    m = re.search(pattern, txt, re.DOTALL)
                    if m:
                        found_prereq = clean_str(m.group(1))
                        found_desc = clean_str(m.group(2))
                        break
                        
                act = parse_activation(found_desc, found_prereq, tname)
                fcost = parse_focus_cost(found_desc)
                icost = parse_investiture_cost(found_desc)
                
                # Derive parent prerequisite IDs
                parent_ids = []
                if tgrid['tier'] == 1:
                    parent_ids.append(f"{pkey}-key")
                else:
                    # Look for other talents mentioned in prereq
                    for other_tgrid in spec_cfg['grid']:
                        if other_tgrid['name'] != tname and other_tgrid['name'].lower() in found_prereq.lower():
                            parent_ids.append(f"{pkey}-{make_id(spec_name)}-{make_id(other_tgrid['name'])}")
                
                spec_talents.append({
                    'id': f"{pkey}-{make_id(spec_name)}-{make_id(tname)}",
                    'name': tname,
                    'isKey': False,
                    'path': pcfg['name'],
                    'specialty': spec_name,
                    'tier': tgrid['tier'],
                    'col': tgrid['col'],
                    'row': tgrid['row'],
                    'prereq': found_prereq,
                    'prereqIds': parent_ids,
                    'activation': act,
                    'focusCost': fcost,
                    'investitureCost': icost,
                    'shortDesc': clean_str(found_desc.split('.')[0] + '.') if '.' in found_desc else found_desc[:100],
                    'description': found_desc
                })
            
            specialties_data.append({
                'name': spec_name,
                'description': spec_cfg['desc'],
                'talents': spec_talents
            })
            
        db[pkey] = {
            'id': pkey,
            'name': pcfg['name'],
            'icon': pcfg['icon'],
            'description': pcfg['desc'],
            'startingSkill': pcfg['starting_skill'],
            'keyTalent': key_talent_obj,
            'specialties': specialties_data
        }
    return db

# EXTRACT ALL SURGE TALENTS
SURGE_CONFIGS = [
    ('abrasion', 'Abrasion', 'Speed', [216, 217, 218], 'Alters friction, allowing you to slide with ease or make surfaces completely frictionless.'),
    ('adhesion', 'Adhesion', 'Presence', [219, 220, 221], 'Binds objects and creatures together with incredible, unbreakable Invested force.'),
    ('cohesion', 'Cohesion', 'Willpower', [221, 222, 223, 224], 'Alters the strong axial forces of matter, shaping and molding solid stone as if it were soft clay.'),
    ('division', 'Division', 'Strength', [224, 225, 226], 'Decays and destroys physical matter, setting fires and combusting materials with devastating power.'),
    ('gravitation', 'Gravitation', 'Awareness', [227, 228, 229], 'Changes the direction and magnitude of gravitational attraction, enabling flight and gravitational slams.'),
    ('illumination', 'Illumination', 'Intellect', [230, 231, 232], 'Creates auditory and visual illusions, weaving light and sound to deceive senses.'),
    ('progression', 'Progression', 'Willpower', [233, 234, 235], 'Accelerates organic growth and healing, rapidly mending severe wounds and restoring life.'),
    ('tension', 'Tension', 'Strength', [235, 236, 237], 'Alters the stiffness of flexible materials, turning cloth as hard as steel or shaping garments into shields.'),
    ('transformation', 'Transformation', 'Intellect', [238, 239, 240], 'Soulcasts inanimate substances, transforming one essence into another such as stone to food or blood to fire.'),
    ('transportation', 'Transportation', 'Awareness', [241, 242, 243, 244], 'Enables transition between the Physical and Cognitive Realms, phasing and Elsecalling across space.')
]

def extract_all_surges():
    surges_db = {}
    for skey, sname, attr, pages, sdesc in SURGE_CONFIGS:
        print(f"Parsing Surge: {sname}...")
        talents = []
        for pno in pages:
            txt = doc[pno - 1].get_text()
            d = doc[pno - 1].get_text('dict')
            for b in d['blocks']:
                if 'lines' not in b: continue
                lines = b['lines']
                for i, l in enumerate(lines):
                    spans = l['spans']
                    if len(spans) == 1 and 12.0 <= spans[0]['size'] <= 15.5:
                        tname = spans[0]['text'].strip()
                        # check prereq
                        has_prereq = False
                        prereq_text = "None"
                        j = i + 1
                        while j < min(i + 4, len(lines)):
                            next_line = ' '.join(s['text'].strip() for s in lines[j]['spans']).strip()
                            if next_line.startswith('Prerequisite:'):
                                has_prereq = True
                                prereq_text = next_line.replace('Prerequisite:', '').strip()
                                break
                            j += 1
                        if has_prereq and not any(k in tname for k in ['Chapter', 'Surges', 'Surge', 'Ethan']):
                            # Extract description
                            pattern = re.escape(tname) + r'\s*\n\s*Prerequisite:(.*?)\n\s*Activation:\s*(.*?)(?=\n[A-Z][A-Za-z ’\'-]{2,30}\n\s*Prerequisite:|\n[A-Z][A-Za-z ]+ Talents|\nEthan El Bard|\Z)'
                            m = re.search(pattern, txt, re.DOTALL)
                            tdesc = clean_str(m.group(2)) if m else ""
                            
                            act = parse_activation(tdesc, prereq_text, tname)
                            fcost = parse_focus_cost(tdesc)
                            icost = parse_investiture_cost(tdesc)
                            
                            # Determine tier from prereq or level
                            tier = 1
                            if 'level 13+' in prereq_text.lower() or 'third ideal' in prereq_text.lower():
                                tier = 4
                            elif 'level 8+' in prereq_text.lower() or 'second ideal' in prereq_text.lower() or '3+' in prereq_text:
                                tier = 3
                            elif 'level 4+' in prereq_text.lower() or 'first ideal' in prereq_text.lower() or '2+' in prereq_text or 'talent' in prereq_text.lower():
                                tier = 2
                                
                            talents.append({
                                'id': f"{skey}-{make_id(tname)}",
                                'name': tname,
                                'surge': sname,
                                'tier': tier,
                                'prereq': clean_str(prereq_text),
                                'activation': act,
                                'focusCost': fcost,
                                'investitureCost': icost,
                                'shortDesc': clean_str(tdesc.split('.')[0] + '.') if '.' in tdesc else tdesc[:100],
                                'description': tdesc
                            })
        surges_db[skey] = {
            'id': skey,
            'name': sname,
            'attribute': attr,
            'description': sdesc,
            'talents': talents
        }
    return surges_db

# EXTRACT ALL RADIANT ORDERS
RADIANT_CONFIGS = [
    ('windrunner', 'Windrunner', ['Adhesion', 'Gravitation'], 'Honorspren', 'I will protect those who cannot protect themselves.', 202, [206, 207], 208),
    ('skybreaker', 'Skybreaker', ['Gravitation', 'Division'], 'Highspren', 'I will put the law before all else.', 168, [172, 173], 174),
    ('dustbringer', 'Dustbringer', ['Division', 'Abrasion'], 'Ashspren', 'I will seek self-mastery.', 136, [140, 141], 142),
    ('edgedancer', 'Edgedancer', ['Abrasion', 'Progression'], 'Cultivationspren', 'I will remember those who have been forgotten.', 144, [148, 149], 150),
    ('truthwatcher', 'Truthwatcher', ['Progression', 'Illumination'], 'Mistspren', 'I will seek truth and share it.', 184, [188, 189], 190),
    ('lightweaver', 'Lightweaver', ['Illumination', 'Transformation'], 'Cryptics (Liespren)', 'I will speak my truth.', 160, [164, 165], 166),
    ('elsecaller', 'Elsecaller', ['Transformation', 'Transportation'], 'Inkspren', 'I will reach my potential.', 152, [156, 157], 158),
    ('willshaper', 'Willshaper', ['Transportation', 'Cohesion'], 'Lightspren (Reachers)', 'I will seek freedom for all.', 194, [198, 199], 200),
    ('stoneward', 'Stoneward', ['Cohesion', 'Tension'], 'Peakspren', 'I will be there when I am needed.', 176, [180, 181], 182),
    ('bondsmith', 'Bondsmith', ['Tension', 'Adhesion'], 'Godspren (Stormfather, Nightwatcher, Sibling)', 'I will unite instead of divide.', 210, [210, 211], 212)
]

def extract_all_radiant():
    radiant_db = {}
    for okey, oname, surges, spren, ideal, p_start, p_trees, p_desc in RADIANT_CONFIGS:
        print(f"Parsing Radiant Order: {oname}...")
        talents = []
        if p_desc < 210: # Standard orders with talent pages
            txt = doc[p_desc - 1].get_text()
            d = doc[p_desc - 1].get_text('dict')
            for b in d['blocks']:
                if 'lines' not in b: continue
                lines = b['lines']
                for i, l in enumerate(lines):
                    spans = l['spans']
                    if len(spans) == 1 and 12.0 <= spans[0]['size'] <= 15.5:
                        tname = spans[0]['text'].strip()
                        has_prereq = False
                        prereq_text = "None"
                        j = i + 1
                        while j < min(i + 4, len(lines)):
                            next_line = ' '.join(s['text'].strip() for s in lines[j]['spans']).strip()
                            if next_line.startswith('Prerequisite:'):
                                has_prereq = True
                                prereq_text = next_line.replace('Prerequisite:', '').strip()
                                break
                            j += 1
                        if has_prereq and not any(k in tname for k in ['Chapter', 'Radiant', 'Ethan']):
                            pattern = re.escape(tname) + r'\s*\n\s*Prerequisite:(.*?)\n\s*Activation:\s*(.*?)(?=\n[A-Z][A-Za-z ’\'-]{2,30}\n\s*Prerequisite:|\n[A-Z][A-Za-z ]+ Talents|\nEthan El Bard|\Z)'
                            m = re.search(pattern, txt, re.DOTALL)
                            tdesc = clean_str(m.group(2)) if m else ""
                            
                            act = parse_activation(tdesc, prereq_text, tname)
                            fcost = parse_focus_cost(tdesc)
                            icost = parse_investiture_cost(tdesc)
                            
                            talents.append({
                                'id': f"{okey}-{make_id(tname)}",
                                'name': tname,
                                'order': oname,
                                'prereq': clean_str(prereq_text),
                                'activation': act,
                                'focusCost': fcost,
                                'investitureCost': icost,
                                'shortDesc': clean_str(tdesc.split('.')[0] + '.') if '.' in tdesc else tdesc[:100],
                                'description': tdesc
                            })
        radiant_db[okey] = {
            'id': okey,
            'name': oname,
            'surges': surges,
            'spren': spren,
            'firstIdeal': ideal,
            'talents': talents
        }
    return radiant_db

heroic = extract_all_heroic()
surges = extract_all_surges()
radiant = extract_all_radiant()

full_db = {
    'version': '1.0.0',
    'source': 'Stormlight Handbook (Official Rules)',
    'heroic_paths': heroic,
    'surges': surges,
    'radiant_orders': radiant
}

with open('rulebook_talents.json', 'w') as f:
    json.dump(full_db, f, indent=2)

print("\nSUCCESS: Successfully wrote rulebook_talents.json!")
print(f"Heroic Paths: {len(heroic)} (Total talents: {sum(1 + sum(len(s['talents']) for s in p['specialties']) for p in heroic.values())})")
print(f"Surges: {len(surges)} (Total talents: {sum(len(s['talents']) for s in surges.values())})")
print(f"Radiant Orders: {len(radiant)} (Total talents: {sum(len(o['talents']) for o in radiant.values())})")
