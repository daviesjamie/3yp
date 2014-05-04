Twitter Hashtag Recommendation
==============================

This project presents an intelligent hashtag recommendation tool for use with
Twitter, that makes it easier for users to compose tweets with relevant
hashtags, as well as aiding the search and navigation of Twitter as a whole. It
integrates a Naive Bayes classifier with a novel stream processing framework to
give functional, non-personalised hashtag suggestions and search query
expansions.

A thorough and detailed explanation of this project can be read in the [final
report](https://github.com/daviesjamie/3yp/raw/master/deliverables/final/final.pdf).

The work contained within this repository has been submitted as the
3<sup>rd</sup> Year Project for the award of MEng Computer Science by Jamie
Davies ([jagd1g11@ecs.soton.ac.uk](mailto:jagd1g11@ecs.soton.ac.uk)).

## Architecture

The system is based on a client-server architecture. The main classification
system is encapsulated in the server, which is accessible through a RESTful API.
Client interfaces (including the demonstration one included within this
repository) can then use the features available through the classification
server as they see fit.

The RESTful API for the server is as follows:

 - `/api/classify` - `POST` <br />
   Classify a tweet to provide a list of hashtag suggestions.
    - `text` - The text of the tweet to classify
    - `results` - The number of classifications (recommendations) to provide
      (*optional*)<br />

 - `/api/status` - `GET` <br />
   Returns a JSON object with useful information and statistics about the
   server.

 - `/api/hashtags` - `GET` <br />
   Returns an ordered list of all hashtags and their counts.
    - `num` - The number of hashtags to return (*optional*)<br />

 - `/api/tokens` - `GET` <br />
   Returns an ordered list of all tokens and their counts.
    - `num` - The number of tokens to return (*optional*)

 - `/api/hashtag/<string:hashtag>` - `GET` <br />
   Returns an ordered list of all tokens and their counts that have been seen
   with the given hashtag.<br />
    - `num` - The number of tokens to return (*optional*)<br />

 - `/api/token/<string:token>` - `GET` <br />
   Returns an ordered list of all hashtags and their counts that have been seen
   with the given token.
    - `num` - The number of hashtags to return (*optional*)<br />


## Usage

The project uses the `pip` tool to manage Python dependencies, and
[Bower](http://bower.io/) to manage HTML/CSS/Javascript dependencies. Before the
project can be used, the dependencies must first be installed:

```
$ git clone https://github.com/daviesjamie/3yp hashtag_recommendation
$ cd hashtag_recommendation
$ pip install -r requirements.txt
$ cd client
$ bower install
```

Next, you need to register the application with Twitter to get the OAuth tokens
necessary to use data from the live Twitter stream. You can do this by going to
[https://apps.twitter.com/](https://apps.twitter.com/), and then entering the
information you are given into `oauth.json` files in both the client and server
directories.

The classification server can then be run through the `server.py` script inside
the server directory. If no arguments are supplied to the script, Tornado is
used to provide access to the WSGI application. If the `dev` argument is
supplied, then Flask is used to serve the application directly, which provides
much more verbose output.

By default, the server will serialise its state and write it out to a .pickle
file once every hour. A development server can be started from any .pickle file
by simply passing in the file as a second argument: `server.py dev
state.pickle`.

The client is a simple Django application that is provided only for
demonstration purposes. It can be run through the `server.py` script inside the
client directory.
