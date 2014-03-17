from spout.structs import Predicate


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