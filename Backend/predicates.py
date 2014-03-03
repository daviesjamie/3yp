from structures import Predicate


class TweetsWithHashtagsPredicate(Predicate):
    def test(self, obj):
        return len(obj['entities']['hashtags']) > 0
