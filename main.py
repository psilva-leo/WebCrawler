import argparse
import schedule
import time
import nlp
import logging
import subprocess

def job_get_news():
    from twisted.internet import reactor
    print("Getting news from Globo Politica")
    logging.info('Getting news from Globo Politica')
    # There is a way to call scrapy crawller using python, however to call it in a loop is not working properly.
    # To solve it, I simply calling from terminal.
    subprocess.Popen("scrapy crawl news -o predict.jl -a train_file="+args.train_file + " -a pages_depth="+str(args.pages_depth),shell=True, stdout=subprocess.PIPE).stdout.read()
    nlp.predict(args.predict_file)
    update_train_file()

def job_train_nlp():
    print('Training NLP')
    logging.info('Training NLP')
    nlp.train(args.train_file, args.n_topics)

def update_train_file():
    # Copy new from predict file to train file
    with open(args.train_file, 'a') as f:
        content = open(args.predict_file, 'r')
        for line in content:
            f.write(line)
        f.close()
    f.close()

    # Clean predict file
    f = open(args.predict_file, 'w')
    f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--topics",
                  dest="n_topics",
                  default=5,
                  help="Number of topics.")
    parser.add_argument("--pdepth",
                  dest="pages_depth",
                  default=5,
                  help="Number of pages to follow (not number of articles).")
    parser.add_argument("--train_file",
                  dest="train_file",
                  default='text.jl',
                  help="Input file for training")
    parser.add_argument("--predict_file",
                  dest="predict_file",
                  default='predict.jl',
                  help="Input file for prediction")
    args = parser.parse_args()


logging.basicConfig(filename='news.log', level=logging.INFO, format='%(asctime)s:%(name)s:%(message)s')
schedule.every(30).minutes.do(job_get_news)
schedule.every(8).hours.do(job_train_nlp)

while True:
    schedule.run_pending()
    time.sleep(1)