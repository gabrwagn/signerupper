
# Formats
TIME_FORMAT = '%H:%M'
DATE_FORMAT = '%Y-%m-%d'
DATE_TIME_FORMAT = f'{DATE_FORMAT} {TIME_FORMAT}'
PARTICIPANT_MAX_NAME_LENGTH = 11

# Announcement
ANNOUNCEMENT_CHANNEL_NAME = "Announcements"


class MESSAGE:
    NEW_EVENT = "New raid event: {} at {} {}, go sign up now in {}!"
    REMINDER = "Hey! Dont for get you signed up for {} {} {}!"
    PLACEMENT = "Hey! You've been assigned {} in the raid {} at {} (see: {})!"


# Event settings
DEFAULT_CAP_PARTICIPANTS = 40
SIGNUP_REACTION = '👍'
DECLINE_REACTION = '👎'
INSTRUCTIONS = f"*Write the command **+sign** or {SIGNUP_REACTION} to attend, " \
               f"write **+decline** or {DECLINE_REACTION} if you can't attend.*"


# Roles
class ROLES:
    # Required
    ADMIN = "Officer"
    DECLINED = "Declined"
    BACKUP = "Backup"

    # Server specific
    TANK = "Tank"
    PHYSICAL = "Physical"
    CASTER = "Caster"
    HEALER = "Healer"

    ALL = [
        TANK,
        PHYSICAL,
        CASTER,
        HEALER,
        DECLINED,
        BACKUP
    ]

    ACTIVE = [
        TANK,
        PHYSICAL,
        CASTER,
        HEALER,
    ]

    @classmethod
    def from_identifier_default(cls, identifier):
        return {
            "Warrior": ROLES.TANK,
            "Rogue": ROLES.PHYSICAL,
            "Hunter": ROLES.PHYSICAL,
            "Paladin": ROLES.HEALER,
            "Shaman": ROLES.HEALER,
            "Priest": ROLES.HEALER,
            "Druid": ROLES.HEALER,
            "Warlock": ROLES.CASTER,
            "Mage": ROLES.CASTER,
        }[identifier]


# Identifiers
IDENTIFIERS = [
    "Warrior",
    "Rogue",
    "Hunter",
    "Paladin",
    "Shaman",
    "Priest",
    "Warlock",
    "Mage",
    "Druid",
]
VALID_USER_ROLES = IDENTIFIERS
