"""
    Tokenizer for tweets!  might be appropriate for other social media dialects too.
    general philosophy is to throw as little out as possible.
    development philosophy: every time you change a rule, do a diff of this
    program's output on ~100k tweets.  if you iterate through many possible rules
    and only accept the ones that seeem to result in good diffs, it's a sort of
    statistical learning with in-the-loop human evaluation :)
"""

__author__ = "Brendan O'Connor (anyall.org, brenocon@gmail.com)"
__version__ = "April 2009"