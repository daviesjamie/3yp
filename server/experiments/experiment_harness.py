from __future__ import division
from spout.sources import JSONInputStream
from classifier import Classifier, TrainOperation
from tokeniser import TokeniseTweetFunction
import json
import os
import sys


class Test:
    def __init__(self, use_hashtag_text, use_stop_words, disallow_urls, disallow_punctuation, disallow_usernames):
        self.use_hashtag_text = use_hashtag_text
        self.use_stop_words = use_stop_words
        self.disallow_urls = disallow_urls
        self.disallow_punctuation = disallow_punctuation
        self.disallow_usernames = disallow_usernames

    def __str__(self):
        string = '+hashtag_text ' if self.use_hashtag_text else '-hashtag_text '
        string += '+stop_words ' if self.use_stop_words else '-stop_words '
        string += '+urls ' if self.disallow_urls else '-urls '
        string += '+punctuation ' if self.disallow_punctuation else '-punctuation '
        string += '+usernames' if self.disallow_usernames else '-usernames'
        return string


def run_tests(output_file='test_results.txt', training_set_file='training_set.json', test_set_file='test_set.json'):
    print "Training from {}".format(training_set_file)
    print "Using {} as test data".format(test_set_file)
    print "Outputting to {}".format(output_file)

    print "Initialising output file..."
    if os.path.isfile(output_file):
        sys.exit("The output file {} already exists!".format(output_file))

    with open(output_file, 'w') as output:
        output.write('test parameters,')
        output.write('percent_1,')
        output.write('percent_5,')
        output.write('percent_10,')
        output.write('percent_15,')
        output.write('percent_20,')
        output.write('percent_30,')
        output.write('percent_50,')
        output.write('percent_all_5,')
        output.write('percent_all_10,')
        output.write('percent_all_15,')
        output.write('percent_all_20,')
        output.write('percent_all_30,')
        output.write('percent_all_50,')
        output.write('correct_1,')
        output.write('correct_5,')
        output.write('correct_10,')
        output.write('correct_15,')
        output.write('correct_20,')
        output.write('correct_30,')
        output.write('correct_50,')
        output.write('all_correct_5,')
        output.write('all_correct_10,')
        output.write('all_correct_15,')
        output.write('all_correct_20,')
        output.write('all_correct_30,')
        output.write('all_correct_50,')
        output.write('count\n')

    print "Initialising tests..."

    tests = []
    tests.append(Test(False, False, False, False, False))
    tests.append(Test(True, False, False, False, False))
    tests.append(Test(False, True, False, False, False))
    tests.append(Test(False, False, True, False, False))
    tests.append(Test(False, False, False, True, False))
    tests.append(Test(False, False, False, False, True))
    tests.append(Test(True, True, True, True, True))
    tests.append(Test(True, True, False, False, False))
    tests.append(Test(False,True,False,True,False))

    for test in tests:
        print "Running test {0}/{1}".format(tests.index(test) + 1, len(tests))
        print "\t" + test.__str__()

        classifier = Classifier(use_hashtag_text=test.use_hashtag_text)

        print "\tTraining classifier..."

        training_set = JSONInputStream(training_set_file)
        training_set \
            .map(TokeniseTweetFunction(stop_tokens=test.use_stop_words,
                                       punctuation=test.disallow_punctuation,
                                       usernames=test.disallow_usernames,
                                       urls=test.disallow_urls)) \
            .for_each(TrainOperation(classifier))

        print "\tClassifying test set..."

        count = 0
        correct_1 = 0
        correct_5 = 0
        correct_10 = 0
        correct_15 = 0
        correct_20 = 0
        correct_30 = 0
        correct_50 = 0
        all_correct_5 = 0
        all_correct_10 = 0
        all_correct_15 = 0
        all_correct_20 = 0
        all_correct_30 = 0
        all_correct_50 = 0

        with open(test_set_file, 'r') as test_set:
            for line in test_set:
                if count % 10 == 0: print '\t{}'.format(count)

                tweet = json.loads(line)

                guesses = [g[0] for g in classifier.classify(tweet['text'], results=50)]
                actuals = [h['text'].lower() for h in tweet['entities']['hashtags']]

                if guesses[0] in actuals:
                    correct_1 += 1

                temp_5 = 0
                temp_10 = 0
                temp_15 = 0
                temp_20 = 0
                temp_30 = 0
                temp_50 = 0

                for actual in actuals:
                    if actual in guesses[:5]:
                        temp_5 += 1
                    if actual in guesses[:10]:
                        temp_10 += 1
                    if actual in guesses[:15]:
                        temp_15 += 1
                    if actual in guesses[:20]:
                        temp_20 += 1
                    if actual in guesses[:30]:
                        temp_30 += 1
                    if actual in guesses[:50]:
                        temp_50 += 1

                if temp_5 > 0:
                    correct_5 += 1
                if temp_10 > 0:
                    correct_10 += 1
                if temp_15 > 0:
                    correct_15 += 1
                if temp_20 > 0:
                    correct_20 += 1
                if temp_30 > 0:
                    correct_30 += 1
                if temp_50 > 0:
                    correct_50 += 1

                all_len = len(actuals)

                if temp_5 == all_len:
                    all_correct_5 += 1
                if temp_10 == all_len:
                    all_correct_10 += 1
                if temp_15 == all_len:
                    all_correct_15 += 1
                if temp_20 == all_len:
                    all_correct_20 += 1
                if temp_30 == all_len:
                    all_correct_30 += 1
                if temp_50 == all_len:
                    all_correct_50 += 1

                count += 1

        print "\tWriting statistics to output file..."

        percent_1 = (correct_1 / count) * 100
        percent_5 = (correct_5 / count) * 100
        percent_10 = (correct_10 / count) * 100
        percent_15 = (correct_15 / count) * 100
        percent_20 = (correct_20 / count) * 100
        percent_30 = (correct_30 / count) * 100
        percent_50 = (correct_50 / count) * 100
        percent_all_5 = (all_correct_5 / count) * 100
        percent_all_10 = (all_correct_10 / count) * 100
        percent_all_15 = (all_correct_15 / count) * 100
        percent_all_20 = (all_correct_20 / count) * 100
        percent_all_30 = (all_correct_30 / count) * 100
        percent_all_50 = (all_correct_50 / count) * 100

        with open(output_file, 'a') as output:
            output.write(test.__str__() + ',')
            output.write(str(percent_1) + ',')
            output.write(str(percent_5) + ',')
            output.write(str(percent_10) + ',')
            output.write(str(percent_15) + ',')
            output.write(str(percent_20) + ',')
            output.write(str(percent_30) + ',')
            output.write(str(percent_50) + ',')
            output.write(str(percent_all_5) + ',')
            output.write(str(percent_all_10) + ',')
            output.write(str(percent_all_15) + ',')
            output.write(str(percent_all_20) + ',')
            output.write(str(percent_all_30) + ',')
            output.write(str(percent_all_50) + ',')
            output.write(str(correct_1) + ',')
            output.write(str(correct_5) + ',')
            output.write(str(correct_10) + ',')
            output.write(str(correct_15) + ',')
            output.write(str(correct_20) + ',')
            output.write(str(correct_30) + ',')
            output.write(str(correct_50) + ',')
            output.write(str(all_correct_5) + ',')
            output.write(str(all_correct_10) + ',')
            output.write(str(all_correct_15) + ',')
            output.write(str(all_correct_20) + ',')
            output.write(str(all_correct_30) + ',')
            output.write(str(all_correct_50) + ',')
            output.write(str(count) + '\n')

        print "\tDone!"

    print "Tests complete!"


if __name__ == '__main__':
    run_tests(sys.argv[1], sys.argv[2], sys.argv[3])

