News Crawler
===================


Webcrawler for feeding news from g1.com.br/politica and do some articles' similarity to see what articles are related. From 30 to 30 minutes it tries to read new articles from g1.com.br/politica and check its similarity with previous articles. Then, every 8 hours it retrains the Latent Semantic Indexing (LSI) with new articles.

----------


How It Works
-------------

Two schedulers are set: job_get_news (triggered every 30 minutes) and job_train_nlp (triggered every 8 hours).
The first one runs a Scrapy Spider to read http://g1.globo.com/politica/, loop through each article following their link and storing its content (text, title, abstract and published date). Then it runs a Natural Language Processing (NLP) script to get the articles' similarity with previous read articles. This is done using *Bag of Words* and *Latent Semantic Indexing (LSI)*.At last, it copies the new articles to the trained ones.
The second one trains the LSI with the new articles. First the text are cleaned from ordinary portuguese words like 'o, a, em, no, nos, nas' etc. and discarts words that appear just once. From there the text is vectorised using Bag of Words which holds the word and how many times it appears in the document. With the Bag of Words done, it's time to tokenize and create a corpus, creating a unique number for each word and holding the occurrence. Applying term *Frequency–Inverse Document Frequency (TF-IDF)* transforms the data to be more compact real valued weights. To extract semantic information over the text Latent Semantic Indexing is applied over TF-IDF data which relates topics with words, gibing greater weiths for related words and less for other less important. With the computed Latent Semantic Indexing expressions the prediction is possible.



Setup
-------------

A few libraries are needed in this project:

 - [Scrapy][1]  conda install -c conda-forge scrapy or pip install Scrapy
 - [Gensim][2] pip install --upgrade gensim
 - [Schedule][3] pip install schedule


Usage
------------

To use this project simply clone it to your workspace and run main.py.
```
>>> python main.py
>>> python main.py -h # For help
```
However there a a few properties you may change using command line:
:	**n_topic** The approximate number of different topics the articles are referring to. *default=5*
:	**pdepth** Number of pages to follow (not number of articles). *default=5*
:	**train_file** File to hold previous articles. *default=text.jl*
:	**predict_file** File to hold new articles to be predicted and applied similarity with those from train_file. *default=predict.jl*



License
------------
Distributed under the MIT license. See LICENSE.txt for more information.

  [1]: https://doc.scrapy.org/en/latest/intro/tutorial.html#using-spider-arguments
  [2]: https://radimrehurek.com/gensim/
  [3]: https://github.com/dbader/schedule
