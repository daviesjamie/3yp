from structures import Predicate


class TruePredicate(Predicate):
    """
    Simple predicate that always returns True. Used for testing purposes only.
    """
    def test(self, obj):
        return True


class TweetsWithHashtagsPredicate(Predicate):
    """
    Filters tweets to only include those that contain hashtags.
    """
    def test(self, obj):
        return len(obj['entities']['hashtags']) > 0


class TweetsInEnglishPredicate(Predicate):
    """
    Filters tweets to only include those that are tagged as being in English.
    """
    def test(self, obj):
        return obj['lang'] == 'en'