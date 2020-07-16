from datetime import timedelta
from time import sleep
import subprocess
import os

import luigi
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from scrapy.crawler import CrawlerProcess

from scraper import FortniteStatsSpider


plt.style.use('seaborn')


class FetchData(luigi.Task):
    date = luigi.DateParameter()

    def output(self):
        return luigi.LocalTarget(
            path='./logs/fetch-{:%Y-%m-%d}.txt'.format(self.date)
        )

    def run(self):
        print('Fetching data from https://fortnitestats.com/')
        process = CrawlerProcess()
        process.crawl(FortniteStatsSpider, filename='data.txt')
        process.start()
        self.output().makedirs()
        self.output().open('w').close()


class TransformData(luigi.Task):
    date = luigi.DateParameter()

    def requires(self):
        return FetchData(date=self.date)

    def output(self):
        return luigi.LocalTarget(
            path='./logs/transform-{:%Y-%m-%d}.txt'.format(self.date)
        )

    def run(self):
        df = pd.read_csv('data.txt')

        scalers = []
        columns = ['K/D', 'WR', 'Kills', 'Wins', 'Matches']

        for item in columns:
            scaler = StandardScaler()
            data = df[item].values.reshape(-1, 1)
            scaled_data = scaler.fit_transform(data)
            scalers.append(scaler)
            
            df[item + '_norm'] = scaled_data
        
        df.to_csv('data.txt')

        self.output().makedirs()
        self.output().open('w').close()


class PlotData(luigi.Task):
    date = luigi.DateParameter()

    def requires(self):
        return TransformData(date=self.date)

    def output(self):
        return luigi.LocalTarget(
            path='./logs/plot-{:%Y-%m-%d}.txt'.format(self.date)
        )

    def run(self):
        df = pd.read_csv('data.txt')

        x = df['Kills'].values
        y = df['Score'].values

        fig = plt.figure(figsize=(6, 4))

        plt.scatter(x, y)
        plt.xlabel('Kills')
        plt.ylabel('Score')
        plt.title('Kills vs. Score')
        plt.savefig('assets/kills_vs_score.png')

        self.output().makedirs()
        self.output().open('w').close()


class TrainModel(luigi.Task):
    date = luigi.DateParameter()

    def requires(self):
        # yield TransformData(date=self.date)
        yield PlotData(date=self.date)

    def output(self):
        return luigi.LocalTarget(
            path='./logs/train-{:%Y-%m-%d}.csv'.format(self.date)
        )

    def run(self):
        df = pd.read_csv('data.txt')

        x = df['Kills'].values
        y = df['Score'].values

        epochs = 500
        batch_size = 2
        lr = 1e-3
        opt = tf.keras.optimizers.Adam(lr=lr)

        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.Dense(1, input_shape=[1]))
        model.compile(loss='mean_squared_logarithmic_error', optimizer='adam')

        n = 5
        for i in range(n):
            print(f"[INFO] Training 500 epochs {i + 1}/{n}.")
            model.fit(x, y, epochs=500, batch_size=batch_size, verbose=False)

        layer = model.get_layer(index=0)
        weights = layer.get_weights()
        m, b = weights[0][0], weights[1]
        print(f"[INFO] Model parameters m={m}, b={b}")
        y_pred_model = model.predict(x)

        fig = plt.figure(figsize=(6, 4))
        plt.scatter(x, y, label='Original data')
        plt.plot(x, y_pred_model, label='Predicted with model', color='r')
        plt.xlabel('Kills')
        plt.ylabel('Score')
        plt.title('Kills vs. Score')
        plt.savefig('assets/trained_model.png')
        plt.legend()

        print("[INFO] Saving trained model...")
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        tflite_model = converter.convert()
        with tf.io.gfile.GFile('model.tflite', 'wb') as f:
            f.write(tflite_model)

        self.output().makedirs()
        self.output().open('w').close()