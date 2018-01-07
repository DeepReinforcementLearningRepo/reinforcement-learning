#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""--------------------------------------------------------------------
NORMAL DISTRIBUTIONS
Started on the 2018/01/03
theo.alves.da.costa@gmail.com
https://github.com/theolvs
------------------------------------------------------------------------
"""

from scipy import stats
import seaborn as sns
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import time
from tqdm import tqdm



class Dist(object):
    def __init__(self,mu = None,std = None,label = None):
        self.mu = np.random.rand()*20 - 10 if mu is None else mu
        self.std = np.random.rand()*10 if std is None else std
        self.label = "" if not label else " - "+label
        self.func = lambda x : stats.norm.cdf(x,loc = self.mu,scale = self.std)
        
    def __repr__(self,markdown = False):
        return "Norm {1}mu={2}{0}, {0}std={3}{0}{4}".format("$" if markdown else "","$\\" if markdown else "",
                                                             round(self.mu,2),round(self.std,2),self.label)
        
    def plot(self,fill = True):
        x = np.linspace(-20, 20, 100)
        y = stats.norm.pdf(x,loc = self.mu,scale = self.std)
        plt.plot(x,y,label = self.__repr__(markdown = True))
        if fill:
            plt.fill_between(x, 0, y, alpha=0.4)
        
        
    def __add__(self,other):
        mu = np.mean([self.mu,other.mu])
        std = np.mean([self.std,other.std])
        return Dist(mu,std)
    
    def mutate(self,alpha = 1):
        self.mu = self.mu + 1/(1+np.log(1+alpha)) * np.random.randn()
        self.std = max(self.std + 1/(1+np.log(1+alpha)) * np.random.randn(),0.5)
        
    def fitness(self,x):
        return 1 - stats.kstest(x,self.func).statistic










class Population(object):
    def __init__(self,distributions = None,n = 100):
        if distributions is not None:
            self.distributions = distributions
        else:
            self.distributions = [Dist() for i in range(n)]
            
    def __getitem__(self,key):
        if type(key) == tuple or type(key) == list:
            d = []
            for i in key:
                d.append(self.distributions[i])
            return d
        else:
            return self.distributions[key]
    
    def __iter__(self):
        return iter(self.distributions)
    
    def __len__(self):
        return len(self.distributions)
    
    def plot(self,title = "Normal distributions",figsize = None):
        if figsize:
            plt.figure(figsize = figsize)
        plt.title(title)
        fill = len(self) < 5
        for d in self:
            d.plot(fill = fill)
        plt.legend()
        plt.xlabel("x")
        plt.show()
    
    def evaluate(self,x):
        fitnesses = [(i,dist.fitness(x)) for i,dist in enumerate(self)]
        indices,fitnesses = zip(*sorted(fitnesses,key = lambda x : x[1],reverse = True))
        return indices,fitnesses
    
    def selection(self,x,top = 0.1):
        indices,fitnesses = self.evaluate(x)
        n = int(top*len(fitnesses))
        return indices[:n]
    
    
    def crossover(self,indices):
        combinations = list(itertools.combinations(indices,2))
        np.random.shuffle(combinations)
        combinations = combinations[:len(self)]
        new_population = []
        for i,j in combinations:
            new_population.append(self[i]+self[j])
        self.distributions = new_population
            
    def mutate(self,generation = 1):
        for d in self:
            d.mutate(generation)
            
            
    def evolve(self,x,top = 0.25,n_generations = 20,last_selection = True):
        all_fitnesses = [self.evaluate(x)[1]]

        for generation in tqdm(range(n_generations)):

            indices = self.selection(x,top)
            self.crossover(indices)
            self.mutate(generation)
            
            indices,fitnesses = self.evaluate(x)
            all_fitnesses.append(fitnesses)
            
        self._plot_fitnesses(all_fitnesses)
        
        if last_selection:
            indices = self.selection(x,top)
    
        return Population(self[indices])
    
    
    def _plot_fitnesses(self,fitnesses):
        sups = []
        infs = []
        means = []
        for step in fitnesses:
            sups.append(np.max(step))
            infs.append(np.min(step))
            means.append(np.mean(step))
            
        plt.figure(figsize=(10,6))
        plt.plot(means)
        plt.fill_between(range(len(means)),sups,infs, alpha = 0.2)
        plt.xlabel('# Generation')
        plt.ylabel('Fitness')
        plt.legend()
        plt.show()